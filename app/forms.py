from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired


class stripeform(Form):
    email = StringField("Email")

def __init__(self):
    Form.__init__(self)