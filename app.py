import face_recognition
import numpy as np
import mysql.connector
from fastapi import FastAPI, UploadFile, File
from datetime import date
from PIL import Image
import io

app = FastAPI()

db = mysql.connector.connect(
    host="localhost",
    user="u257771616_main",
    password="Kiet@2001",
    database="u257771616_main"
)

def get_known_faces():
    cur = db.cursor()
    cur.execute("SELECT htno, face_encoding FROM student_faces")
    rows = cur.fetchall()
    encodings=[]
    labels=[]
    for htno,blob in rows:
        encodings.append(np.frombuffer(blob,dtype=np.float64))
        labels.append(htno)
    return encodings,labels

@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    img_bytes = await file.read()
    img = Image.open(io.BytesIO(img_bytes))
    img = np.array(img)

    faces = face_recognition.face_encodings(img)
    if len(faces)==0:
        return {"status":"no_face"}

    known,labels = get_known_faces()
    matches = face_recognition.compare_faces(known,faces[0],tolerance=0.5)

    if True in matches:
        idx = matches.index(True)
        htno = labels[idx]

        cur = db.cursor()
        today = date.today()

        cur.execute("""
            INSERT IGNORE INTO attendance
            (htno,classid,att_date,status,ph_no)
            SELECT htno,classid,%s,'Present',student_phone
            FROM students
            WHERE htno=%s
        """,(today,htno))
        db.commit()

        return {"status":"marked","htno":htno}

    return {"status":"unknown"}
