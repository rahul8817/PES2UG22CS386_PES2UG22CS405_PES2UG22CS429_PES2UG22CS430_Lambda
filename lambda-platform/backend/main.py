from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from backend.docker_runner import run_function_in_docker
import os

app = FastAPI()

# Optional: Allow frontend/other tools to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload and run function endpoint
@app.post("/run-function/")
async def run_function(file: UploadFile, language: str = Form(...), timeout: int = Form(5)):
    os.makedirs("functions", exist_ok=True)
    filepath = f"functions/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(await file.read())

    output = run_function_in_docker(filepath, language, timeout)
    return {"output": output}

