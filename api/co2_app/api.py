import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class CO2Reading(Base):
    __tablename__ = "co2_readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    room = Column(String, index=True)
    co2 = Column(Integer)

Base.metadata.create_all(bind=engine)

class CO2Data(BaseModel):
    timestamp: datetime
    room: str
    co2: int

@app.post("/co2_data/")
async def create_co2_data(data: CO2Data):
    db = SessionLocal()
    try:
        db_reading = CO2Reading(**data.dict())
        db.add(db_reading)
        db.commit()
        db.refresh(db_reading)
        return {"message": "Data saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving data: {str(e)}")
    finally:
        db.close()

@app.get("/co2_data/")
async def get_co2_data(limit: int = 10):
    db = SessionLocal()
    try:
        results = db.query(CO2Reading).limit(limit).all()
        return [{"id": r.id, "timestamp": r.timestamp, "room": r.room, "co2": r.co2} for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="vcm-41372.vm.duke.edu", port=8000)
