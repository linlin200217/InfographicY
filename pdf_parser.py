from openai import OpenAI
import PyPDF2
from pydantic import BaseModel
from typing import List, Optional,Literal
import os
from dotenv import load_dotenv
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

    def _read_prompt_from_md(self, md_path: str):
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
    

if __name__ == "__main__":
    client = OpenAI(
        api_key=os.getenv("OPENAI_KEY")
        )
    pdf_parser = PdfParser("/mnt/disk2/jielin.feng/InfographicY/uploads/WorldWar2.pdf", "worldwar2", client)
    result = pdf_parser.run()
    with open("result.json", "w",encoding='utf-8') as file:
        file.write(result.model_dump_json(indent=2))