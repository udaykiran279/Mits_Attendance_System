from flask import Flask,render_template,redirect,request,Response,make_response,url_for,session,jsonify
import cv2
import os
import json
from datetime import datetime
import requests
import numpy as np
from PIL import Image
from pathlib import Path
from facetools import FaceDetection, LivenessDetection
import pandas as pd
import pyrebase
from pathlib import Path
import pickle
import base64
import time
import io


app=Flask(__name__)

df=pd.read_csv("class-merge.csv")
model=pickle.load(open("model.pkl","rb"))
config={
    "apiKey": "AIzaSyAYey8JOEz4XrP_kZTFV0KSwIU9QK8FmCo",
  "authDomain": "mits-students-data.firebaseapp.com",
  "projectId": "mits-students-data",
  "databaseURL":"https://mits-students-data-default-rtdb.firebaseio.com/",
  "storageBucket": "mits-students-data.appspot.com",
  "messagingSenderId": "25326053045",
  "appId": "1:25326053045:web:2416e76031cbf2a78bc0fc",
  "measurementId": "G-8Q4Q08D5T5"
}
firebase=pyrebase.initialize_app(config)
database=firebase.database()
storage=firebase.storage()
firebaseConfig1={
  'apiKey': "AIzaSyBWW3MflR1E_duhKdz-6TD5PQnp6YQmWz0",
  'authDomain': "staff-details-495df.firebaseapp.com",
  'projectId': "staff-details-495df",
  'storageBucket': "staff-details-495df.appspot.com",
  'messagingSenderId': "750490829584",
  'appId': "1:750490829584:web:b85fc2a3c27200cf98db95",
  'measurementId': "G-W4V7K08HL8",
  'databaseURL':""
}
firebase1=pyrebase.initialize_app(firebaseConfig1)
auth1=firebase1.auth()


l=[]
roll=[]
year=[]
depa=[]
lat=[]
lon=[]
roomno=[]
status=[]
filename=[]
root = Path(os.path.abspath(__file__)).parent.absolute()
data_folder = root / "data"

#resNet_checkpoint_path = data_folder / "checkpoints" / "InceptionResnetV1_vggface2.onnx"
facebank_path = data_folder / "reynolds.csv"

deepPix_checkpoint_path = data_folder / "checkpoints" / "OULU_Protocol_2_model_0_0.onnx"

faceDetector = FaceDetection(max_num_faces=1)
livenessDetector = LivenessDetection(checkpoint_path=deepPix_checkpoint_path.as_posix())

@app.route("/")

def homepage():
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/std")
def std():
    return render_template("student.html")
@app.route("/ssup")
def ssup():
    return render_template("stdsignup.html")

@app.route("/capture",methods=["POST","GET"])
def capture():
    captured_image = request.form['image']
    roll_no=request.form.get('rollno').upper()
    year=request.form.get('year')
    dept=request.form.get('dept').upper()
    '''if year=="1":
        std_data=database.child("First").child(dept).child(roll_no).get()
    elif year=="2":
        std_data=database.child("Second").child(dept).child(roll_no).get()
    elif year=="3":
        std_data=database.child("Third").child(dept).child(roll_no).get()
    elif year=="4":
        std_data=database.child("Four").child(dept).child(roll_no).get()
    if std_data.val()['Room']=="":
            return render_template("student.html",msg="No Class Scheduled Yet.")'''

    encoded_data = captured_image.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img1= cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cap_path=f'retrieve_images/cap.jpg'
    cv2.imwrite(cap_path, img1)
    #roll_no pic to retrieve
    storage.child(f'{roll_no}.jpg').download('',f'{roll_no}.jpg')
    img2=cv2.imread(f'{roll_no}.jpg')
    image1= Image.open(cap_path)
    image2=Image.open(f'{roll_no}.jpg')
    image_bytes = io.BytesIO()
    image1.save(image_bytes, format='JPEG')
    image_bytes = image_bytes.getvalue()
    image_bytes2= io.BytesIO()
    image2.save(image_bytes2, format='JPEG')
    image_bytes2= image_bytes2.getvalue()
    faces, boxes = faceDetector(img1)

    for face_arr, box in zip(faces, boxes):
        #min_sim_score, mean_sim_score = identityChecker(face_arr)
        liveness_score = livenessDetector(face_arr)
        if liveness_score>0.65:
            print("real")
            #result = DeepFace.verify(cap_path,f'{rr_roll}.jpg',model_name='Facenet', distance_metric='euclidean_l2')
            payload = {
            'image1': image_bytes,
            'image2': image_bytes2
            }

    # Make a POST request to the DeepFace API on PythonAnywhere
            deepface_api_url = 'https://udaykirannaidu.pythonanywhere.com/compare'  # Replace with your DeepFace API endpoint URL on PythonAnywhere
            response = requests.post(deepface_api_url, files=payload)
            result = response.json()
            os.remove(cap_path)
            os.remove(f'{roll_no}.jpg')
            if result=='True':

                #d={'20691a3157':['3','AI']}

                #return render_template('studentform.html',roll=roll,year=d[roll][0],dep=d[roll][1],rmn='216')
                return "same"
            else:
                return "Different"
        else:
            os.remove(cap_path)
            os.remove(f'{roll_no}.jpg')
            return render_template("index.html",msg="Fake...Don't Cheat us 😄")
    
        
@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/faculty")
def faculty():
    return render_template("faculty.html")


@app.route("/stdsignup",methods=["POST"])
def stdsignup():
    roll=request.form['rollno'].upper()
    year=request.form['year']
    dept=request.form['dept'].upper()
    file=request.files['face_pic']
    data={'Roll':roll,'Year':year,'Department':dept,'Room':'','status':''}
    if year=='1':
        database.child("First").child(dept).child(roll).set(data)
    elif year=='2':
        database.child("Second").child(dept).child(roll).set(data)
    elif year=='3':
        database.child("Third").child(dept).child(roll).set(data)
    elif year=='4':
        database.child("Four").child(dept).child(roll).set(data)
    image = Image.open(file)
    save_path = "upload_images/"+f'{roll}.jpg'
    image.save(save_path)
    storage.child(f'{roll}.jpg').put(save_path)
    os.remove(save_path)

    return render_template("student.html",msg="Uploaded Successfully.Log Back to your Account")

    '''k=[i for i in request.form.values()]
    email=k[0].lower()
    password=k[1]
    try:
        auth.create_user_with_email_and_password(email,password)
        return render_template("student.html")
    except:
        return render_template("student.html",msg="Email Already Exists")'''
@app.route("/facsignup",methods=["POST","GET"])
def facsignup():
    k=[i for i in request.form.values()]
    email=k[0].lower()
    password=k[1]
    try:
        auth1.create_user_with_email_and_password(email,password)
        return render_template("faculty.html")
    except:
        return render_template("faculty.html",msg="Email Already Exists")

@app.route("/facsignin",methods=["POST","GET"])
def facsignin():
    fval=[i for i in request.form.values()]
    email=fval[0].lower()
    password=fval[1]
    try:
        auth1.sign_in_with_email_and_password(email,password)
    except:
        return render_template("faculty.html",msg="Invalid User or Incorrect Password")
    return render_template("facultyform.html")

@app.route("/create",methods=["POST","GET"])
def create():
    val=[i for i in request.form.values()]
    print(val)
    for i in val:
        l.append(i)
    remsg="Class Room Scheduled"
    return render_template("facultyform.html",remsg=remsg)

@app.route("/studentform",methods=["POST","GET"])

def studentform():
    '''sval=[i for i in request.form.values()]
    email=sval[0].lower()
    password=sval[1]
    k=l
    if len(k)==0:
        return render_template("student.html",msg="No Class Scheduled Yet")
    course=k[1]
    rmn=k[-1]
    roomno.append(rmn)
    try:
        auth.sign_in_with_email_and_password(email,password)
    except:
        return render_template("student.html",msg="Invalid User or Incorrect Password")
        
    
    return render_template("studentform.html",rm=rmn,course="Attendance for {} class".format(course))'''

@app.route("/predict",methods=["POST","GET"])

def predict():
    vals=[i for i in request.form.values()]
    print(vals)
    roll.append(vals[0])
    year.append(vals[1])
    depa.append(vals[2])
    room=int(vals[3])
    lat.append(vals[-2])
    lon.append(vals[-1])
    l1=float(str(vals[-2])[0:10])
    lo1=float(str(vals[-1])[0:10])
    mark=model.predict([[l1,lo1,room],])[0]
    print(mark)
    if mark==0:
        marked="Absent"
        status.append(marked)
    else:
        marked="Present"
        status.append(marked)
    print(status)
    return render_template("studentform.html",attend="Your attendence marked as: "+marked)

@app.route("/download",methods=["POST","GET"])

def download():
    df1=pd.DataFrame({"ROLL_NO":roll,"Year":year,"Department":depa,"status":status,"Room_no":roomno})
    if df1.shape[0]==0:
        return render_template("facultyform.html",msg="No Presenters Yet")
    resp=make_response(df1.to_csv(index=False))
    resp.headers["Content-Disposition"]="attachement;filename=attend_sheet.csv"
    resp.headers["Content-Type"]="text/csv"
    lat.clear()
    lon.clear()
    year.clear()
    depa.clear()
    roll.clear()
    l.clear()
    status.clear()
    return resp
if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')
