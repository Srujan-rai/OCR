from flask import Flask,redirect,render_template,request,Response,jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import mimetypes
from dotenv import load_dotenv
import google.generativeai as genai


app=Flask(__name__)

API_KEY =os.getenv("API_KEY")

genai.configure(api_key=API_KEY)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}


saved_file_path='uploads'



if not os.path.exists(saved_file_path):
    os.makedirs(saved_file_path,exist_ok=True)
    
    
    
def process_image(file_path):
    img=Image.open(file_path)
    
    
    text=pytesseract.image_to_string(img,lang='eng')
    print(text)
    return text
    

@app.route('/')
def home():
    return render_template('home.html',message="")
    
@app.route('/process',methods=['POST','GET'])
def process():
    if 'file' not in request.files:
        return "file not found"
    
    file=request.files['file']
    
    
    if file.filename=='':
        return render_template('home.html',message=None)
    
    else:
        file=request.files['file']
        file_path=os.path.join(saved_file_path,secure_filename(file.filename))
        file.save(file_path)
        mime_type,_=mimetypes.guess_type(file_path)
        if mime_type in ['image/png', 'image/jpeg']:
            message=process_image(file_path)

        
        elif mime_type == 'application/pdf':
            message="uploaded is pdf"

        
        
        os.remove(file_path)
        
        return jsonify({"message":message})
  
@app.route('/chat',methods=['POST','GET'])
def chat():
    if request.method=='POST':
        query=request.form['query']
        print(query)
        
    return render_template("home.html",message=query)
        
        
        



if __name__=="__main__":
    app.run(debug=True,host='0.0.0.0')