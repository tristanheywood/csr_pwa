from asyncio.tasks import sleep
# from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import Flask, request, send_file
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
from flask.globals import session
from numpy.core.arrayprint import BoolFormat
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

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# # ide likes .img imports, python does not
# if False is True:
#     from .img import BaseImage, ImageFolder, Session, ImageSession, ImgLogger, BlotchCircle
#     from .protobuf_py.types import *
# else:
#     from img import BaseImage, ImageFolder, Session, ImageSession, ImgLogger, BlotchCircle
#     from protobuf_py.types import *

from pkg.img import BaseImage, ImageFolder, Session, ImageSession, ImgLogger, BlotchCircle
from pkg.protobuf_py.types import *
if False is True:
  from .pkg.img import BaseImage, ImageFolder, Session, ImageSession, ImgLogger, BlotchCircle
  from .pkg.protobuf_py.types import *

nodeRecvQ = queue.Queue()
nodeSendQ = queue.Queue()

def log(*args):
    msg = ' '.join(str(arg) for arg in args)

    print('[Log]', msg)
    nodeSendQ.put(msg)

ImgLogger.log = log

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
handler = WSForwardLogHandler()
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)


@app.route('/open_folder')
def do_open_folder():
    log('opening folder selection ui')

    # global imageFolder
    # imageFolder = ImageFolder.from_gui_folder_selection()

    global session
    session.set_imgFolder(ImageFolder.from_gui_folder_selection())
    # session.imgFolder.register_images_on_session(session)
    session.set_currImgSession(ImageSession(session.imgFolder.images[0]))

    uiState = session.get_UIState_msg()

    return uiState.SerializeToString()

    # return {
    #     'hasImages': len(session.imgFolder.images) > 0,
    #     'thumbnails': session.imgFolder.get_thumbnails()
    # }

@app.route('/select_scan')
def do_get_selected_scan():
    fname = request.args.get('fname')
    idx = int(request.args.get('selectedIdx'))
    log('Processing get for file:', fname)

    # global imageFolder, colours

    # colours = []

    global session

    scanImg = session.get_image_by_name(fname)
    imgSess = ImageSession(scanImg)
    session.set_currImgSession(imgSess)
    session.currSelectedImgIdx = idx

    return session.get_UIState_msg().SerializeToString()

    # return {'imgData': session.currImgSession.image.to_b64_png()}

@app.route('/set_clipboard_cols', methods=['POST'])
def set_clipboard_cols():

  body = request.get_data()
  log('clipboard cols body', body)

  cvc = ClipboardViewColumns.FromString(body)

  log('/set_clipboard_cols', cvc.to_dict())

  global session
  session.selectedClipboardCols = cvc

  pyperclip.copy(session.get_clipboard_str())

  return session.get_UIState_msg().SerializeToString()

@app.route('/new_circle', methods=['POST'])
def do_new_circle():

    # body = json.loads(request.get_data())
    body = request.get_data()
    # print(request)
    print('body:', body)

    pc = PickedCircle.FromString(body)

    log('/new_circle', pc.to_dict())

    # global image
    # self.image = image

    # global imageFolder
    # image = imageFolder.get_image_with_fname(pc.img_file_name)

    global session
    # image = session.imgFolder.get_image_with_fname(pc.img_file_name)
    image: BaseImage = session.get_image_by_name(pc.img_file_name)
    imgSess = session.currImgSession

    # self.image.add_circle(int(body['center']['y']), int(body['center']['x']), int(body['radius']))
    # self.image.show()
    cr = int(pc.center_row)
    cc = int(pc.center_col)
    r = int(pc.radius)

    # im = image.get_circle_context(int(pc.center_y), int(
    #     pc.center_x), int(pc.radius))

    # contextPNG = im.to_png_bytes()
    # img64 = base64.b64encode(contextPNG).decode('ascii')

    # session.currImgSession.add_circle(cr, cc, r)

    # # colour = image.get_circle_colour(cr, cc, r)
    # comparePNG = image.get_colour_display(cr, cc, r).to_png_bytes()
    # compare64 = base64.b64encode(comparePNG).decode('ascii')

    imgSess.add_circle(cr, cc, r)
    # imgSess.blotchCircles[-1].register_imgs_on_session(session)

    # global colours
    # colours.append([int(x) for x in colour])



    # clipboard = '\n'.join('\t'.join(str(component) for component in _colour)
                          # for _colour in colours)
    # pyperclip.copy(
    #     clipboard
    # )

    # pyperclip.copy(imgSess.get_clipboard_str())
    pyperclip.copy(session.get_clipboard_str())

    # return {
    #     "circContext": img64,
    #     "meanColour": "",
    #     "colourCompare": compare64,
    #     "clipboardContent": imgSess.get_clipboard_content_msg().SerializeToString(),
    # }

    return session.get_UIState_msg().SerializeToString()

    # import pdb; pdb.set_trace();

    # resp = BytesIO()
    # # response.write(b'This is POST request. ')
    # # response.write(b'Received: ')
    # resp.write().encode('utf-8'))
    # return resp

@app.route('/image_bytes/<path:vfn>')
def serve_image_bytes(vfn):
  log('Client requested image with vfn: ', vfn)

  global session
  # bio = session.imgDataManager.get_img(vfn)
  bio = session.get_image_data_by_name(vfn)
  bio.seek(0)
  bioCopy = BytesIO(bio.getvalue())

  return send_file(bioCopy, mimetype='image/png', cache_timeout=60*60*24)

@app.route('/remove_blotch/<blotchId>')
def remove_blotch(blotchId):
  log('Client requested removal of blotch ', blotchId)

  global session
  session.currImgSession.remove_blotch(int(blotchId))

  pyperclip.copy(session.get_clipboard_str())

  return session.get_UIState_msg().SerializeToString()

@app.route('/set_zoom/<viewRatio>/<srcRatio>')
def set_zoom(viewRatio: str, srcRatio: str):
  viewRatio = int(viewRatio)
  srcRatio = int(srcRatio)

  log(f'Client requested zoom of {viewRatio}:{srcRatio} (viewRatio:srcRatio)')

  global session
  session.set_img_zoom(viewRatio, srcRatio)

  return session.get_UIState_msg().SerializeToString()



# thread = threading.Thread(target = run_node_websocket, daemon=True)
# thread.start()

# fix tkinter bad dpi scaling
ctypes.windll.shcore.SetProcessDpiAwareness(1)


# image = Image()
# imageFolder = None
# colours = []

session = Session()

# httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
log('Serving...')
# webbrowser.open('http://localhost:8000')
# httpd.serve_forever()

app.run(host='localhost', port=8000)
