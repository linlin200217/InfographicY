import os
import uuid
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from openai import OpenAI
from pdf_parser import ParserResult, PdfParser
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

print(os.getenv("OPENAI_KEY"))
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
    if file.filename and not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")


    new_filename = f"{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    client = OpenAI(
    api_key=os.getenv("OPENAI_KEY")
    )
    pdf_parser = PdfParser(file_path, question, client)
    return pdf_parser.run()



'''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9029)
'''