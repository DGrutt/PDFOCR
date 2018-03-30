import io
from flask import Flask, render_template, flash, redirect, url_for, request
#from flask_triangle import Triangle
from flask_uploads import UploadSet, configure_uploads 
# add to import line above PDFs and remove IMAGES
from app import app, db
from app.forms import ViewForm, KeywordForm
from app.models import Document
from PIL import Image
import pytesseract
from wand.image import Image as wi
import os
#from matchFind import matchFind
from uuid import uuid4

import nltk
nltk.download('movie_reviews')
import random
from nltk.corpus import movie_reviews
from nltk.classify import *
import pickle
#adding nltk

import shutil

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


def show_most_informative_features_in_list(classifier, n=10):
    """
    Return a nested list of the "most informative" features 
    used by the classifier along with it's predominant labels
    !!
    Try to modify this function like this:
    http://www.nltk.org/_modules/nltk/classify/naivebayes.html#NaiveBayesClassifier.show_most_informative_features
    """
    cpdist = classifier._feature_probdist       
    # probability distribution for feature values given labels
    feature_list = []
    for (fname, fval) in classifier.most_informative_features(n):
        def labelprob(l):
            return cpdist[l, fname].prob(fval)
        labels = sorted([l for l in classifier._labels if fval in cpdist[l, fname].samples()], 
                        key=labelprob)
        feature_list.append([fname, labels[-1]])
    return feature_list


@app.route('/sentiment_all', methods=['GET', 'POST'])
def sentiment_all():
    documents = [(list(movie_reviews.words(fileid)), category)
                    for category in movie_reviews.categories()
                    for fileid in movie_reviews.fileids(category)]

    random.shuffle(documents)

    all_words = []

    for w in movie_reviews.words():
        all_words.append(w.lower())

    all_words = nltk.FreqDist(all_words)
    
    word_features = list(all_words.keys()) [:3000]
    
    def find_features(document):
        words = set(document)
        features = {}
        for w in word_features:
            features[w]=(w in words)
        return features
    
    featuresets = [(find_features(rev), category) for (rev, category) in documents]

    training_set = featuresets[:1900]
    testing_set = featuresets[1900:]

    classifier = nltk.NaiveBayesClassifier.train(training_set)
    
    save_classifier = open("naivebayes.pickle", "wb")
    pickle.dump(classifier, save_classifier)
    save_classifier.close()    

    classifier_f = open("naivebayes.pickle", "rb")
    classifier = pickle.load(classifier_f)
    classifier_f.close()
    
    #accuracy = nltk.classify.accuracy(classifier, testing_set)*100
    informativeFeatures = show_most_informative_features_in_list(classifier, 15)      
    
    #in below copy from numberedView and get sentiment one by one
    #results = classifier.classify(testing_set)
     
    return render_template('sentiment_all.html', informativeFeatures=informativeFeatures, featuresets=featuresets, documents=documents)

@app.route('/keywordMatches', methods=['GET', 'POST'])
def keywordMatches():
    form = KeywordForm()
    if request.method == 'POST':
        Doc = Document.query.all()
        for item in Doc:
            with open("app"+item.txtLocation, "r") as f:
                tmp= f.read()
            #item.keywordMatches=tmp
            #item.keywordMatches=item.txtLocation
            item.keywordMatches=str(matchFind(tmp, form.keywords.data))
        db.session.commit()
    return render_template('keywordMatches.html', form=form)

@app.route('/numberedView', methods=['GET', 'POST'])
def numberedView():
       
    page = request.args.get('page', 1, type=int)
    pageViews = Document.query.paginate(page,1,False)
    next_url = url_for('numberedView', page=pageViews.next_num) \
        if pageViews.has_next else None
    prev_url = url_for('numberedView', page=pageViews.prev_num) \
        if pageViews.has_prev else None
    Doc = Document.query.all()
    for document in pageViews.items:
        with open("app"+document.txtLocation, "r") as f:
            DocText = f.read()
    for document in pageViews.items:
        docImage=str(document.imgLocation)
    for document in pageViews.items:
        docKeywordMatches = str(document.keywordMatches)
    
    #nltk portion 
    documents = [(list(movie_reviews.words(fileid)), category)
                    for category in movie_reviews.categories()
                    for fileid in movie_reviews.fileids(category)]

    random.shuffle(documents)

    all_words = []

    for w in movie_reviews.words():
        all_words.append(w.lower())

    all_words = nltk.FreqDist(all_words)
    
    word_features = list(all_words.keys()) [:3000]
    
    def find_features(document):
        words = set(document)
        features = {}
        for w in word_features:
            features[w]=(w in words)
        return features
    
    featuresets = [(find_features(rev), category) for (rev, category) in documents]

    #featuresets is a list of dictionaries 
    DocTextList=find_features(DocText.split())
    
    training_set = featuresets[:1900]
    #testing_set = featuresets[1900:]
    testing_set = DocTextList   

    classifier = nltk.NaiveBayesClassifier.train(training_set)
    
    save_classifier = open("naivebayes.pickle", "wb")
    pickle.dump(classifier, save_classifier)
    save_classifier.close()    

    classifier_f = open("naivebayes.pickle", "rb")
    classifier = pickle.load(classifier_f)
    classifier_f.close()
    
    results = classifier.classify(testing_set)
    informativeFeatures = show_most_informative_features_in_list(classifier, 15)    
    #ends nltk portion


    
    return render_template('numberedView.html', tree=make_tree("app/static/img"), pageViews=pageViews.items, docImage=docImage, Doc=Doc, DocText=DocText, docKeywordMatches=docKeywordMatches, next_url=next_url, prev_url=prev_url, results=results, informativeFeatures=informativeFeatures)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    pdfs = UploadSet('pdfs', ['pdf', 'txt', 'img', 'jpeg'])
    #if the extension is 4 characters such as jpeg it will cause a problem
    app.config['UPLOADED_PDFS_DEST'] = 'app/static/img'
    configure_uploads(app, pdfs)
    if request.method == 'POST' and 'photo' in request.files:
        filename = pdfs.save(request.files['photo']) 
        DocTxtLoc ="/static/txts/"+ filename[:-4]+".txt"
        if DocTxtLoc.endswith("..txt"):
            DocTxtLoc=DocTxtLoc[:-5]+".txt"
        doc =Document(txtLocation=DocTxtLoc, imgLocation ="/static/OCRdfiles/"+filename, keywordMatches="test", sentiment="blank")
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
        B = keyword.lower()
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


def ocr(file_to_ocr):
    im = Image.open(file_to_ocr)
    txt = pytesseract.image_to_string(im, lang='eng')
    return txt
           
def pdfOCR(pdf_to_ocr):
    #function to OCR pdfs 
    PDF = pdf_to_ocr 
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
                        
    recognized_text=str(recognized_text).replace('\\n'," ")
    return recognized_text.lower()

@app.route('/OCR_All', methods=['GET', 'POST'])
def OCR_All():
    debugVar="unchanged"
    #import pdb; pdb.set_trace()
    if request.method == 'POST':
        
        directory = os.path.join("app/static/img")        
        
        Doc = Document.query.all()
        for root,dirs,files in os.walk(directory):
            for file in files:
                if file.endswith(".pdf"):
                    pre_fix=file[:-4]
                    for item in Doc:
                        #if str(item.txtLocation[:-4]).endswith(pre_fix):
                        #   debugVar= "OCR complete"
                        #else:
                        text=pdfOCR("./app/static/img/" + file)
                        with open("app/static/txts/"+pre_fix+".txt", 'w') as f: f.write(str(text))
                        f.close()
                        shutil.copy2('./app/static/img/' + file, './app/static/OCRdfiles/')
                        os.remove('./app/static/img/' + file)
 
                if file.endswith(".png"):
                    pre_fix=file[:-4] 
                    for item in Doc:
                    #    if str(item.txtLocation[:-4]).endswith(pre_fix):
                    #       debugVar= "OCR complete"
                        txt=ocr("./app/static/img/"+file)
                        with open(directory+"//"+pre_fix+".txt", 'w') as f: f.write(str(txt))
                        f.close()   
                        shutil.copy2('./app/static/img/' + file, './app/static/OCRdfiles/')
                
                if file.endswith(".jpeg"):
                    pre_fix=file[:-5]
                    for item in Doc:
                    #    if str(item.txtLocation[:-4]).endswith(pre_fix):
                    #       debugVar= "OCR complete"
                        txt=ocr("./app/static/img/"+file)
                        with open(directory+"//"+pre_fix+".txt", 'w') as f: f.write(str(txt))
                        f.close() 
                        shutil.copy2('./app/static/img/' + file, './app/static/OCRdfiles/')

    #find a way to add this line to the code on the line above so you don't ocr completed files
    #if os.path.isfile(directory+"//"+pre_fix+".txt")==False: 
                            
    #if request.method == 'POST':
    #    pass
    return render_template("OCR_all.html", debugVar=debugVar)


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
        #recognized_text=recognized_text.decode("utf-8").replace('\\n'," ")
        recognized_text=recognized_text.replace('\\n'," ")

    matches = matchFind(recognized_text, keywords)

    return render_template('view.html', title='View', form=form, PDF=PDF, recText=recognized_text, keywords=keywords, matches=matches)


