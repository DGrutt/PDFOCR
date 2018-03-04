from app import db

class Corpus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    corpusname = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Corpus {}>'.format(self.corpusname)

