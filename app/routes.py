import io
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_triangle import Triangle
from flask_uploads import UploadSet, configure_uploads 
# add to import line above PDFs and remove IMAGES
from app import app, db
from app.forms import ViewForm
from app.models import Document
from PIL import Image
import pytesseract
from wand.image import Image as wi
import os
#from matchFind import matchFind
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

    return render_template('index.html', title='home', corpus=corpus, documents=documents)

@app.route('/angular', methods=['GET', 'POST'])
def angular():
    return render_template('angular.html')

@app.route('/numberedView', methods=['GET', 'POST'])
def numberedView():
    pageViews = Document.query.paginate(1,1,False)
    Doc = Document.query.all()
    return render_template('numberedView.html', tree=make_tree("app/static/img"), pageViews=pageViews.items, Doc=Doc )

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    pdfs = UploadSet('pdfs', ['pdf'])
    app.config['UPLOADED_PDFS_DEST'] = 'app/static/img'
    configure_uploads(app, pdfs)
    if request.method == 'POST' and 'photo' in request.files:
        filename = pdfs.save(request.files['photo']) 
        doc =Document(txtLocation="/static/"+filename[:-4]+".txt", imgLocation ="/static/img/"+filename)
        db.session.add(doc)
        db.session.commit()
        #need to update above based on https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ix-pagination with code on submitting posts
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

def matchFind(corpus, keyword):
        A = corpus
        B = keyword
        C = A.split()
        D = B.split()
        Both = []
        for x in C:
            if x in D:
                Both.append(x)
        for x in range(len(Both)):
            Both[x]=str(Both[x])
        Final = []
        for x in set(Both):
            Final.append(x)
        MissingA = []
        for x in C:
            if x not in Final and x not in MissingA:
                MissingA.append(x)
        for x in range(len(MissingA)):
            MissingA[x]=str(MissingA[x])
        MissingB = []
        for x in D:
            if x not in Final and x not in MissingB:
                MissingB.append(x)
        for x in range(len(MissingB)):
            MissingB[x]=str(MissingB[x])
        return Final

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
            #figure out why wi returns none below when filename is PDF or hardcoded
            #convertPDF= wi(filename='./app/static/img/Bostrom.pdf', resolution = 300)
            convertPDF=wi(filename=PDF, resolution = 300)
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
           
             
            #for n, i in enumerate(recognized_text):
            #    if i == "/n":
            #        recognized_text[n]="<br>"
            #recognized_text="<br />".join(recognized_text.split("\n"))
            return recognized_text

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
def view():
    form = ViewForm()
    #create function to walk through documents using dictionary below
    DocumentsDict={}
    PDF = '/static/Bostrom.pdf'
    convertPDF= wi(filename ='app/static/Bostrom.pdf', resolution = 300)
    pdfImage = convertPDF.convert('jpeg')

    keywords = 'galactic supercluster bitcoin'

    with open("app/static/img/Bostrom.txt", "r") as f: 
        
        recognized_text = f.read()
        recognized_text=recognized_text.decode("utf-8").replace('\\n'," ")

    matches = matchFind(recognized_text, keywords)

    return render_template('view.html', title='View', form=form, PDF=PDF, recText=recognized_text, keywords=keywords, matches=matches)


