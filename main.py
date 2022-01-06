from typing import Optional
from pydantic import BaseModel
from motor.motor_tornado import MotorCollection
import uvicorn
from database.engine import engine
from fastapi import FastAPI
from odmantic import Model

app = FastAPI()

class Test(Model):
    key: str

class Test2(BaseModel):
    key: str

a = Test()

@app.get("/")
async def root():
    doc = Test()
    doc_id = await engine.save(doc)
    return {"message": doc_id.id}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")