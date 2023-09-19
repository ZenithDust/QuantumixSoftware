from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class KeySystem(FlaskForm):
  recaptcha = RecaptchaField()

class KeyCaptcha(FlaskForm):
  captcha = RecaptchaField()

class Search(FlaskForm):
  searchInput = StringField()