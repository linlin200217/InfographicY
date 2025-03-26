import json
import os
import uuid
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from openai import OpenAI
from pdf_parser import ColorScheme, ParserResult, PdfParser
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
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

'''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9029)
'''