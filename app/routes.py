import io
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_triangle import Triangle
from flask_uploads import UploadSet, configure_uploads 
# add to import line above PDFs and remove IMAGES
from app import app
from app.forms import ViewForm
from PIL import Image
import pytesseract
from wand.image import Image as wi
import os
from uuid import uuid4

@app.route('/')
@app.route('/index')
def index():
    corpus = {'corpusname': 'Sample Corpus'}
    documents = [
    {
        'docID': {'docname': 'Sample1'},
        'body': 'This is sample text'
    },
    {
        'docID': {'docname': 'Sample2'},
        'body': 'Another sample text'
    }
    ]
    docimage = '/static/doge.jpeg'

    return render_template('index.html', title='home', corpus=corpus, documents=documents, docimage=docimage)

@app.route('/angular', methods=['GET', 'POST'])
def angular():
    return render_template('angular.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    pdfs = UploadSet('pdfs', ['pdf'])
    app.config['UPLOADED_PDFS_DEST'] = 'app/static/img'
    configure_uploads(app, pdfs)
    if request.method == 'POST' and 'photo' in request.files:
        filename = pdfs.save(request.files['photo']) 
        return filename 
    return render_template('upload.html')

def make_tree(path):
    tree = dict(name=path, children=[])
    try: lst= os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=fn[4:]))
    #tree['children'] ={k: v[4:] for k, v in tree.items()}
    return tree  

@app.route('/complete', methods=['GET', 'POST'])
def complete():
    path = os.path.expanduser(u'~')
    #return render_template('complete.html', tree=make_tree("/home/dan/PDFOCR/app/static/img"))
    return render_template('complete.html', tree=make_tree("app/static/img"))

@app.route('/OCR_All', methods=['GET', 'POST'])
def OCR_All():
    if request.method == 'POST':
        def ocr(file_to_ocr):
            im = Image.open(file_to_ocr)
            txt = pytesseract.image_to_string(im, lang='eng')
            return txt
           
        def pdfOCR(pdf_to_ocr):
            #function to OCR pdfs one by one
            PDF = pdf_to_ocr 
            #convertPDF= wi(filename =PDF, resolution = 300)
            #pdfImage = convertPDF.convert('jpeg')
            return PDF

        directory = os.path.join("app/static/img")
        for root,dirs,files in os.walk(directory):
            for file in files:
                if file.endswith(".pdf"):
                    pre_fix=file[:-4]
                    text=pdfOCR("./app/static/img/" + file)
                    with open(directory+"//"+pre_fix+".txt", 'w') as f: f.write(str(text)) 
                if file.endswith(".png"):
                    pre_fix=file[:-4]
                    txt=ocr("./app/static/img/"+file)
                    with open(directory+"//"+pre_fix+".txt", 'w') as f: f.write(str(txt)) 
    #find a way to add this line to the code on the line above so you don't ocr completed files
    #if os.path.isfile(directory+"//"+pre_fix+".txt")==False: 
                            
    #if request.method == 'POST':
    #    pass
    return(render_template("OCR_all.html"))

@app.route('/view', methods=['GET', 'POST'] )
#Commented out code to display a jpeg is still in this function.
def view():
    form = ViewForm()
    #docimage = '/static/Irregularis_sampletext.png'
    #im = Image.open('app/static/Irregularis_sampletext.png')
    #text = pytesseract.image_to_string(im, lang = 'eng')
    PDF = '/static/Bostrom.pdf'
    convertPDF= wi(filename ='app/static/Bostrom.pdf', resolution = 300)
    pdfImage = convertPDF.convert('jpeg')

    imageBlobs = []
    
    for img in pdfImage.sequence:
        imgPage = wi(image = img)
        imageBlobs.append(imgPage.make_blob('jpeg'))

    recognized_text = []

    for imgBlob in imageBlobs:
        im = Image.open(io.BytesIO(imgBlob))
        text = pytesseract.image_to_string(im, lang = 'eng')
        outputName=PDF[:-4]
        outputName=outputName[8:]
        testvar = './app/static/txts/'+outputName+ '.txt'
        recognized_text.append(text)
        with open(testvar, 'w') as f: f.write(str(recognized_text))
        #with open('./app/static/txts/output2.txt', 'w') as f: f.write(str(recognized_text))
    return render_template('view.html', title='View', form=form, text=text, PDF=PDF, recText=recognized_text)


