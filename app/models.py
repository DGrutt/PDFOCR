from app import db

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    txtLocation = db.Column(db.String(300), index=True, unique=True)
    imgLocation = db.Column(db.String(300), index=True, unique=True)
    keywordMatches= db.Column(db.String(300), index=True, unique=False)
    sentiment = db.Column(db.String(300), index=True, unique=False)
    texts = db.relationship('Raw_Text', backref='source', lazy='dynamic')

    
    def __repr__(self):
        return '<Document {} {} {} {}>'.format(self.imgLocation, self.txtLocation, self.keywordMatches, self.sentiment)

class Raw_Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_number = (db.Integer)
    page_text = (db.Text)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))

    def __repr__(self):
        return '<Raw_Text {} {} {} {}>'.format(self.id, self.page_number, self.page_text, self.document_id)

