from typing import List

from io import BytesIO
import tkinter
import tkinter.filedialog
import base64
import os

import numpy as np
from skimage import data, io, filters, draw
from PIL import Image as PILImage


class Image:

    fname: str
    data: np.ndarray

    def __init__(self, data=None, fname=None):
        if data is None:
            try:
                self.data = io.imread('./data/sample.png')
            except:
                print('sample.png not found, initialising empty Image')
                self.data = np.zeros((10, 10, 3))
        else:
            self.data = data

        self.fname = fname

    def add_circle(self, centerR, centerC, radius):
        rr, cc = draw.circle_perimeter(centerR, centerC, radius)

        self.data[rr, cc] = [255, 0, 0]

    def get_circle_context(self, cr, cc, r, s=3):
        newIm = np.copy(self.data)
        row, col = draw.circle_perimeter(cr, cc, r)
        newIm[row, col] = [255, 0, 0]

        return Image(newIm[
            max(cr - s*r, 0): min(cr + s*r, newIm.shape[0]),
            max(cc - s*r, 0): min(cc + s*r, newIm.shape[1]),
            :
        ])

    def get_circle_colour(self, cr, cc, r):
        rows, cols = draw.disk((cr, cc), r)

        # colour = np.mean(self.data[rows, cols], axis=(0, 1))
        colour = np.mean(self.data[rows, cols], axis=0)

        return colour

    def get_colour_display(self, cr, cc, r):
        colour = self.get_circle_colour(cr, cc, r)

        rows, cols = draw.disk((cr, cc), r)

        im = np.full((2*r, 2*r, 3), 255, dtype=self.data.dtype)

        irows, icols = draw.disk((r, r), r)

        im[irows, icols] = self.data[rows, cols]

        im[:, :r] = colour

        return Image(im)

    def to_png_bytes(self):

        with BytesIO() as stream:

            pIm = PILImage.fromarray(self.data)
            pIm.save(stream, format='PNG')

            return stream.getvalue()

    def to_b64_png(self):
        return base64.b64encode(self.to_png_bytes()).decode('ascii')

    def show(self):
        io.imshow(self.data)
        io.show()


if __name__ == '__main__':
    img = Image()
    cr = 294
    cc = 484
    r = 73


class ImageFolder:

    downsample: int = 2

    def __init__(self, dir_path: str, images: List[Image]):
        self.dir_path = dir_path
        self.images = images

    @classmethod
    def from_gui_folder_selection(cls):
        root = tkinter.Tk()
        root.attributes("-topmost", True)
        root.lift()
        root.focus_force()
        root.withdraw()

        res = tkinter.filedialog.askdirectory(parent=root)
        root.destroy()
        print(res)
        scans = os.listdir(res)
        print(scans)

        # thumbnails = []
        images = []

        for scan in scans:
            fname = res + '/' + scan
            print('opening: ', fname)
            try:
                scanData = io.imread(fname)
            except:
                print('Failed to open', fname)
                continue

            print('finished imread')
            print('WARNING: IMAGES ARE BEING DOWNSIZED')
            images.append(
                Image(scanData[::cls.downsample, ::cls.downsample], scan))
            # scanThumb = transform.resize(scanData, (scanData.shape[0] // 10, scanData.shape[1] // 10), anti_aliasing=True)
            # scanThumb = Image(np.asarray(scanData[::8, ::8], order='C'))
            # thumbnails.append({
            #     'fileName': scan,
            #     'img': base64.b64encode(scanThumb.to_png_bytes()).decode('ascii'),
            # })

        return cls(res, images)

    def get_thumbnails(self):
        return [
            {
                'fileName': img.fname,
                'img': base64.b64encode(
                    Image(np.asarray(
                        img.data[::8, ::8], order='C')).to_png_bytes()
                ).decode('ascii')
            }
            for img in self.images
        ]

    def get_image_with_fname(self, fname: str) -> Image:
        return [i for i in self.images if i.fname == fname][0]


class BlotchCircle:

    id: int
    centerRow: float
    centerCol: float
    radius: float
    context: Image
    avgColour: np.ndarray

    def __init__(self, id: int, centerRow: float, centerCol: float, radius: float, context: Image, avgColour: np.ndarray):
        self.id = id
        self.centerRow = centerRow
        self.centerCol = centerCol
        self.radius = radius
        self.context = context
        self.avgColour = avgColour

    @classmethod
    def from_selected_circle(cls, id: int, centerRow: float, centerCol: float, radius: float, image: Image):

        context = image.get_circle_context(centerRow, centerCol, radius)
        avgColour = image.get_circle_colour(centerRow, centerCol, radius)

        return cls(id, centerRow, centerCol, radius, context, avgColour)


class ImageSession:

    image: Image

    blotchCircles: List[BlotchCircle]
    nextBlotchId: int

    def __init__(self, image: Image) -> None:
        self.image = image

        self.blotchCircles = []
        self.nextBlotchId = 0

    def add_circle(self, centerRow: float, centerCol: float, radius: float):
        self.blotchCircles.append(BlotchCircle.from_selected_circle(
            self.nextBlotchId, centerRow, centerCol, radius, self.image
        ))
        self.nextBlotchId += 1

    def remove_circle(self, id: int):
        for idx, bc in enumerate(self.blotchCircles):
            if bc.id == id:
                self.blotchCircles.pop(idx)
                return

# class Session:

#   imgFolder: ImageFolder
#   currImgSession: ImageSession

#   def __init__(self) -> None:
#     pass

#   def set_imgFolder(imgFolder: ImageFolder):
