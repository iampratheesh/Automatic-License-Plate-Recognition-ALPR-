import os
from flask import Flask
from flask import render_template, url_for, flash, redirect, request, abort
from flask_forms.forms import ImageForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

@app.route('/', methods = ['GET','POST'])
def home():
	form = ImageForm()
	if form.validate_on_submit():
		if form.picture.data:
			return render_template('Success')
	return render_template('index.html', form=form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    app.run(debug=True)