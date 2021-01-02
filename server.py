from asyncio.tasks import sleep
from http.server import HTTPServer, BaseHTTPRequestHandler
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

from numpy.lib.type_check import imag

import pyperclip
from skimage import io, transform
import numpy as np

# ide likes .img imports, python does not
if False is True:
    from .img import Image, ImageFolder
else:
    from img import Image, ImageFolder


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    image: Image = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.image: Image = None

    def do_GET(self):
        # import pdb; pdb.set_trace();
        print('Get to path: {}'.format(self.path))

        if (self.path == '/'):
            self.do_get_root()
        elif self.path == '/status':
            self.do_get_status()
        elif (self.path == '/pic'):
            self.do_get_pic()
        elif (self.path == '/open_folder'):
            self.do_open_folder()
        elif (self.path.startswith('/select_scan')):
            self.do_get_selected_scan()
        else:
            print('path unrecognized')

    def do_get_selected_scan(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        print(qs)

        fname = qs['fname'][0]

        global imageFolder, colours

        colours = []

        self.wfile.write(json.dumps(
            {'imgData': imageFolder.get_image_with_fname(fname).to_b64_png()}
        ).encode('utf-8'))

    def do_get_pic(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
          img = open('./data/sample.png', 'rb').read()
        except:
          print('sample.png not found, initialising empty Image')
          img = np.zeros((10, 10, 3))
        img64 = base64.b64encode(img).decode('ascii')
        # import pdb; pdb.set_trace()

        self.wfile.write(json.dumps(
            {'meme': True, 'imgData': img64}).encode('utf-8'))

    def do_open_folder(self):

        global imageFolder
        imageFolder = ImageFolder.from_gui_folder_selection()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(json.dumps(
            {'hasImages': len(imageFolder.images) > 0, 'thumbnails': imageFolder.get_thumbnails()}).encode('utf-8'))

    def do_get_status(self):

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(json.dumps(
          {'status': 'good'}
        ))

    def do_get_root(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        js = open('../frontend/app.tsx', 'rt').read()

        html = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <title>Hello World</title>
    <script src="https://unpkg.com/react@16/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@16/umd/react-dom.development.js"></script>

    <!-- Don't use this in production: -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="text/babel">
      {}
    </script>
    <!--
      Note: this page is a great way to try React but it's not suitable for production.
      It slowly compiles JSX with Babel in the browser and uses a large development build of React.

      Read this section for a production-ready setup with JSX:
      https://reactjs.org/docs/add-react-to-a-website.html#add-jsx-to-a-project

      In a larger project, you can use an integrated toolchain that includes JSX instead:
      https://reactjs.org/docs/create-a-new-react-app.html

      You can also use React without JSX, in which case you can remove Babel:
      https://reactjs.org/docs/react-without-jsx.html
    -->
  </body>
</html>'''.format(js)

        # html = open('../frontend/index.html', 'rt').read()

        self.wfile.write(bytes(html, 'utf8'))
        # self.wfile.write(b'Hello, world!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        body = json.loads(body)
        print('POST to ', self.path)
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

        # import pdb; pdb.set_trace();

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = BytesIO()
        # response.write(b'This is POST request. ')
        # response.write(b'Received: ')
        response.write(json.dumps({
            "circContext": img64,
            "meanColour": [int(x) for x in colour],
            "colourCompare": compare64,
            "clipboardContent": clipboard,
        }).encode('utf-8'))
        self.wfile.write(response.getvalue())

nodeRecvQ = queue.Queue()
nodeSendQ = queue.Queue()


def run_in_thread(func):
  threading.Thread(target = func, daemon=True).start()

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
    except websockets.exceptions.ConnectionClosedOK as e:
      print('NodeJS WS closed with exception:', e)

  asyncio.set_event_loop(asyncio.new_event_loop())

  run_server = websockets.serve(connect, 'localhost', 8001)
  print('Starting websocket server for nodejs comms at localhost:8001')

  asyncio.get_event_loop().run_until_complete(run_server)
  asyncio.get_event_loop().run_forever()

@run_in_thread
def ping_nodejs_websocket():
  while True:
    nodeSendQ.put('meme')
    time.sleep(1)

@run_in_thread
def print_from_nodejs_websocket():
  while True:
    while not nodeRecvQ.empty():
      print(nodeRecvQ.get())
    time.sleep(1)


# thread = threading.Thread(target = run_node_websocket, daemon=True)
# thread.start()

# fix tkinter bad dpi scaling
ctypes.windll.shcore.SetProcessDpiAwareness(1)


image = Image()
imageFolder = None
colours = []
httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
print('Serving...')
# webbrowser.open('http://localhost:8000')
httpd.serve_forever()
