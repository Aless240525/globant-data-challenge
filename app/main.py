from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/load/{table_name}")
def load_table(table_name: str, db: Session = Depends(get_db)):
    table_map = {
        "departments": (models.Department, "data/departments.csv"),
        "jobs": (models.Job, "data/jobs.csv"),
        "employees": (models.Employee, "data/employees.csv"),
    }
    if table_name in table_map:
        model, path = table_map[table_name]
        crud.load_csv_to_db(path, model, db)
        return {"message": f"{table_name} loaded successfully"}
    return {"error": "Invalid table name"}
