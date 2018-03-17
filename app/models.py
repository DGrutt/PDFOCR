from app import db

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    txtLocation = db.Column(db.String(300), index=True, unique=True)
    imgLocation = db.Column(db.String(300), index=True, unique=True)


    def __repr__(self):
        return '<Document {} {}>'.format("text "+self.imgLocation, self.txtLocation)

