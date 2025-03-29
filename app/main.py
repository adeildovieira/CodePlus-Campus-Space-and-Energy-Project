from typing import Union

from fastapi import FastAPI, File, UploadFile

import os
import datetime
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from create_heatmap_bostock import *

app = FastAPI()

#save csv files
UPLOAD_DIR = "/csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/uptime")
def return_uptime():
    awake_since = os.popen('uptime -p').read()
    right_now = datetime.datetime.now()
    return {"server_uptime": awake_since,
            "current_timestamp": right_now}



@app.post("/upload/csv/{filename}")
async def upload_csv(filename: str, file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"info": f"File '{filename}' uploaded successfully"}


from create_heatmap_bostock import create_heatmap

@app.get("/generate-heatmap/{date}/{time}")
def generate_heatmap(date: str, time: str):
    heatmap_path = create_heatmap(date, time)
    heatmap_filename = os.path.basename(heatmap_path)
    return {"message": f"Heatmap generated for {date} at time {time}", "heatmap_path": heatmap_path}
