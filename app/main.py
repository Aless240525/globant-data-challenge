from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, crud
from sqlalchemy import text

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

from sqlalchemy import text

@app.get("/metrics/hired-by-quarter")
def hired_by_quarter(db: Session = Depends(get_db)):
    query = text("""
        SELECT
            d.name AS department,
            j.title AS job,
            SUM(CASE WHEN strftime('%m', e.datetime) BETWEEN '01' AND '03' THEN 1 ELSE 0 END) AS Q1,
            SUM(CASE WHEN strftime('%m', e.datetime) BETWEEN '04' AND '06' THEN 1 ELSE 0 END) AS Q2,
            SUM(CASE WHEN strftime('%m', e.datetime) BETWEEN '07' AND '09' THEN 1 ELSE 0 END) AS Q3,
            SUM(CASE WHEN strftime('%m', e.datetime) BETWEEN '10' AND '12' THEN 1 ELSE 0 END) AS Q4
        FROM employees e
        JOIN jobs j ON e.job_id = j.id
        JOIN departments d ON e.department_id = d.id
        WHERE strftime('%Y', e.datetime) = '2021'
        GROUP BY d.name, j.title
        ORDER BY d.name, j.title
    """)
    result = db.execute(query).fetchall()
    return [dict(r) for r in result]

@app.get("/metrics/departments-above-average")
def departments_above_average(db: Session = Depends(get_db)):
    query = text("""
        WITH dept_hires AS (
            SELECT
                d.id,
                d.name AS department,
                COUNT(*) AS hired
            FROM employees e
            JOIN departments d ON e.department_id = d.id
            WHERE strftime('%Y', e.datetime) = '2021'
            GROUP BY d.id, d.name
        ),
        avg_hires AS (
            SELECT AVG(hired) AS avg_hired FROM dept_hires
        )
        SELECT *
        FROM dept_hires
        WHERE hired > (SELECT avg_hired FROM avg_hires)
        ORDER BY hired DESC
    """)
    result = db.execute(query).fetchall()
    return [dict(r) for r in result]
