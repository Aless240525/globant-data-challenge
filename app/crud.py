import pandas as pd
from sqlalchemy.orm import Session
from app import models

def load_csv_to_db(csv_path, model, db: Session):
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        db.add(model(**row.to_dict()))
    db.commit()
