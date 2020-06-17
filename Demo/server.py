import os

from flask import request, Flask, jsonify, render_template, g

import math
import tensorflow as tf
import numpy as np

from PIL import Image
import cv2

import base64

from im2txt import configuration
from im2txt import inference_wrapper
from im2txt.inference_utils import caption_generator
from im2txt.inference_utils import vocabulary

import time

from bs4 import BeautifulSoup
import requests
from urllib.request import Request, urlopen

CHECKPOINT_PATH = 'model'
VOCAB_FILE = 'vocab/word_counts.txt'

tf.logging.set_verbosity(tf.logging.INFO)

# Build the inference graph.
g = tf.Graph()
with g.as_default():
	model = inference_wrapper.InferenceWrapper()
	restore_fn = model.build_graph_from_config(configuration.ModelConfig(), CHECKPOINT_PATH)
g.finalize()

# Create the vocabulary.
vocab = vocabulary.Vocabulary(VOCAB_FILE)

generator = caption_generator.CaptionGenerator(model, vocab)

# WEB API
app = Flask(__name__, template_folder='templates')

@app.route('/')
def root():
	return render_template('index.html')

@app.route('/caption', methods=['POST'])
def caption():
	start = time.time()

	# Request Preprocessing
	request_type = request.headers['Content-Type']
	print("Content-Type:", request_type)


	# submitted using HTML form containing image as file
	if "multipart/form-data" in request_type:

		pil_image = Image.open(request.files['image'])

		#  convert to numpy array
		nparr = np.asarray(pil_image)

	# request containing image as base64 string
	elif "application" in request_type:

		# submitted as JSON
		if "application/json" in request_type:
			data = request.get_json()

		# submitted as form encoding
		elif "application/x-www-form-urlencoded" in request_type:
			data = request.form
		else:
			return "Request type not supported"

		b64_string = data['image']

		b64_string += "=" * ((4 - len(b64_string) % 4) % 4) # padding
		original = base64.b64decode(b64_string)
		
		jpg_as_np = np.frombuffer(original, dtype=np.uint8)
		nparr = cv2.imdecode(jpg_as_np, flags=1)

	else:
		return "Request type not supported"

	#  let opencv decode image to correct format
	image = cv2.cvtColor(nparr, cv2.COLOR_BGR2RGB)
	image = cv2.imencode(".jpg", image)[1].tobytes()

	output = dict()
	output['captions'] = []

	with tf.Session(graph=g) as sess:
		print('Starting session....')
		# Load the model from checkpoint.
		restore_fn(sess)

		captions = generator.beam_search(sess, image)

		for i, caption in enumerate(captions):
			# Ignore begin and end words.
			sentence = [vocab.id_to_word(w) for w in caption.sentence[1:-1]]
			out = dict()
			out['caption'] = " ".join(sentence)
			out['caption'] = out['caption'].capitalize()
			out['caption'] = out['caption'].replace(" .", ".");

			out['probability'] = round(math.exp(caption.logprob), 5)
			
			output['captions'].append(out)


	print(output)
	print('Time taken:', time.time() - start, 'sec')
	
	return jsonify(output)


def page(url, header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}):
	req = Request(url, headers=header)
	page = urlopen(req).read()
	return BeautifulSoup(page, 'html.parser')


@app.route('/retrieve', methods=['POST'])
def retrieve():
	start = time.time()

	# Request Preprocessing
	request_type = request.headers['Content-Type']
	print("Content-Type:", request_type)

	query = ''

	# submitted using HTML form containing image as file
	if "multipart/form-data" in request_type:
		query = request.form['query']	

	# request containing image as base64 string
	elif "application" in request_type:

		# submitted as JSON
		if "application/json" in request_type:
			data = request.get_json()

		# submitted as form encoding
		elif "application/x-www-form-urlencoded" in request_type:
			data = request.form
		else:
			return "Request type not supported"
		
		query = data['query']
	
	query = '+'.join(query.split())

	toCreate = "static/img/{}/".format(query)

	if not os.path.exists(toCreate):
		os.makedirs(toCreate)
	
	url = "https://www.google.co.in/search?q="+ query +"&source=lnms&tbm=isch"

	soup = page(url)

	imgs = soup.find_all('img', attrs={'class': 'rg_i Q4LuWd'})

	output = dict()
	output['paths'] = []

	count = 0
	downloaded = 0
	for img in imgs:
		count += 1
		img = str(img)
		imgUrl = img.split('src="')[-1].replace('"', '').replace('/>', '').split(' ')[0]
		try:
			filename = toCreate + "{}.jpg".format(count)
			with open(filename, 'wb') as f:
				response = requests.get(imgUrl)
				f.write(response.content)
			
			output['paths'].append(filename)
			downloaded += 1
			if downloaded == 3:
				break
		except:
			os.remove(filename)
			continue
	
	print(output)
	print('Time taken:', time.time() - start, 'sec')
	
	return jsonify(output)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)