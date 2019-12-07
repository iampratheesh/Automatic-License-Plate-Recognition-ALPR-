import os
from flask import Flask
from flask import render_template, url_for, redirect
from flask_forms.forms import ImageForm

import cv2
from darkflow.net.build import TFNet
import pytesseract
import numpy as np
from PIL import Image
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

options = {
	'model': 'cfg/tiny-yolo-voc-1c.cfg',
	'load': 1125,
	'threshold': 0.1
}

tfnet = TFNet(options)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    i = Image.open(form_picture)
    i.save(picture_path)
    return picture_fn

@app.route('/', methods = ['GET','POST'])
def home():
	form = ImageForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			img = img = cv2.imread(os.path.join(app.root_path, 'static/images', picture_file), cv2.IMREAD_COLOR)
			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			result = tfnet.return_predict(img)

			tl = (result[0]['topleft']['x'], result[0]['topleft']['y'])
			br = (result[0]['bottomright']['x'], result[0]['bottomright']['y'])
			label = result[0]['label']
			confidence = result[0]['confidence']
			print(result)
			img = cv2.rectangle(img, tl, br, (0,255,0), 7)
			img = cv2.putText(img, label, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 2)
			img = cv2.putText(img, str(confidence), br, cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 2)

			x1,y1 = tl
			x2,y2 = br
			license_plate = img[y1:y2, x1:x2]
			print(type(img), type(license_plate))
			img = Image.fromarray(img)
			license_plate = Image.fromarray(license_plate)
			print(type(img), type(license_plate))
			#text = pytesseract.image_to_string(license_plate)
			return render_template('output.html', img=img, license_plate=license_plate) #text=text)
	return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)