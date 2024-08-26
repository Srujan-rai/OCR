from flask import Flask,redirect,render_template,request,Response,jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract


app=Flask(__name__)

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
        print("srujan")
        file=request.files['file']
        file_path=os.path.join(saved_file_path,secure_filename(file.filename))
        file.save(file_path)
        
        message=process_image(file_path)
        
        os.remove(file_path)
        
        return jsonify({"message":message})
    
        
        
        



if __name__=="__main__":
    app.run(debug=True,host='0.0.0.0')