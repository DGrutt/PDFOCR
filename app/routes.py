import io
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_uploads import UploadSet, configure_uploads, IMAGES 
# add to import line above PDFs and remove IMAGES
from app import app
from app.forms import ViewForm
from PIL import Image
import pytesseract
from wand.image import Image as wi


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
    photos = UploadSet('photos', IMAGES)
    app.config['UPLOADED_PHOTOS_DEST'] = 'app/static/img'
    configure_uploads(app, photos)
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        return filename 
    return render_template('upload.html')

@app.route('/view', methods=['GET', 'POST'] )
#Note the code to display a jpeg is still in this function but unused.
def view():
    form = ViewForm()
    if form.validate_on_submit():
        flash('document coded {}'.format(form.relevance.data))
        return redirect(url_for('index'))
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


