import io
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_uploads import UploadSet, configure_uploads 
# add to import line above PDFs and remove IMAGES
from app import app
from app.forms import ViewForm
from PIL import Image
import pytesseract
from wand.image import Image as wi
import os

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

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    photos = UploadSet('photos', ['pdf'])
    app.config['UPLOADED_PHOTOS_DEST'] = 'app/static/img'
    configure_uploads(app, photos)
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
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
                tree['children'].append(dict(name=fn))
    return tree     

@app.route('/complete', methods=['GET', 'POST'])
def complete():
    path = os.path.expanduser(u'~')
    #return render_template('complete.html', tree=make_tree("/home/dan/PDFOCR/app/static/img"))
    return render_template('complete.html', tree=make_tree("app/static/img"))

@app.route('/view', methods=['GET', 'POST'] )
#Note the code to display a jpeg is still in this function but unused.
def view():
    form = ViewForm()
    docimage = '/static/Irregularis_sampletext.png'
    im = Image.open('app/static/Irregularis_sampletext.png')
    text = pytesseract.image_to_string(im, lang = 'eng')
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
        recognized_text.append(text)
    return render_template('view.html', title='View', docimage=docimage, form=form, text=text, PDF=PDF, recText=recognized_text)


