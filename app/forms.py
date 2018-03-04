from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from wtforms.validators import DataRequired

class ViewForm(FlaskForm):
    relevance = RadioField('Relevance', choices=[('hot','hot'),('relevant', 'relevant'), ('not relevant', 'not relevant')])
    submit = SubmitField('next')
