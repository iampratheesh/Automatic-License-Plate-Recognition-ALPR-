from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired
from wtforms import SubmitField

class ImageForm(FlaskForm):
	picture = FileField('Upload your image here: ', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Submit')