from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired

class ViewForm(FlaskForm):
    relevance = RadioField('Relevance', choices=[('hot','hot'),('relevant', 'relevant'), ('not relevant', 'not relevant')])
    submit = SubmitField('next')

class KeywordForm(FlaskForm):
    #keywords = TextAreaField('Keywords', validators=[DataRequired()]) 
    keywords = TextAreaField('Keywords')
    submit = SubmitField("Submit")
