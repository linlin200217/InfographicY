from openai import OpenAI
import PyPDF2
from pydantic import BaseModel
from typing import List, Optional,Literal
import os
from dotenv import load_dotenv
import json

from util import rank_infographic
load_dotenv()



class RelatedSubtask(BaseModel):
    title: Optional[str]  # 相关子任务的标题
    relation: Optional[str]  # 叙述逻辑关系类型


class Subtask(BaseModel):
    subtask_title: str  # 子任务标题
    subtask_content: str  # 子任务相关内容
    subtask_relation: str  # 该子任务与问题的逻辑关系
    related_subtask: RelatedSubtask  # 相关的子任务


class TaskDecompositionOutput(BaseModel):
    subtasks: List[Subtask]  # 任务拆解后的子任务列表


class KnowledgeItem(BaseModel):
    knowledge_content: str
    data_insight: str
    first_level_highlight: str
    second_level_highlight: Optional[str]
    icon_keyword: str

class VisItem(BaseModel):
    key: str
    value: int|float

class Visualization(BaseModel):
    is_visualization: bool
    type: Literal['pie_chart','single_pie_chart','bar_chart','line_chart','pictographs'] | None
    data:list[VisItem]

class knowledgeItemViz(KnowledgeItem):
    visualization: Visualization

class KnowledgeResponse(BaseModel):
    knowledges: List[KnowledgeItem]

class ParserResultItem(Subtask):
    knowledges: List[knowledgeItemViz]

class ParserResult(BaseModel):
    title: str
    data: List[ParserResultItem]

class ColorScheme(BaseModel):
    theme_colors: List[List[int]]  # 3-5个RGB颜色列表
    background_color: List[int]  # 背景颜色
    first_level_color: List[int]  # 一级强调颜色
    first_level_font: str  # 一级强调字体
    second_level_color: List[int]  # 二级强调颜色
    second_level_font: str  # 二级强调字体
    text_color: List[int]  # 文本颜色
    text_font: str  # 文本字体

class PdfParser:
    def __init__(
        self, pdf_path: str, question: str, client: OpenAI, model: str = "gpt-4o-mini"
    ):
        self.pdf_path = pdf_path
        self.client = client
        self.model = model
        self.question = question
        self.pdf_text = self.pdf_to_text()

    def pdf_to_text(self):
       
        reader = PyPDF2.PdfReader(self.pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    @staticmethod
    def _read_prompt_from_md(md_path: str):
        with open(md_path, "r",encoding="utf-8") as file:
            prompt = file.read()
        return prompt

    def generate_title(self):
        system_prompt = self._read_prompt_from_md("prompts/generate_title.md")
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self.question},
            ],
        )

        Title = completion.choices[0].message.content
        return Title or "No title generated"

    def generate_subtasks(self) -> List[Subtask]:
        system_prompt = self._read_prompt_from_md("prompts/generate_subtasks.md")
        user_prompt = f"""
        Text: {self.pdf_text}
        Question: {self.question}
        """
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=TaskDecompositionOutput,
        )

        resp =  completion.choices[0].message.parsed
        if resp:
            return resp.subtasks
        return []

    def get_knowledges(self, subtask: Subtask)->List[KnowledgeItem]:
        prompt = self._read_prompt_from_md("prompts/get_knowledge.md")
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": subtask.subtask_content},
            ],
            response_format=KnowledgeResponse,
        )
        resp = completion.choices[0].message.parsed
        if resp:
            return resp.knowledges
        return []
    
    def generate_visualization(self, knowledge_item: KnowledgeItem):
        prompt = self._read_prompt_from_md("prompts/generate_visualization.md")
        # 只提取 knowledge_content 和 data_insight 两个字段
        content = knowledge_item.model_dump_json(include={"knowledge_content", "data_insight"})
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
            response_format=Visualization,  # 如果你使用的是新的 Visualization 模型
        )
        return completion.choices[0].message.parsed



    def run(self):
        title = self.generate_title()
        data: List[ParserResultItem] = []
        
        subtasks = self.generate_subtasks()
        for subtask in subtasks:
            knowledges = self.get_knowledges(subtask)
            konwledges_vis:list[knowledgeItemViz]=[]
            for knowledge in knowledges:
                vis = self.generate_visualization(knowledge)
                if not vis:
                    continue
                konwledges_vis.append(knowledgeItemViz(**knowledge.model_dump(),visualization=vis))
            data.append(ParserResultItem(**subtask.model_dump(), knowledges=konwledges_vis))

        return ParserResult(title=title, data=data)
    
    @staticmethod
    def extract_knowledge_from_parser_result(parser_result:ParserResult):

        result = ""
        result += f"Title: {parser_result.title}\n\n"
        for subtask in parser_result.data:
            if subtask.subtask_title:
                result += f"Subtask: {subtask.subtask_title}\n"
            if subtask.knowledges:
                for knowledge in subtask.knowledges:
                    if hasattr(knowledge, 'knowledge_content'):
                        result += f"- {knowledge.knowledge_content}\n"
            result += "\n"
        return result.strip()
    
    @staticmethod
    def generate_colors(text: str, client: OpenAI, model: str = "gpt-4o-mini") -> ColorScheme:
        """
        根据提供的文本内容生成适合信息图表的配色方案和字体推荐

        参数:
            text (str): 用于生成配色方案的文本内容
            client (OpenAI): OpenAI 客户端实例
            model (str): 使用的模型名称，默认为 "gpt-4o-mini"

        返回:
            ColorScheme: 包含主题颜色、背景颜色、一级强调颜色和字体、二级强调颜色和字体、文本颜色和字体的对象
        """
        # 从文件读取提示词
        system_prompt = PdfParser._read_prompt_from_md("prompts/generate_colors.md")
        
        # 用户提示
        user_prompt = f"{text}"

        # 调用 OpenAI API 并解析结果
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=ColorScheme
        )

        # 返回解析后的结果
        parsed_result = completion.choices[0].message.parsed
        if parsed_result is None:
            # 如果解析失败，返回一个默认的 ColorScheme
            return ColorScheme(
                theme_colors=[[51, 51, 58], [100, 100, 100], [150, 150, 150]],
                background_color=[255, 255, 255],
                first_level_color=[51, 51, 58],
                first_level_font="Arial",
                second_level_color=[100, 100, 100],
                second_level_font="Verdana",
                text_color=[51, 51, 58],
                text_font="Helvetica"
            )
        return parsed_result
    @staticmethod
    def rank( parser_result: ParserResult, infographic_size: tuple[int, int]) -> list[str]:
        return rank_infographic(parser_result.model_dump(), infographic_size)

if __name__ == "__main__":
    # client = OpenAI(
    #     api_key=os.getenv("OPENAI_KEY")
    #     )
    # pdf_parser = PdfParser("uploads/rabbit.pdf", "rabbit", client)
    # result = pdf_parser.run()
    # with open("result.json", "w",encoding='utf-8') as file:
    #     file.write(result.model_dump_json(indent=2))
    
    # # 测试新的 extract_knowledge_from_parser_result 函数
    # knowledge_content = PdfParser.extract_knowledge_from_parser_result(result)
    # print("\n提取的知识内容:")
    # print(knowledge_content)
    
    # # 测试新的 generate_colors 静态方法
    # print("\n生成配色方案:")
    # colors = PdfParser.generate_colors(knowledge_content, client)
    # print(colors.model_dump_json(indent=2))

    # 测试新的 rank 静态方法
    with open("result.json", "r",encoding='utf-8') as file:
       result = ParserResult(**json.load(file))
    
    print(PdfParser.rank(result, (1000, 1000)))