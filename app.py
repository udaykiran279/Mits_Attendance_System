from flask import Flask,render_template,redirect,request,Response,make_response,url_for,session,jsonify
import cv2
import os
import json
import urllib.request
from datetime import datetime
import requests
import numpy as np
from PIL import Image
from pathlib import Path
import pandas as pd
from io import StringIO
import pyrebase
import base64
import time
import io
from sklearn.neighbors import KNeighborsClassifier


app=Flask(__name__)

app.secret_key='udaykiranchowdary2002'
df=pd.read_csv("class-merge.csv")

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
@app.route("/fac_form")
def fac_form():
    return render_template("facultyform.html")

@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/faculty")
def faculty():
    return render_template("faculty.html")

#student routes
@app.route("/stdsignup",methods=["POST"])
def stdsignup():
    roll=request.form['rollno'].upper()
    year=request.form['year']
    dept=request.form['dept'].upper()
    file=request.files['face_pic']
    data={'Roll':roll,'Year':year,'Department':dept,'faculty_id':'','Room':'','course':'','status':'Absent'}
    d={"1":"First","2":"Second","3":"Third","4":"Fourth"}
    #check=database.child(d[year]).child(dept).child(roll).get()
    #if check is not None:
        #return render_template("stdsignup.html",msg=f"{roll} Data Exist.")
    database.child(d[year]).child(dept).child(roll).set(data)
    image = Image.open(file)
    save_path = "upload_images/"+f'{roll}.jpg'
    image.save(save_path)
    storage.child(f'{roll}.jpg').put(save_path)
    os.remove(save_path)

    return render_template("student.html",msg="Uploaded Successfully.Log Back to your Account")


@app.route("/capture",methods=["POST","GET"])
def capture():
    captured_image = request.form['image']
    roll_no=request.form.get('rollno').upper()
    year=request.form.get('year')
    dept=request.form.get('dept').upper()
    d={"1":"First","2":"Second","3":"Third","4":"Fourth"}
    std_data=database.child(d[year]).child(dept).child(roll_no).get()
    if std_data.val() is None:
        return render_template("index.html",msg="Check You Credentials correctly")
    if std_data.val()['Room']=="":
        return render_template("student.html",msg="No Class Scheduled Yet.")

    encoded_data = captured_image.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img1= cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image1= Image.fromarray(img1)
    image_bytes = io.BytesIO()
    image1.save(image_bytes, format="JPEG")
    image_bytes = image_bytes.getvalue()
    roll_path=storage.child(f"{roll_no}.jpg").get_url(None)
    response = requests.get(roll_path)
    image_bytes2= response.content
    
    url = "http://bunny2003.pythonanywhere.com/liveness"

    # Request payload (assuming you are sending the base64 string as JSON)
    payload = {
        "image":image_bytes
    }

    # Make the POST request to the API
    response = requests.post(url, files=payload)
    result=response.json()
    if result=="Real":
        payload = {
            'image1': image_bytes,
            'image2': image_bytes2
        }
    
        # Make a POST request to the DeepFace API on PythonAnywhere
        deepface_api_url = 'https://udaykirannaidu.pythonanywhere.com/compare'  # Replace with your DeepFace API endpoint URL on PythonAnywhere
        response = requests.post(deepface_api_url, files=payload)
        result = response.json()
        if result=='True':
            att_data=database.child(d[year]).child(dept).child(roll_no).get()
            dv=dict(att_data.val())
            return render_template('studentform.html',roll=roll_no,year=year,dep=dept,rmn=dv['Room'],course=dv['course'])
        else:
            return render_template("index.html",msg=f"Identity did not match with {roll_no} 😄")
    elif result=="Fake":
        return render_template("index.html",msg="Don't Cheat Us 😄")
    else:
        return render_template("index.html",msg="Retry capturing your face Clearly.")


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
    fac_id=request.form.get('facid').upper()
    course=request.form.get('course').upper()
    room=request.form.get('rmn')
    year=request.form.get('year')
    dept=request.form.get('dept').upper()
    std_data=database.child(year).child(dept).get()
    std_val=std_data.val()
    for i in std_val:
        database.child(year).child(dept).child(i).update({'faculty_id':fac_id,'Room':room,'course':course})
    
    return render_template("facultyform.html",remsg="Class Room Scheduled")



@app.route("/predict",methods=["POST","GET"])

def predict():
    roll=request.form.get('roll')
    year=request.form.get('year')
    dept=request.form.get('deptart')
    cour=request.form.get('course')
    room_no=int(request.form.get('roomno'))
    lat=float(request.form.get('lat'))
    lon=float(request.form.get('lon'))
    d={"1":"First","2":"Second","3":"Third","4":"Fourth"}
    x=df.drop("place",axis=1)
    y=df.place
    knn = KNeighborsClassifier(n_neighbors=19,metric='euclidean')
    knn.fit(x,y)
    mark=knn.predict([[lat,lon,room_no],])[0]
    if mark==1:
        database.child(d[year]).child(dept).child(roll).update({'status':'Present'})
        return render_template("studentform.html",attend="Your attendence marked as: Present")
    else:
        database.child(d[year]).child(dept).child(roll).update({'status':'Absent'})
        return render_template("studentform.html",attend="Your attendence marked as: Absent")

@app.route("/view_attend")
def view_attend():
    return render_template("fac_down.html")

@app.route("/download",methods=["POST","GET"])

def download():
    fac_id=request.form.get('facid').upper()
    year=request.form.get('year')
    dept=request.form.get('dept').upper()
    sheet=request.form.get('sheet')
    date=request.form.get('selectedDate')
    d={'First':'I','Second':'II','Third':'III','Fourth':'IV'}
    if sheet=="Download previous Classes":
        url=storage.child("vamsi").child("data.csv").get_url(None)
        try:
            # Fetch the dataset from the URL using urllib
            with urllib.request.urlopen(url) as response:
                data = response.read().decode("utf-8")
            # Convert the fetched data to a DataFrame using pandas
            df = pd.read_csv(StringIO(data))
            #print(df.shape)
            resp=make_response(df1.to_csv(index=False))
            resp.headers["Content-Disposition"]=f"attachement;filename={dept}-{d[year]}-{date}.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
        except Exception as e:
            return render_template("fac_down.html",msg=f"No class Scheduled on {date}")
    else:

        data_list=[]
        std_data=database.child(year).child(dept).get()
        std_val=std_data.val()
        for i in std_val:
            dd=database.child(year).child(dept).child(i).get()
            dd_data=dict(dd.val())
            if dd_data['faculty_id']==fac_id:
                data_list.append(dd_data)
                database.child(year).child(dept).child(i).update({'faculty_id':"","Room":"","course":"","status":""})
        df1=pd.DataFrame(data_list)
        if df1.shape[0]==0:
            return render_template("facultyform.html",msg="No Presenters Yet or No Class Room Scheduled.")
        current_date = datetime.today().date()
        formatted_date = current_date.strftime("%d-%m-%Y")
        csv_file=f'{dept}-{d[year]}-{formatted_date}.csv'
        csv_path=f"upload_images/{csv_file}"
        df1.to_csv(csv_path,index=False)
        storage.child(fac_id).child(csv_file).put(csv_path)
        resp=make_response(df1.to_csv(index=False))
        resp.headers["Content-Disposition"]=f"attachement;filename={dept}-{d[year]}-{formatted_date}.csv"
        resp.headers["Content-Type"]="text/csv"
        return resp

if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')
