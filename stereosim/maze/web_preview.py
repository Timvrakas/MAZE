"""Web Server Framework"""
from flask import Flask, jsonify, render_template, request, send_file
import logging
import os
import sys
from multiprocessing.managers import BaseManager
app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


def get_maze():
    BaseManager.register('get_maze')
    manager = BaseManager(address=('', 50000), authkey=b'abc')
    manager.connect()
    maze = manager.get_maze()
    return maze


@app.route('/')
def index():
    maze = get_maze()
    return render_template('preview.html')


@app.route('/refresh_preview', methods=['POST'])
def refresh_preview():
    maze = get_maze()
    images = maze.get_last_images()
    image_hash = hash(tuple(images))
    if images is None:
        image_hash = 0
    return jsonify({'image_hash': image_hash})

@app.route('/get_stats', methods=['POST'])
def get_stats():
    maze = get_maze()
    stats = maze.get_stats()
    return jsonify({'stats' : stats})


@app.route('/leftImg.jpg')
def leftImg():
    maze = get_maze()
    image_left, image_right = maze.get_last_images()
    if(image_left is not None):
        return send_file(image_left, mimetype='image/jpeg')
    else:
        return jsonify({'image_left': image_left, 'image_right': image_right})


@app.route('/rightImg.jpg')
def rightImg():
    maze = get_maze()
    image_left, image_right = maze.get_last_images()
    if(image_right is not None):
        return send_file(image_right, mimetype='image/jpeg')
    else:
        return jsonify({'image_left': image_left, 'image_right': image_right})


def startServer():
    try:
        os.remove('flask.log')
    except FileNotFoundError:
        pass
    sys.stdout = open('flask.log', "w")
    logging.getLogger('Flask').info(
        "Starting Preview Server at: http://10.5.0.1:5000/")
    app.run(host='0.0.0.0')
