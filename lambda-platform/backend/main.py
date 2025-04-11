from fastapi import FastAPI, UploadFile, File, Form, Depends # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from backend.docker_runner import run_function_in_docker  # type: ignore
from backend.db import SessionLocal, Function, init_db # type: ignore
import os

# Initialize FastAPI app
app = FastAPI()

# Initialize DB on startup
init_db()

# Enable CORS (optional but useful for frontend integrations)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------- CRUD Endpoints for Metadata -----------

@app.post("/functions/")
async def create_function(
    name: str = Form(...),
    route: str = Form(...),
    language: str = Form(...),
    timeout: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filepath = f"functions/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(await file.read())

    func = Function(name=name, route=route, language=language, timeout=timeout, file_path=filepath)
    db.add(func)
    db.commit()
    db.refresh(func)
    return func

@app.get("/functions/")
def list_functions(db: Session = Depends(get_db)):
    return db.query(Function).all()

@app.get("/functions/{id}")
def get_function(id: int, db: Session = Depends(get_db)):
    return db.query(Function).filter(Function.id == id).first()

@app.put("/functions/{id}")
def update_function(id: int, name: str, timeout: int, db: Session = Depends(get_db)):
    func = db.query(Function).filter(Function.id == id).first()
    if func:
        func.name = name
        func.timeout = timeout
        db.commit()
        db.refresh(func)
    return func

@app.delete("/functions/{id}")
def delete_function(id: int, db: Session = Depends(get_db)):
    func = db.query(Function).filter(Function.id == id).first()
    if func:
        db.delete(func)
        db.commit()
        return {"message": "Function deleted"}
    return {"message": "Not found"}

# ----------- Function Execution Endpoint -----------

@app.post("/run-function/")
async def run_function(file: UploadFile, language: str = Form(...), timeout: int = Form(5)):
    os.makedirs("functions", exist_ok=True)
    filepath = f"functions/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(await file.read())

    output = run_function_in_docker(filepath, language, timeout)
    return {"output": output}
