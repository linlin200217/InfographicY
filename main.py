import json
import os
import uuid
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from openai import OpenAI
from pdf_parser import ColorScheme, ParserResult, PdfParser
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from icon import scale_creation
from pydantic import BaseModel
import requests

from util import reorder_valentine_data
load_dotenv()

#print(os.getenv("OPENAI_KEY"))
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def hello():
    return "hello"

@app.post("/upload",response_model=ParserResult)
def upload_pdf(question: str = Form(...), file: UploadFile = File(...)):
    
    '''
     if file.filename and not file.filename.endswith(".pdf"):
         raise HTTPException(status_code=400, detail="Only PDF files are allowed")


     new_filename = f"{uuid.uuid4().hex}.pdf"
     file_path = os.path.join(UPLOAD_DIR, new_filename)

     with open(file_path, "wb") as f:
         f.write(file.file.read())

     client = OpenAI(
     api_key=os.getenv("OPENAI_KEY"),
     #base_url= os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
     )
     pdf_parser = PdfParser(file_path, question, client)
     return pdf_parser.run()
    
    '''    
     #先用假数据
    with open("result.json", "r",encoding="utf-8") as f:
        data = json.load(f)
    return data



class IconItem(BaseModel):
    keyword: str
    colorlist: list[list[int]]
    coordinates: list[list[float]]

@app.post("/icon")
def generate_icon(item:IconItem):
  color_controls = [{'rgb': rgb} for rgb in item.colorlist]
  client = OpenAI(
    base_url='https://external.api.recraft.ai/v1',
    api_key=os.getenv("RECRAFT_KEY"),
  )

  response = client.images.generate(
    model='recraftv2',
    prompt=item.keyword,
    style='icon',
    n=1,
    size= scale_creation(item.coordinates),
    extra_body={
        'controls': {
            'colors': color_controls
        }
      }
    )

  # 获取返回的 SVG URL
  svg_url = response.data[0].url

  # 下载 SVG 文件内容
  svg_response = requests.get(svg_url)
  if svg_response.status_code == 200:
    # 将 SVG 内容保存到本地文件
      with open('output.svg', 'wb') as file:
        file.write(svg_response.content)
      print("SVG 文件已保存为 output.svg")
      return svg_response.content
  else:
      print("下载 SVG 失败，状态码：", svg_response.status_code)
      



@app.post("/color",response_model=ColorScheme)
def color(knowledgeContent: ParserResult,infographic_size:tuple[int, int]|None=None):
    client = OpenAI(
    api_key=os.getenv("OPENAI_KEY"),
    #base_url= os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    )
    knowledge_content =PdfParser.extract_knowledge_from_parser_result(knowledgeContent)
    return PdfParser.generate_colors(knowledge_content, client)

@app.post("/rank",response_model=list[str])
def rank(parser_result: ParserResult, infographic_size: tuple[int, int]):
    return PdfParser.rank(parser_result, infographic_size)



def layout_poster(type:str,valentine_data:dict, W, H, margin=0, vertical_margin=0):
    if type == "portrait" or type == "Portrait":
        from portrait import layout_poster
        return layout_poster(valentine_data, W, H, margin, vertical_margin)
    elif type == "landscape" or type == "Landscape":
        from landscape import layout_poster
        return layout_poster(valentine_data, W, H, margin, vertical_margin)
    elif type == "grid" or type == "Grid":
        from grid import layout_poster
        return layout_poster(valentine_data, W, H, margin, vertical_margin)
    elif type == "grid_protrait" or type == "PortraitGrid":
        from grid_protrait import layout_poster
        return layout_poster(valentine_data, W, H, margin, vertical_margin)
    elif type == "star" or type == "Star":
        from star import layout_poster
        return layout_poster(valentine_data, W, H, margin, vertical_margin)
    else:
        raise ValueError("Invalid type")
    
@app.post("/layout",response_model=dict)
def layout(type:str,infographic_size: tuple[int, int],parser_result:dict):
    return layout_poster(type,parser_result,infographic_size[0], infographic_size[1],margin=0, vertical_margin=0)

@app.post("/submit")
def submit(type:str,layout:dict,parser_result:dict):
    from pprint import pprint
    print(type)
    pprint(layout)
    pprint(parser_result)
    return "ok"
    #new_parser_result = reorder_valentine_data(parser_result)
    #new_layout = layout_poster(type,new_parser_result,infographic_size[0], infographic_size[1],margin=0, vertical_margin=0)
    #return {
        #"new_paser_result": new_parser_result ,
        #"new_layout": new_layout
    #}
'''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9029)
'''