from app import db

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    txtLocation = db.Column(db.String(300), index=True, unique=True)
    imgLocation = db.Column(db.String(300), index=True, unique=True)
    keywordMatches= db.Column(db.String(300), index=True, unique=False)
    sentiment = db.Column(db.String(300), index=True, unique=False)

class raw_text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_number = (db.Integer)
    page_text = (db.Text)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))

    def __repr__(self):
        return '<Document {} {} {} {}>'.format("text "+self.imgLocation, self.txtLocation, self.keywordMatches, self.sentiment)

