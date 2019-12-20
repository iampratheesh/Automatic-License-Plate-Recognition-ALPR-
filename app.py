import os, shutil
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
    print(picture_path)
    i = Image.open(form_picture)
    i.save(picture_path)
    return picture_fn

def save_output(image_array):
	PIL_image = Image.fromarray(image_array)
	random_hex = secrets.token_hex(8)
	f_ext = ".png"
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/output', picture_fn)
	PIL_image.save(picture_path , 'PNG')
	return picture_fn

def remove_files(path):
	for filename in os.listdir(path):
	    file_path = os.path.join(path, filename)
	    try:
	        if os.path.isfile(file_path) or os.path.islink(file_path):
	            os.unlink(file_path)
	        elif os.path.isdir(file_path):
	            shutil.rmtree(file_path)
	    except Exception as e:
	        print('Failed to delete %s. Reason: %s' % (file_path, e))

@app.route('/', methods = ['GET','POST'])
def home():
	form = ImageForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			img = img = cv2.imread(os.path.join(app.root_path, 'static/images', picture_file), cv2.IMREAD_COLOR)
			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			results = tfnet.return_predict(img)
			img_name = save_output(img)
			img_path = url_for('static', filename='output/' + img_name)
			license_plate_lst = []
			text_lst = []
			for result in results:
				print(result)
				tl = (result['topleft']['x'], result['topleft']['y'])
				br = (result['bottomright']['x'], result['bottomright']['y'])
				label = result['label']
				confidence = result['confidence']
				
				x1,y1 = tl
				x2,y2 = br
				license_plate = img[y1:y2, x1:x2]

				#img = cv2.rectangle(img, tl, br, (0,255,0), 7)
				#img = cv2.putText(img, label, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 2)
				#img = cv2.putText(img, str(confidence), br, cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 2)

				license_plate_name = save_output(license_plate)
				license_plate_path = url_for('static', filename='output/' + license_plate_name)
				license_plate_lst.append(license_plate_path)

				image = cv2.imread(os.path.join(app.root_path, 'static/output', license_plate_name))
				gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
				gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
				gray = cv2.medianBlur(gray, 3)
				filename = "{}.png".format(os.getpid())
				cv2.imwrite(filename, gray)
				text = pytesseract.image_to_string(Image.open(filename))
				text_lst.append(text)
				os.remove(filename)

			return render_template('output.html', img_path=img_path, license_plate_lst=license_plate_lst, text_lst=text_lst)
	path = os.path.join(app.root_path, 'static/output')
	remove_files(path)
	path = os.path.join(app.root_path, 'static/images')
	remove_files(path)
	return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)