import os
from pprint import pprint
import openai
import pdfplumber
import json
from openai import OpenAI
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from math import sqrt

load_dotenv()

client = OpenAI(
    #base_url="https://pro.aiskt.com/v1",
    api_key=os.getenv("OPENAI_KEY")
    #api_key=os.getenv("DEEPSEEK_KEY")
    )


def extract_text_from_pdf(pdf_path):
    full_text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
    except Exception as e:
        print(f"提取PDF文字时出错: {e}")
        return None
    return full_text

# AGENT1: TASK DECOPOSITION ASSISTANT
# Define the function to generate subtasks
# AGENT1: TASK DECOPOSITION ASSISTANT
# Define the function to generate subtasks

def generate_title(text):
    system_prompt = """
    You are a naming assistant. Your task is to create concise, clear, and brief infographic titles based on provided sentences. The title should be simple, direct, and suitable for an infographic. 
    Example:
    Input:Death and casualties in World War II
    Output:
    World War II: Deaths & Casualties
    """
    user_prompt = f"""
    Text: {text}
    """

    # Call the OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Use the appropriate model
        #model = "deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=False
    )

    # Extract and return the subtasks
    Title = completion.choices[0].message.content
    return Title

def generate_subtasks(text, question):
    # Prepare the prompt
    system_prompt = """
    You are a task decomposition assistant. Your task is to analyze textual paragraphs provided by the user, extract key information, and output the results in JSON format. Additionally, you need to break down the task into subtasks based on the provided text and question. The subtasks should be connected according to narrative logic, which includes the following types:
      1. Cause-effect: because; and so.
      2. Violated expectation: although; but; while.
      3. Similarity: and; (and) similarly.
      4. Contrast: by contrast; but.
      5. Temporal: sequence (and) then; first, second, . . . ; before; after; while.
      6. Attribution: according to . . . ; . . . said; claim that . . . ; maintain that . . . ; stated that . . . .
      7. Example: for example; for instance.
      8. Elaboration: also; furthermore; in addition; note (furthermore) that; (for, in, on, against, with, . . . ) which; who; (for, in, on, against, with, . . . ) whom.
      9. Generalization: in general.
    For each subtask, output the following structure:

    {
      "subtask_num":<num is the index of subtask, e.g., subtask_1, subtask_2..> {
        "subtask_title": "<A short title for the subtask>",
        "subtask_content": "<ALL relevant content from the text for this subtask>",
        "subtask_relation": "<The narrative logic relationship with the user's provided prompt>",
        "related_subtask":
          {
            "title": "<If there is a narrative logic relationship with any previous subtask, show the title of that specific subtask. Priority is given to the Subtask_title for determining the relationship, while Subtask_content is used only as supplementary information. If no narrative logic relationship is detected, return None.>",
            "relation": "<If there is a narrative logic relationship with any previous subtask, then state the narrative logic relationship with that subtask. Priority is given to the Subtask_title for determining the relationship, while Subtask_content is used only as supplementary information. If no narrative logic relationship is detected, return None.>"
          },
        }

    }
    Your output should following above structure in JSON format. Note: The total number of subtasks should NOT exceed 10.

    Strict Rules for Determining [title, relation]
      - Priority to Subtask_title: The relationship between subtasks should primarily be determined by analyzing the Subtask_title. Use Subtask_content only to confirm or clarify the relationship if the title is ambiguous.
      - Explicit Connection Required: A relationship between two subtasks must be explicitly supported by the text. If the connection is implied but not explicitly stated, return [None, None].
      - Use Defined Narrative Logic Types Only: Only use the 9 defined narrative logic types (e.g., Cause-effect, Similarity, Elaboration, etc.). Do not infer relationships outside these types.
      - Keyword-Based Judgment: Use the keywords provided for each narrative logic type (e.g., "because" for Cause-effect, "although" for Violated expectation) to determine the relationship. If no such keywords or clear logical connectors exist, return [None, None].
      - Avoid Overgeneralization: Do not assume relationships based on general knowledge or external context. Only use information explicitly provided in the text.
      - One-to-One Relationship: Each subtask can only have one relationship with one previous subtask. If multiple relationships are possible, choose the most explicit and direct one.

    Example1(Here I give in list, you should provide me JSON):
      -User input question: What is killing the frog?

      -Subtask_title: Factors leading to frog population decline.
      -Subtask_content: The factors leading to the decline of frog populations include overpopulation of predators, disease, pesticide-induced mutations, roadkill, and human consumption.
      -Subtask_relation: Example
      -[title, relation]: [None, None].

      -Subtask_title: Areas of amphibian population decline.
      -Subtask_content: Areas of decline in amphibian population are xx, xx, and xxx (shown in world map).
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

      -Subtask_title: Global disease impact on amphibians.
      -Subtask_content: A third of the amphibian population in the world is already infected with a fatal disease.
      -Subtask_relation: Elaboration
      -[title, relation]: [Areas of amphibian population decline, Elaboration].

      -Subtask_title: Disappearance of frog and toad species.
      -Subtask_content: 200 Frogs & Toad species have completely disappeared.
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

      -Subtask_title: Extinction rate of amphibians.
      -Subtask_content: 20% of the world's amphibians species are EXTINCT.
      -Subtask_relation: Elaboration
      -[title, relation]: [Areas of amphibian population decline, Generalization].

      -Subtask_title: Amphibians as a percentage of extinct species.
      -Subtask_content: 32% of the world's extinct species are amphibians.
      -Subtask_relation: Elaboration
      -[title, relation]: [Extinction rate of amphibians, Similarity].

    Example2(Here I give in list, you should provide me JSON):
      -User input question: Hawaii 2012

      -Subtask_title: Time spent in Hawaii.
      -Subtask_content: A total of 29 days spent in paradise, in which Kauai for 15 days, Oahu for 11 days, and Maui for 3 days.
      -Subtask_relation: Generalization
      -[title, relation]: [None, None].

      -Subtask_title: Time before reuniting with old friends.
      -Subtask_content: 3.25 AVERAGE YEARS PASSED BEFORE REUNITING WITH OLD BUDS.
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

      -Subtask_title: Exploration of new places.
      -Subtask_content: Explored and discovered 80% new buildings, Explored 66% new waterfalls, and Explored 40% new beaches.
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

      -Subtask_title: Improvement in Robert's linguistic skills.
      -Subtask_content: Robert's linguistic skill increased a lot.
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

      -Subtask_title: Creatures encountered.
      -Subtask_content: Creatures encountered include dolphin, turtle, and whale.
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

      -Subtask_title: New additions to the family.
      -Subtask_content: 2 new ADDITIONS TO THE FAMILY.
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

      -Subtask_title: Miles of Maui's roads survived.
      -Subtask_content: 71.2 MILES OF MAUI'S WINDING ROADS SURVIVED.
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

      -Subtask_title: Photos taken.
      -Subtask_content: 941 photos.
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

      -Subtask_title: Noteworthy adventures.
      -Subtask_content: Noteworthy ventures include 10000m sky dive, 180m bike riding, sea level boarding, and -40m dive.
      -Subtask_relation: Elaboration
      -[title, relation]: [None, None].

    Example3(Here I give in list, you should provide me JSON):
      - User input question: Titanic survival factors
      - Subtask_title: Titanic's lifeboat capacity and survival statistics.
      - Subtask_content: According to Wikipedia, there were approximately 1,317 passengers and 900 crew members aboard the Titanic when it crashed into an iceberg in the North Atlantic Ocean on its maiden voyage in 1912. The ship was considered under capacity, as inventors estimated it would be able to carry 2,435 passengers and 900 crew members at any given time. As Rose Kate, so modestly pointed out, however, there were only 20 lifeboats on the ship at this time — enough to save approximately 1,178 people. While this was a non-issue for the fictional Mr. Andrews and his unsinkable ship, hindsight is 20/20. Only 705 people survived the horrific event, now considered one of the deadliest commercial peacetime maritime disasters in modern history.
      - Subtask_relation: Example
      - [title, relation]: [None, None].

      - Subtask_title: Survival rates by class and gender.
      - Subtask_content: One of the first ways we sliced and diced the data was by class. While in Kate and Leo's version of events the lifeboats were not seated by class, turns out there was a difference in survival rates depending on what class ticket you held. 61.9% of First Class passengers survived while only 43% of Second and 25.5% of Third Class passengers survived. We also broke the data down by class and gender. Turns out, the blockbuster hit was right in terms of women getting on the lifeboats first. Women had a much higher chance of survival — regardless of what class they were in — then men did. Of the 466 women on board, 339 survived. Of the 843 men on board, only 161 survived — a measly 19% compared to the 73% of women who made it safely back to shore.
      - Subtask_relation: Elaboration
      - [title, relation]: [Titanic's lifeboat capacity and survival statistics, Elaboration].

      - Subtask_title: Survival rates by age.
      - Subtask_content: Next, we wanted to determine how much age played a factor in whether or not someone survived the Titanic. According to our data set, the oldest person aboard the Titanic was 80 years old while the youngest was just a few months. The women on board the ship were generally a bit younger than the men, the average age of the males was 30.6 while the average age of the females was 28.7. As you can see, however, there was more of a discrepancy in terms of the average age of survivors versus the average age of those who perished. For men, the younger you were, the more likely you were to have survived the tragedy. For women, the older you were, the more likely you were to have survived. We already know that overall women had a higher chance of survival, so that's another point for the movie — of the males, looks like the children were sent to the lifeboats first.
      - Subtask_relation: Elaboration
      - [title, relation]: [Survival rates by class and gender, Similarity].

      - Subtask_title: Survival rates by family presence.
      - Subtask_content: Were you alone onboard like Jack or surrounded by family (albeit people you may not want relations with..) like Rose? Would either scenario make you more likely to survive on that fateful night in April? The graph below breaks out not only average number of family members but also the average number of spouses/siblings and parents/children aboard. Take a gander at the results:To no surprise, you had a better chance of survival if you had more family members aboard. It seems the presence of siblings or spouses had little to no bearing on your chances of getting out alive, as the average number is about the same for both those who perished and those who survived. Once again it seems like "women and children first," as most Hollywood depictions show, may not have just been a trope. Being a parent or child gave you a lifeline - the greater number of parents or children you had accompanying you on the ship, the better your chances of survival.
      - Subtask_relation: Elaboration
      - [title, relation]: [Survival rates by age, Similarity].

      - Subtask_title: Survival rates by port of departure.
      - Subtask_content: Not many people realized that Titanic had three ports of call before sailing the high seas across the great Atlantic. The three ports were Queesntown, Ireland (present day Cobh, Ireland), Southampton, U.K., and Cherbourg, France. The highest rate of survival - shown below - was from Cherbourg, France where over half of the passengers departing from this region survived the accident. Those whom called Ireland their port of call had the second-highest survival rate at 35.8% while Southampton, U.K. came in last with a survival rate of only ⅓. When you look at Average Class per passenger, it most certainly makes sense as to why France boasts such a high survival rate with an average of 1.8. As for Ireland coming in second, most likely due to the female:male ratio than the class with 48% female passengers vs. UK's 32%.
      - Subtask_relation: Elaboration
      - [title, relation]: [Survival rates by family presence, Similarity].

      - Subtask_title: Hollywood's depiction vs. reality.
      - Subtask_content: As shown in the data, Hollywood's depiction of the Titanic wasn't far from the mark. If you were in fact a late 20-something female, had a parent or child on board and were a first class passenger (optimally from France) on the boat mdash; you had the greatest likelihood of survival. Historically speaking, the 58 men that survived the incident in real life received loads of criticism mdash; mainly from the press mdash; since there were more than 150 women and children who perished instead. Women and children first, indeed.That being said, there was an opportunity to save at least one more male from the wreckage, *cough, cough* ROSE! And while Jack Dawson's survival would not have had a significant effect on our overall analysis, it would have made for a much better ending to the epic blockbuster film.
      - Subtask_relation: Elaboration
      - [title, relation]: [None, None].

    NOTE:
      - Subtask_content: Output ALL relevant content; do not use ellipses.
      - Subtask_relation: Strictly determine the relationship between the subtask and the user's prompt.
      - [title, relation]: Only return a relationship if it strictly exists based on the defined narrative logic types. If no relationship is detected, return [None, None].
      - Ensure the narrative logic relationships are judged strictly based on the provided definitions and examples.
    """

    user_prompt = f"""
    Text: {text}
    Question: {question}
    """

    # Call the OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4o",  # Use the appropriate model
        #model = "deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={
        'type': 'json_object'
        },
        stream=False
    )

    # Extract and return the subtasks
    subtasks = completion.choices[0].message.content
    return subtasks

#subtasks = generate_subtasks(extract_text_from_pdf("/mnt/disk2/jielin.feng/InfographicY/uploads/WorldWar2.pdf"), "Death in worldwar2")


#AGENT2
#AGENT2
##"Knowledge_num":<num is the index of knowledge, e.g., Knowledge_1, Knowledge_2..>
def generate_Knowledge(text):

    # Prepare the prompt
    system_prompt = """
    You are a knowledge extraction assistant specialized in designing infographics. Your task is to extract data-driven insights from text that are simple, unique, and visually representable. Follow these rules:

    Data Insight Types:
    - Only classify knowledge into these types (one type per insight, if more than one insight, chose the most appropriate one.):
    1. Value: Standalone numerical facts (e.g., "189 deaths").
    2. Difference: Explicit comparisons (e.g., "25% higher than").
    3. Proportion: Part-to-whole relationships (e.g., "28% of X", "1 in 10", "1/5").
    4. Trend: Time-bound changes (e.g., "grown by 40% annually", "increase", "decrease").
    5. Categorization: Must contain at leaset one discrete classes (e.g., "Basic, Pro, Enterprise tiers").
    6. Distribution: Data spread (e.g., "peaks at 20–34 years").
    7. Rank: Ordered hierarchy (e.g., "ranks first").
    9. Extreme: Maxima/minima (e.g., "hottest month ever").

    For each data knowledge, output the results in JSON format:
    {
      "Knowledge_num":(num is the index of knowledge, e.g., Knowledge_1, Knowledge_2..)
      {[
        "Knowledge_content": "<Extracted knowledge content (summarize the knowledge based on insight simply, ensuring the data is included)>",
        "Data_insight": "<Specify the type of information included in the knowledge_content (value, difference, proportion, trend, categorization, distribution, rank, extreme).>"
        "First_level_Highlight": "<According to the knowledge_content, identify the Most critical number/superlative.>",
        "Second_level_Highlight": "<According to the knowledge_content, identify the Secondary contextual keyword> or null",
        "Icon_Keyword": "<Single iconic noun from original knowledge_content text>",

      ]}
   }

   If no knowledge is detected, return null in following format:
   {
    "Knowledge_num":<num is the index of knowledge, e.g., Knowledge_1, Knowledge_2..> null,
   }

    Rule for First_level_Highlight:
      - Must exist
      - Multiple values comma-separated

    Rule for Second_level_Highlight:
      - Optional (return null if none)
      - No overlap with First_level

    Rule for Icon_Keyword:
      - Must be original noun
      - No modifications allowed

    Note:
      - Use strict JSON format for each insight.
      - Skip insights that don't clearly match the defined types.
      - Ensure no repetition (e.g., separate "189 deaths" and "700 injured" into distinct entries).

    Example(Here I give in list, you should provide me JSON):
    Input:
      "The tragic Mumbai train bombing resulted in 189 deaths, leaving a devastating impact on countless families and communities. In addition to the fatalities, 700 individuals were injured, some of whom suffered life-altering wounds. The legal response to the attack included 5 death sentences, a stark reminder of the severity of the crime. Furthermore, 7 individuals were sentenced to life imprisonment, reflecting the gravity of their involvement in this heinous act of terrorism."
    Output:

      {
  "knowledge1": [
    {
      "Knowledge_content": "189 deaths.",
      "Data_insight": "Value",
      "First_level_Highlight": "189",
      "Second_level_Highlight": null,
      "Icon_Keyword": "deaths"
    }
  ],
  "knowledge2": [
    {
      "Knowledge_content": "5 death sentences.",
      "Data_insight": "Value",
      "First_level_Highlight": "5",
      "Second_level_Highlight": null,
      "Icon_Keyword": "death sentences"
    }
  ],
  "knowledge3": [
    {
      "Knowledge_content": "700 injured.",
      "Data_insight": "Value",
      "First_level_Highlight": "700",
      "Second_level_Highlight": null,
      "Icon_Keyword": "injured"
    }
  ],
  "knowledge4": [
    {
      "Knowledge_content": "7 life imprisonment sentences.",
      "Data_insight": "Value",
      "First_level_Highlight": "700",
      "Second_level_Highlight": null,
      "Icon_Keyword": "imprisonment"
    }
  ]
}
    """

    user_prompt = f"""
    Text: {text}
    """

    # Call the OpenAI API
    completion = client.chat.completions.create(
        #model="deepseek-chat",  # Use the appropriate model
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={
        'type': 'json_object'
    },
        stream=False
    )

    # Extract and return the subtasks
    knowledges = completion.choices[0].message.content
    return knowledges

def process_subtasks(subtasks):
    """
    将 subtasks 中的每个 subtask_content 依次传入 generate_Knowledge 函数，
    并将结果组织为更大的 JSON 文件。

    参数:
        subtasks (str): 包含 subtasks 的 JSON 字符串（字典形式）。

    返回:
        list: 包含所有 subtask_title 和对应 knowledge 结果的列表。
    """
    try:
        subtasks_dict = json.loads(subtasks)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return []

    results = []

    for subtask_key, subtask in subtasks_dict.items():

        subtask_title = subtask.get("subtask_title", "")
        subtask_content = subtask.get("subtask_content", "")
        subtask_relation = subtask.get("subtask_relation","")
        related_subtask = subtask.get("related_subtask","")

        knowledge_result = generate_Knowledge(subtask_content)

        results.append({
            "subtitle": subtask_title,
            "relation_withTitle": subtask_relation,
            "relation_withVG": related_subtask,
            "knowledge": knowledge_result

        })

    return results

def get_subtasks(pdf_path,question):
    subtasks_result = generate_subtasks(extract_text_from_pdf(pdf_path), question)
    return subtasks_result



# AGENT2 - Visualization
# AGENT2 - Visualization
def generate_Vis(content, insight):
    # Prepare the prompt
    system_prompt = """
    I will provide knwoledge content for content input, like following example:
    "15 in 56 deaths"
    I will provide data insight for insight input, like following exmaple:
    "Value"

    Data_insight includes:
      1. Value: Standalone numerical facts (e.g., "189 deaths").
      2. Difference: Explicit comparisons (e.g., "25% higher than").
      3. Proportion: Part-to-whole relationships (e.g., "28% of X", "1 in 10", "1/5").
      4. Trend: Time-bound changes (e.g., "grown by 40% annually", "increase", "decrease").
      5. Categorization: Discrete classes (e.g., "Basic, Pro, Enterprise tiers").
      6. Distribution: Data spread (e.g., "peaks at 20–34 years").
      7. Rank: Ordered hierarchy (e.g., "ranks first").
      8. Extreme: Maxima/minima (e.g., "hottest month ever").

    You are a data analyst. Your task is to choose a visualization form according to Knowledge_content and Data_insight.
    You can choose from the following visualization forms:
         1. pie chart: if there are proportions of different entities
         2. bar chart: if you need to show features of each entity
         3. line chart: show trends in data over time or fluctuations
         4. pictogram: if you want to show the magnitude of an important stat or visualize a fraction or percentage
         5. none

    Your output should be one of the following Json form:
        1.{
             "If Visualization": "None",
             "Visulization_type": None,

        },

  
        2.{
             "If Visualization": "Yes",
             "Visualization_type": "Pie_Chart",
             "Categorization":["xx","xx","xx"],
             "proportion":["20%","30%","50%"]
        },
        3.{
             "If Visualization": "Yes",
             "Visualization_type": "Bar_Chart",
             "Categorization":["xx","xx"],
             "value":[30,50]
        },
        4.{
             "If Visualization": "Yes",
             "Visualization_type": "Line_Chart",
             "Categorization":["xx","xx","xx"],
             "value":[10,12,15]
        },
        5.{
             "If Visualization": "Yes",
             "Visualization_type": "Pictogram",
             "Highlight": 12,
             "Total": 50
        }
"""

    user_prompt = f"""
    content: {content}
    insight: {insight}
    """

    # Call the OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=False,
        response_format={
        'type': 'json_object'
    },

    )

    # Extract and return the subtasks
    visualization = completion.choices[0].message.content
    pprint(visualization)
    return visualization


def get_knowledge(pdf_path,question):
    knowledge_result = process_subtasks(get_subtasks(pdf_path,question))
    return knowledge_result 

def data_with_visualization(knowledge_data):
    for item in knowledge_data:
        knowledge_dict = json.loads(item["knowledge"])
        for key in knowledge_dict:
            if knowledge_dict[key] is not None:  # 检查knowledge是否为空
                knowledge_list = knowledge_dict[key]
                for knowledge_object in knowledge_list:
                  knowledge = knowledge_dict[key]
                  content = knowledge_object.get("Knowledge_content", None)
                  insight = knowledge_object["Data_insight"]
                  visualization = generate_Vis(content, insight)
                  knowledge_object["visualization"] = visualization
        item["knowledge"] = json.dumps(knowledge_dict, indent=2)
    return knowledge_data

# NEW UPDATE
def extract_knowledge_contents(json_file_path):
    """
    从指定的 JSON 文件中提取知识内容并返回一个结构化字符串

    参数:
        json_file_path (str): JSON 文件的路径

    返回:
        str: 包含标题、subtask_title 和对应 knowledge_content 的结构化字符串
    """
    import json
    
    # 读取指定的 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # 初始化结果字符串
    result = ""
    
    # 添加标题
    if 'title' in data:
        result += f"Title: {data['title']}\n\n"
    
    # 遍历 data 列表中的每个 subtask
    for subtask in data['data']:
        # 添加 subtask_title（如果存在）
        if 'subtask_title' in subtask and subtask['subtask_title']:
            result += f"Subtask: {subtask['subtask_title']}\n"
        
        # 添加该 subtask 的所有 knowledge_content
        if 'knowledges' in subtask:
            for knowledge in subtask['knowledges']:
                if 'knowledge_content' in knowledge:
                    result += f"- {knowledge['knowledge_content']}\n"
        
        # 在每个 subtask 之间添加分隔符
        result += "\n"
    
    # 去除最后一个多余的换行符
    return result.strip()

def extract_knowledge_from_parser_result(parser_result):
    """
    从 ParserResult 对象中提取知识内容并返回一个结构化字符串

    参数:
        parser_result (ParserResult): ParserResult 对象

    返回:
        str: 包含标题、subtask_title 和对应 knowledge_content 的结构化字符串
    """
    # 初始化结果字符串
    result = ""
    
    # 添加标题
    result += f"Title: {parser_result.title}\n\n"
    
    # 遍历 data 列表中的每个 subtask
    for subtask in parser_result.data:
        # 添加 subtask_title
        if subtask.subtask_title:
            result += f"Subtask: {subtask.subtask_title}\n"
        
        # 添加该 subtask 的所有 knowledge_content
        if subtask.knowledges:
            for knowledge in subtask.knowledges:
                if hasattr(knowledge, 'knowledge_content'):
                    result += f"- {knowledge.knowledge_content}\n"
        
        # 在每个 subtask 之间添加分隔符
        result += "\n"
    
    # 去除最后一个多余的换行符
    return result.strip()

# AGENT2 - COLOR PALATTE DESIGNER
import openai
import json

def generate_colors(text):
    # 增强版系统提示
    system_prompt = """
    You are a professional color palette generator for infographic designs.
    Based on the emotional tone and semantic context of the provided text, please generate a color palette and font recommendations following the JSON output structure below:
    
    {
    "themeColors": [<list of 3-5 RGB colors>],
    "backgroundColor": [<one RGB color>],
    "First_level_Color": [<one RGB color from themeColors>],
    "First_level_Font": "<one font style>",
    "Second_level_Color": [<one RGB color from themeColors>],
    "Second_level_Font": "<one font style>",
    "Text_Color": [<one RGB color: either [51,51,58] or [255,255,255]>],
    "Text_Font": "<one font style>"
  }

    Definitions:
    themeColors: Choose 3 to 5 RGB color codes representing the infographic's overall theme, aligned with the text content's emotion and context.
    backgroundColor: Select 1 RGB color suitable for the infographic background, harmonizing well with the chosen theme colors.
    First_level_Color: An eye-catching highlight color for the most important information, selected from the themeColors.
    First_level_Font: A font style for the most important highlighted content, chosen from the provided font list.
    Second_level_Color: A highlight color for the second-most important information, also selected from the themeColors.    
    Second_level_Font: A font style for secondary highlighted content, chosen from the provided font list.
    Text_Color: Choose either [51,51,58] (dark) or [255,255,255] (white), ensuring sharp contrast with the background color for clear readability.
    Text_Font: A font style suitable for regular textual content, chosen from the provided font list.
  
    Font List : 
    ['Arial', 'Verdana', 'Helvetica', 'Courier', 'Consolas', 'cursive', 'Tahoma', 'Trebuchet MS', 'Times New Roman', 'Georgia', 'Palatino', 'Baskerville', 'Gill Sans', 'Andalé Mono', 'Avantgarde', 'Optima', 'Arial Narrow', 'Didot', 'Bookman', 'American Typewriter', 'OCR A Std', 'Brush Script MT', 'Lucida', 'Bradley Hand', 'Trattatello', 'fantasy', 'Harrington', 'Marker Felt', 'Chalkduster', 'Comic Sans MS' ]


    Requirements:
    1. Generate colors and fonts that match the emotional tone and semantic context of the provided text.
    2. Theme colors should be harmonious and suitable for use in graphics, icons, and highlighted text.
    3. The background color must complement the theme colors effectively.
    4. Highlight colors must be chosen directly from the themeColors to maintain visual consistency.
    5. Font styles must reflect the emotion, semantics, and context of the provided text.
    6. Ensure your overall recommendations adhere to aesthetic and infographic design principles.


    

    Example valid output:
    {
      "themeColors": [[45, 32, 27], [78, 64, 55], [134, 86, 52], [92, 109, 125]],
      "backgroundColor": [255, 255, 255],
      "First_level_Color": [45, 32, 27],
      "First_level_Font": "Verdana",
      "Second_level_Color": [78, 64, 55],
      "Second_level_Font": "Arial",
      "Text_Color": [51, 51, 58],
      "Text_Font": "Gill Sans"
    }
    """

    # 优化后的用户提示
    user_prompt = f"""
    {text}
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=False,
        response_format={
        'type': 'json_object'
    },

    )

    # 处理响应并解析JSON
    ColorFont = completion.choices[0].message.content
    return ColorFont

# 示例使用
'''
text = extract_knowledge_contents("/mnt/disk2/jielin.feng/InfographicY/result.json")
colors = generate_colors(text)
print(colors)
'''





'''
with open("/mnt/disk2/jielin.feng/InfographicY/result.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
'''


import json

def count_visual_groups(dict_data):
    # 初始的 relation 类型统计字典，每种 narrative logic 初始 count 都为 0
    relation_dic = {
        "Elaboration": 0,
        "Example": 0,
        "Attribution": 0,
        "Generalization": 0,
        "Temporal": 0,
        "Cause-Effect": 0,
        "Violated expectation": 0,
        "Contrast": 0,
        "Similarity": 0
    }
    
    """
    统计 result.json 文件中 visual group、knowledge、related subtask 的数量、
    relation 类型统计字典以及每个 visual group 被其他相关 visual group 引用的次数。
    
    参数:
        json_file_path (str): JSON 文件的路径

    返回:
        tuple: (visual group 的数量, knowledge 的数量, related subtask 的数量,
                relation 类型统计字典, visual group 引用计数列表)
    """

    
    groups = dict_data.get('data', [])
    visual_group_count = len(groups)
    knowledge_count = 0
    related_subtask_count = 0
    
    # 先统计 relation 类型及 knowledge、related_subtask 数量
    for subtask in groups:
        knowledges = subtask.get('knowledges', [])
        knowledge_count += len(knowledges)
        
        related_subtask = subtask.get('related_subtask')
        if related_subtask and related_subtask.get('title') is not None:
            related_subtask_count += 1
            relation_type = related_subtask.get('relation')
            if relation_type in relation_dic:
                relation_dic[relation_type] += 1

    # 构建 visual group 的标题列表，用于匹配 related_subtask 中的 title
    visual_group_titles = [group.get("subtask_title") for group in groups]
    # 初始化引用计数列表，每个 visual group 初始为 0
    visual_group_ref_count = [0] * visual_group_count

    # 遍历每个 visual group的 related_subtask，
    # 如果其 title 与某个 visual group 的 subtask_title 匹配，则将该 visual group 的计数加 1
    for subtask in groups:
        related_subtask = subtask.get('related_subtask')
        if related_subtask:
            related_title = related_subtask.get('title')
            if related_title:
                try:
                    index = visual_group_titles.index(related_title)
                    visual_group_ref_count[index] += 1
                except ValueError:
                    # 如果没有匹配上，则跳过
                    pass

    return visual_group_count, knowledge_count, related_subtask_count, relation_dic, visual_group_ref_count


  


    # 假设每个subtask_title属于一个visual group
#print(count_visual_groups("/mnt/disk2/jielin.feng/InfographicY/result.json"))


#VG_num = len(data['data'])

def Rank_Template(visual_group_count, knowledge_count, related_subtask_count, relation_dic, visual_group_ref_count, infographic_size):
    # 初始分数
    Grid = 0
    Spiral = 0
    Landscape = 0
    Star = 0
    Portrait = 0
    PortraitGrid = 0

    # 1. 根据 visual_group_count 计分
    if visual_group_count > 8:
        Grid += 1
        Spiral += 1
    elif 6 <= visual_group_count <= 8:
        Star += 1
        PortraitGrid += 1
    elif visual_group_count < 6:
        Landscape += 1
        Portrait += 1

    # 2. 根据 knowledge_count/visual_group_count 计分
    ratio_knowledge = (knowledge_count / visual_group_count) if visual_group_count != 0 else 0
    if ratio_knowledge < 0.3:
        Portrait += 1
        Landscape += 1
    elif 0.3 <= ratio_knowledge <= 0.6:
        Star += 1
        PortraitGrid += 1
    elif 0.6 < ratio_knowledge <= 0.75:
        Grid += 1
    elif ratio_knowledge > 0.75:
        Spiral += 1

    # 3. 根据 related_subtask_count/visual_group_count 计分
    ratio_related = (related_subtask_count / visual_group_count) if visual_group_count != 0 else 0
    if ratio_related > 0.8:
        Spiral += 1
    elif 0.6 <= ratio_related <= 0.8:
        Portrait += 1
        Star += 1
        PortraitGrid += 1
        Landscape += 1
    elif ratio_related < 0.6:
        Grid += 1

    # 4. 根据 relation_dic 的规则计分
    # 如果 Generalization、Elaboration 与 Example 均大于 0，则 Portrait 与 Landscape 各 +1
    if (relation_dic.get("Generalization", 0) > 0 and 
        relation_dic.get("Elaboration", 0) > 0 and 
        relation_dic.get("Example", 0) > 0):
        Portrait += 1
        Landscape += 1
    # 如果存在 Generalization，但 Elaboration 或 Example 不同时大于 0，则 Star +1, PortraitGrid +1
    elif relation_dic.get("Generalization", 0) > 0 and (relation_dic.get("Elaboration", 0) == 0 or relation_dic.get("Example", 0) == 0):
        Star += 1
        PortraitGrid += 1

    # 如果 Example 的数量大于或等于 2，则 Spiral +1
    if relation_dic.get("Example", 0) >= 2:
        Spiral += 1

    # 如果有超过 3 种类型的 relation count 大于 0，则 Grid +1
    positive_types = sum(1 for v in relation_dic.values() if v > 0)
    if positive_types > 3:
        Grid += 1

    # 5. 根据 visual_group_ref_count 计分
    # 如果存在任一数字大于 2，则 Star +1, PortraitGrid +1
    if any(count > 2 for count in visual_group_ref_count):
        Star += 1
        PortraitGrid += 1

    # 如果 visual_group_ref_count 只包含 0 和 1，则判断 1 与 0 的数量
    if set(visual_group_ref_count).issubset({0, 1}):
        ones = visual_group_ref_count.count(1)
        zeros = visual_group_ref_count.count(0)
        if ones > zeros:
            Spiral += 1
            Portrait += 1
            Landscape += 1
        elif zeros > ones:
            Grid += 1

    # 整体分数字典
    scores = {
        "Grid": Grid,
        "Spiral": Spiral,
        "Landscape": Landscape,
        "Star": Star,
        "Portrait": Portrait,
        "PortraitGrid": PortraitGrid
    }

    # 6. 根据分数排序，分数相同时按 tie-break 优先级排序
    # tie-break 优先级：Grid > Star > PortraitGrid > Portrait > Spiral > Landscape
    priority_order = {"Grid": 0, "Star": 1, "PortraitGrid": 2, "Portrait": 3, "Spiral": 4, "Landscape": 5}
    sorted_scores = sorted(scores.items(), key=lambda x: (-x[1], priority_order[x[0]]))
    
    # 7. 根据 infographic_size 做特殊排序处理
    # infographic_size: [height, width]
    width, height = infographic_size
    if height > width:
        # 如果是竖屏（height > width），则 Landscape 无论分数如何都自动垫底
        sorted_scores = [item for item in sorted_scores if item[0] != "Landscape"]
        sorted_scores.append(("Landscape", scores["Landscape"]))
    else:
        # 如果是横屏（width > height），且 Portrait 的分数大于或等于 Landscape，则自动把 Landscape 排到 Portrait 前面
        if scores["Portrait"] >= scores["Landscape"]:
            # 获取 Portrait 与 Landscape 在当前排序中的位置
            portrait_index = next((i for i, item in enumerate(sorted_scores) if item[0] == "Portrait"), None)
            landscape_index = next((i for i, item in enumerate(sorted_scores) if item[0] == "Landscape"), None)
            if (portrait_index is not None and landscape_index is not None and 
                portrait_index < landscape_index):
                # 交换二者的位置
                sorted_scores[portrait_index], sorted_scores[landscape_index] = sorted_scores[landscape_index], sorted_scores[portrait_index]

    # 返回类型名称列表，按最终排序顺序排列
    sorted_types = [k for k, v in sorted_scores]
    return sorted_types
 

def reorder_valentine_data(valentine_data):
    """
    根据相关子任务关系对 valentine_data 中的 "data" 数组重新排序：
    如果某个子任务的 related_subtask.title 与另一子任务的 subtask_title 相同，
    则认为这两个任务有关联，排序时尽量使它们相邻。同时保留原始数组中第一个任务的位置不变。
    
    参数:
      valentine_data: dict，格式如下
        {
          "title": "Factors Influencing Survival Rates",
          "data": [ {subtask1}, {subtask2}, ... ]
        }
    返回:
      一个新的字典，结构与输入相同，但 "data" 数组经过排序。
    """
    data = valentine_data["data"]
    n = len(data)
    
    # 建立从 subtask_title 到（原始索引, 子任务对象）的映射
    title_to_info = {
        item["subtask_title"]: (i, item)
        for i, item in enumerate(data)
    }
    
    # 初始化图结构和入度：节点为 subtask_title
    graph = { title: [] for title in title_to_info }
    indegree = { title: 0 for title in title_to_info }
    
    # 遍历每个子任务，根据 related_subtask.title 建立边：如果 A 的标题与 B 的 related_subtask.title 相同，则 A->B
    for item in data:
        rel_title = item.get("related_subtask", {}).get("title")
        if rel_title and rel_title in title_to_info:
            parent_title = rel_title
            child_title = item["subtask_title"]
            graph[parent_title].append(child_title)
            indegree[child_title] += 1

    # 利用拓扑排序（使用原始顺序作为 tie-breaker）对任务进行排序
    # 首先把所有入度为0的节点加入队列，并按照原始顺序排序
    queue = [title for title, deg in indegree.items() if deg == 0]
    queue.sort(key=lambda t: title_to_info[t][0])
    
    sorted_titles = []
    while queue:
        current = queue.pop(0)
        sorted_titles.append(current)
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
                queue.sort(key=lambda t: title_to_info[t][0])
    
    # 如果存在环或遗漏节点，则把未排序的节点按照原始顺序追加
    for title, (i, _) in title_to_info.items():
        if title not in sorted_titles:
            sorted_titles.append(title)
    
    # 保证原始数组中的第一个任务不变：如果排序结果首个任务不是原始第一个，则将原始第一个任务移到最前面
    first_title = data[0]["subtask_title"]
    if sorted_titles[0] != first_title:
        if first_title in sorted_titles:
            sorted_titles.remove(first_title)
        sorted_titles.insert(0, first_title)
    
    # 根据新顺序构造新的 data 数组
    new_data = [ title_to_info[title][1] for title in sorted_titles ]
    
    # 返回新的数据结构
    return {
        "title": valentine_data["title"],
        "data": new_data
    }

def rank_infographic(dict_data:dict, infographic_size:tuple[int, int]) -> list[str]:
    visual_group_count, knowledge_count, related_subtask_count, relation_dic, visual_group_ref_count = count_visual_groups(dict_data)
    return Rank_Template(visual_group_count, knowledge_count, related_subtask_count, relation_dic, visual_group_ref_count, infographic_size)

def add_padding_to_layout(layout, padding=1):
    """
    Adds padding to all blocks within the layout dictionary.
    
    Args:
        layout: Dictionary containing the poster layout with coordinates for each block.
        padding: Float value to add as padding to each block (default=10).
    
    Returns:
        New layout dictionary with padded coordinates for each block.
    """
    import copy
    
    # Create a deep copy of the layout to avoid modifying the original
    padded_layout = copy.deepcopy(layout)
    
    # Helper function to apply padding to a block's coordinates
    def pad_coords(coords):
        if coords is None:
            return None
        # Original coordinates
        x1, y1 = coords[0]
        x2, y2 = coords[3]  # Bottom-right corner
        # Apply padding
        x1_padded = x1 + padding
        y1_padded = y1 + padding
        x2_padded = x2 - padding
        y2_padded = y2 - padding
        # Ensure the block remains valid (non-negative width and height)
        if x1_padded >= x2_padded or y1_padded >= y2_padded:
            return None  # Block becomes invalid with padding
        return [
            [x1_padded, y1_padded],
            [x2_padded, y1_padded],
            [x1_padded, y2_padded],
            [x2_padded, y2_padded]
        ]
    
    # Pad the Title block
    padded_layout["Title"] = pad_coords(padded_layout["Title"])
    
    # Iterate through each Visual Group (VG)
    for vg_key in padded_layout:
        if vg_key.startswith("VG"):
            vg = padded_layout[vg_key]
            # Pad the Subtitle and VG coords
            if 'Subtitle' in vg:
                vg["Subtitle"] = pad_coords(vg["Subtitle"])
            vg["coords"] = pad_coords(vg["coords"])
            
            # Iterate through each Knowledge Group (KG) within the VG
            for kg_key in vg:
                if kg_key.startswith("KG"):
                    kg = vg[kg_key]
                    # Pad all elements within the KG
                    kg["coords"] = pad_coords(kg["coords"])
                    kg["Highlight"] = pad_coords(kg["Highlight"])
                    kg["Icon"] = pad_coords(kg["Icon"])
                    kg["Vis"] = pad_coords(kg["Vis"])
                    kg["Text"] = pad_coords(kg["Text"])
    
    return padded_layout
