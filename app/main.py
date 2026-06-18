from fastapi import FastAPI, UploadFile, File
from app.extractor import extract_text
from app.image_extractor import extract_images
from app.gemini_service import normalize_document
from fastapi.staticfiles import StaticFiles
from app.cleanup import cleanup_old_uploads
from fastapi.middleware.cors import CORSMiddleware

import shutil
import os
import uuid

session_id = str(
    uuid.uuid4()
)

session_folder = os.path.join(
    "uploads",
    session_id
)

os.makedirs(
    session_folder,
    exist_ok=True
)

app = FastAPI()
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
BASE_URL = "https://standarpdf.onrender.com"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)



@app.get("/")
def root():
    return {
        "status": "ok"
    }

@app.post("/extract")
async def extract_pdf(
    file: UploadFile = File(...)
):
    
    cleanup_old_uploads()

    pdf_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    text_pages = extract_text(pdf_path)

    images = extract_images(
        pdf_path,
        session_folder
    )

    formatted_images = []

    for image in images:
        formatted_images.append({

            "id": image["id"],

            "page": image["page"],

            "url":
                f"{BASE_URL}/uploads/"
                f"{session_id}/"
                f"{image['filename']}"
        })

    return {
        "metadata": {
            "filename": file.filename,
            "totalPages": len(text_pages)
        },
        "text": text_pages,
        "assets": formatted_images
    }

@app.post("/normalize")
async def normalize(
    payload: dict
):

    result = normalize_document(
        payload
    )

    return result
