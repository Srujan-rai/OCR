from flask import Flask,redirect,render_template,request,Response,jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import mimetypes
from dotenv import load_dotenv
import google.generativeai as genai
import easyocr
from pdf2image import convert_from_path
import easyocr
import io
import tempfile

load_dotenv()

global message
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

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)
chat_session = model.start_chat(history=[])

saved_file_path='uploads'



if not os.path.exists(saved_file_path):
    os.makedirs(saved_file_path,exist_ok=True)
    





def gemini_api(query):
    response = chat_session.send_message(f"{query}")

    text_parts = []
    candidates = response.candidates
    
    for candidate in candidates:
        content = candidate.content
        
        for part in content.parts:
            text = part.text
            cleaned_text = text.replace('\n', ' ').replace('[', '').replace(']', '').replace('**', '').strip('"')
            text_parts.append(cleaned_text)
    
    return ' '.join(text_parts)
    
def process_image(file_path):
    text=[]
    reader=easyocr.Reader(['en'])
    results=reader.readtext(file_path)
    

    for result in results:
        print(result[1])
        text.append(result[1]) 
        
    extracted_text= ' ,'.join(text)
    print(extracted_text)      

    reponse=gemini_api(f'this text is taken from an image and i will be asking some questions on thsi text . the text is:{extracted_text}')
    print(reponse)
    return extracted_text
    

@app.route('/')
def home():
    return render_template('home.html',message="")
    
@app.route('/process',methods=['POST','GET'])
def process():
    if 'file' not in request.files:
        return "file not found"
    
    file=request.files['file']
    
    
    if file.filename=='':
        return jsonify({"message":"choose the file and then submit"})
    
    else:
        file=request.files['file']
        file_path=os.path.join(saved_file_path,secure_filename(file.filename))
        file.save(file_path)
        mime_type,_=mimetypes.guess_type(file_path)
        
        if mime_type in ['image/png', 'image/jpeg']:
            message=process_image(file_path)

        
        elif mime_type == 'application/pdf':
            images = convert_from_path(file_path)
            reader = easyocr.Reader(['en'])

            text = []
            for i, image in enumerate(images):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file_path = temp_file.name
                    image.save(temp_file_path, format='PNG')

                    result = reader.readtext(temp_file_path)
                    text.extend([res[1] for res in result])
                    print(f"Page {i + 1}: {text}")
                    reponse=gemini_api(f'this text is taken from an image and i will be asking some questions on thsi text . the text is:{text}')
                    print(reponse)

                    os.remove(temp_file_path)   

            message = " ".join(text)
        
        
        os.remove(file_path)
        print(message)
        
        return jsonify({"message":message})
  
@app.route('/chat',methods=['POST','GET'])
def chat():
    if request.method=='POST':
        if request.form['query']!= '':
            query=request.form['query']
            print(query)
            text=gemini_api(query)
            print(text)
   
        
            return jsonify({'reply':text})
        
        
            
        
        
        
        



if __name__=="__main__":
    app.run(debug=True,host='0.0.0.0',port=5000)