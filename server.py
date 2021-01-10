from asyncio.tasks import sleep
# from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import Flask, request
import urllib.parse
from io import BytesIO
import os
import json
import base64
import webbrowser
import tkinter
import tkinter.filedialog
import ctypes
import asyncio
import websockets
import queue
import threading
import time
import logging
import sys

from numpy.lib.type_check import imag

import pyperclip
from skimage import io, transform
import numpy as np

# ide likes .img imports, python does not
if False is True:
    from .img import Image, ImageFolder
else:
    from img import Image, ImageFolder

nodeRecvQ = queue.Queue()
nodeSendQ = queue.Queue()

def log(*args):
    msg = ' '.join(args)

    print('[Log]', msg)
    nodeSendQ.put(msg)

class WSForwardLogHandler(logging.StreamHandler):

  def emit(self, record):
    print('wsforward.emit')
    msg = self.format(record)
    log(msg)

def run_in_thread(func):
    threading.Thread(target=func, daemon=True).start()

@run_in_thread
def run_node_websocket():

    async def connect(websocket, path):

        async def send():
            while True:
                while not nodeSendQ.empty():
                    msg = nodeSendQ.get()
                    await websocket.send(msg)
                await asyncio.sleep(0.1)
            # if not nodeSendQ.empty():
            #   msg = nodeSendQ.get()
            #   await websocket.send(msg)

        async def recv():
            while True:
                msg = await websocket.recv()
                nodeRecvQ.put(msg)

        try:
            await asyncio.gather(
                send(),
                recv(),
            )
        except websockets.exceptions.WebSocketException as e:
            print('NodeJS WS closed with exception:', e)

    asyncio.set_event_loop(asyncio.new_event_loop())

    run_server = websockets.serve(connect, 'localhost', 8001)
    print('Starting websocket server for nodejs comms at localhost:8001')

    asyncio.get_event_loop().run_until_complete(run_server)
    asyncio.get_event_loop().run_forever()

# @run_in_thread
# def ping_nodejs_websocket():
#   while True:
#     nodeSendQ.put('meme')
#     time.sleep(1)


@run_in_thread
def print_from_nodejs_websocket():
    while True:
        while not nodeRecvQ.empty():
            print(nodeRecvQ.get())
        time.sleep(1)

# def do_get_pic(self):
#     self.send_response(200)
#     self.send_header("Content-type", "application/json")
#     self.send_header("Access-Control-Allow-Origin", "*")
#     self.end_headers()

#     try:
#         img = open('./data/sample.png', 'rb').read()
#     except:
#         print('sample.png not found, initialising empty Image')
#         img = np.zeros((10, 10, 3))
#     img64 = base64.b64encode(img).decode('ascii')
#     # import pdb; pdb.set_trace()

#     self.wfile.write(json.dumps(
#         {'meme': True, 'imgData': img64}).encode('utf-8'))

app = Flask(__name__)
app.logger.addHandler(WSForwardLogHandler())
app.logger.setLevel(logging.INFO)

@app.route('/select_scan')
def do_get_selected_scan():
    fname = request.args.get('fname')
    log('Processing get for file:', fname)

    global imageFolder, colours

    colours = []

    return {'imgData': imageFolder.get_image_with_fname(fname).to_b64_png()}

@app.route('/open_folder')
def do_open_folder():
    log('opening folder selection ui')

    global imageFolder
    imageFolder = ImageFolder.from_gui_folder_selection()

    return {
        'hasImages': len(imageFolder.images) > 0,
        'thumbnails': imageFolder.get_thumbnails()
    }

@app.route('/new_circle', methods=['POST'])
def do_new_circle():

    body = json.loads(request.get_data())
    # print(request)
    print('body:', body)

    # global image
    # self.image = image

    global imageFolder
    image = imageFolder.get_image_with_fname(body['fname'])

    # self.image.add_circle(int(body['center']['y']), int(body['center']['x']), int(body['radius']))
    # self.image.show()
    cr = int(body['center']['y'])
    cc = int(body['center']['x'])
    r = int(body['radius'])

    im = image.get_circle_context(int(body['center']['y']), int(
        body['center']['x']), int(body['radius']))

    contextPNG = im.to_png_bytes()
    img64 = base64.b64encode(contextPNG).decode('ascii')

    colour = image.get_circle_colour(cr, cc, r)
    comparePNG = image.get_colour_display(cr, cc, r).to_png_bytes()
    compare64 = base64.b64encode(comparePNG).decode('ascii')

    global colours
    colours.append([int(x) for x in colour])

    clipboard = '\n'.join('\t'.join(str(component) for component in _colour)
                          for _colour in colours)
    pyperclip.copy(
        clipboard
    )

    return {
        "circContext": img64,
        "meanColour": [int(x) for x in colour],
        "colourCompare": compare64,
        "clipboardContent": clipboard,
    }

    # import pdb; pdb.set_trace();

    # resp = BytesIO()
    # # response.write(b'This is POST request. ')
    # # response.write(b'Received: ')
    # resp.write().encode('utf-8'))
    # return resp




# thread = threading.Thread(target = run_node_websocket, daemon=True)
# thread.start()

# fix tkinter bad dpi scaling
ctypes.windll.shcore.SetProcessDpiAwareness(1)


image = Image()
imageFolder = None
colours = []
# httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
log('Serving...')
# webbrowser.open('http://localhost:8000')
# httpd.serve_forever()

app.run(host='localhost', port=8000)
