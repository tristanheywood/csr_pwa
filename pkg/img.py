from typing import List, Dict, Any

from abc import ABC
from io import BytesIO
import tkinter
import tkinter.filedialog
import base64
import os
from io import BytesIO
import uuid
import PIL

import numpy as np
from skimage import data, io, filters, draw
from PIL import Image as PILImage
from websockets.typing import Data

if False is True:
    from .protobuf_py.types import *
else:
    from protobuf_py.types import *

class ImgLogger:

  log: Any

class BaseImage(ABC):

  @property
  def data(self) -> np.ndarray:
    raise NotImplementedError()

  @property
  def pngBytesIO(self) -> BytesIO:
    if self._pngBytesIO is None:
      self._pngBytesIO = BytesIO()
      PILImage.fromarray(self.data).save(self._pngBytesIO, format="PNG")

    return self._pngBytesIO

  @property
  def name(self) -> str:
    raise NotImplementedError()

  @property
  def fullData(self) -> np.ndarray:
    '''
      Return the full image data (for subclasses like MiniFileImage or ThumbnailImage) equivalent to self.data for
      FileImage and DataImage
    '''
    raise NotImplementedError()

  def add_circle(self, centerR, centerC, radius):
      rr, cc = draw.circle_perimeter(centerR, centerC, radius)

      self.data[rr, cc] = [255, 0, 0]

  def get_circle_context(self, cr, cc, r, s=2):
      newIm = np.copy(self.fullData)
      row, col = draw.circle_perimeter(cr, cc, r)
      newIm[row, col] = [255, 0, 0]

      return DataImage(
          newIm[
              max(cr - s * r, 0) : min(cr + s * r, newIm.shape[0]),
              max(cc - s * r, 0) : min(cc + s * r, newIm.shape[1]),
              :,
          ]
      )

  def get_circle_colour(self, cr, cc, r):
      rows, cols = draw.disk((cr, cc), r)

      # colour = np.mean(self.data[rows, cols], axis=(0, 1))
      colour = np.mean(self.data[rows, cols], axis=0)

      return colour

  def get_circle_stats(self, cr, cc, r) -> PickStats:

      # import pdb; pdb.set_trace()
      rows, cols = draw.disk((cr, cc), r)

      mu = np.mean(self.fullData[rows, cols], axis=0)
      sigma = np.std(self.fullData[rows, cols], axis=0)

      ps = PickStats()
      ps.mu_r = mu[0]
      ps.mu_g = mu[1]
      ps.mu_b = mu[2]
      ps.sigma_r = sigma[0]
      ps.sigma_g = sigma[1]
      ps.sigma_b = sigma[2]

      totSum = np.sum(self.fullData[rows, cols])

      ps.perc_r = np.sum(self.fullData[rows, cols][:, 0]) / totSum
      ps.perc_g = np.sum(self.fullData[rows, cols][:, 1]) / totSum
      ps.perc_b = np.sum(self.fullData[rows, cols][:, 2]) / totSum

      return ps

  def get_colour_display(self, cr, cc, r):
      # colour = self.get_circle_colour(cr, cc, r)
      ps = self.get_circle_stats(cr, cc, r)
      colour = np.array([ps.mu_r, ps.mu_g, ps.mu_b])
      ImgLogger.log("Got mean colour for display: ", colour)

      rows, cols = draw.disk((cr, cc), r)

      im = np.full((2 * r, 2 * r, 3), 255, dtype=self.fullData.dtype)

      irows, icols = draw.disk((r, r), r)

      im[irows, icols] = self.fullData[rows, cols]

      im[:, :r] = colour

      return DataImage(im)

  def to_png_bytes(self):

      with BytesIO() as stream:

          pIm = PILImage.fromarray(self.data)
          pIm.save(stream, format="PNG")

          return stream.getvalue()

  def to_b64_png(self):
      return base64.b64encode(self.to_png_bytes()).decode("ascii")

  def show(self):
      io.imshow(self.data)
      io.show()


class FileImage(BaseImage):

    fname: str
    # fileDownsample: int = 2 # downsample images when reading from files

    _data: np.ndarray
    virtualFileName: str
    _pngBytesIO: BytesIO

    def __init__(self, fname):
        # if data is None:
        #     try:
        #         self._data = io.imread("./data/sample.png")
        #     except:
        #         print("sample.png not found, initialising empty Image")
        #         self._data = np.zeros((10, 10, 3))
        # else:
        #     self.data = data

        self.fname = fname
        self.virtualFileName = None
        self._pngBytesIO = None
        self._data = None

    @property
    def data(self):
      if self._data is None:
        ImgLogger.log('Opening', self.fname)
        # ImgLogger.log('WARNING: IMAGES ARE BEING DOWNSAMPLED')
        # self._data = io.imread(self.fname)[:: self.fileDownsample, :: self.fileDownsample]
        self._data = io.imread(self.fname)

      return self._data

    @property
    def fullData(self):
      return self.data

    @property
    def pngBytesIO(self):
      if self._pngBytesIO is None:
        self._pngBytesIO = BytesIO()
        PILImage.fromarray(self.data).save(self._pngBytesIO, format="PNG")

      return self._pngBytesIO

    @property
    def name(self) -> str:
      return self.fname

    @classmethod
    def from_img_file(cls, fname):
        return cls(data=io.imread(fname))

class ThumbnailImage(BaseImage):

  _srcImg: BaseImage

  _data: np.ndarray
  _pngBytesIO: BytesIO

  def __init__(self, srcImg: BaseImage):
    self._srcImg = srcImg
    self._data = None
    self._pngBytesIO = None

  @property
  def data(self) -> np.ndarray:
    if self._data is None:
      self._data = np.asarray(self._srcImg.data[::8, ::8], order='C')

    return self._data

  @property
  def fullData(self) -> np.ndarray:
    return self._srcImg.fullData

  @property
  def pngBytesIO(self) -> BytesIO:
    if self._pngBytesIO is None:
      self._pngBytesIO = BytesIO()
      PILImage.fromarray(self.data).save(self._pngBytesIO, format="PNG")

    return self._pngBytesIO

  @property
  def name(self) -> str:
    return 'thumbnail_' + self._srcImg.name

class MiniFileImage(BaseImage):

  _srcImg: BaseImage
  _downsampleFactor: int

  _data: np.ndarray
  _pngBytesIO: BytesIO

  def __init__(self, srcImg: BaseImage, downsampleFactor: int = 4):
    self._srcImg = srcImg
    self._downsampleFactor = downsampleFactor

    self._data = None
    self._pngBytesIO = None

  @property
  def data(self) -> np.ndarray:
    if self._data is None:
      self._data = np.asarray(self._srcImg.data[::self._downsampleFactor, ::self._downsampleFactor], order='C')

    return self._data

  @property
  def fullData(self) -> np.ndarray:
    return self._srcImg.data

  @property
  def name(self) -> str:
    return 'downsampled_' + self._srcImg.name.__str__()


class DataImage(BaseImage):

  _data: np.ndarray
  _pngBytesIO: BytesIO
  _name: str

  def __init__(self, data: np.ndarray, name: str = None):
    self._data = data
    self._pngBytesIO = None

    if name is None:
      name = uuid.uuid1().__str__() + '.png'

    self._name = name

  @property
  def data(self) -> np.ndarray:
    return self._data

  @property
  def fullData(self) -> np.ndarray:
    return self.data

  # @property
  # def pngBytesIO(self) -> BytesIO:
  #   if self._pngBytesIO is None:
  #     self._pngBytesIO = BytesIO()
  #     PILImage.fromarray(self.data).save(self._pngBytesIO, format="PNG")

  #   return self._pngBytesIO

  @property
  def name(self) -> str:
    return self._name


# if __name__ == "__main__":
#     img = Image()
#     cr = 294
#     cc = 484
#     r = 73


class ImageFolder:

    downsample: int = 2
    images: List[BaseImage]
    thumbnails: List[BaseImage]
    dir_path: str

    def __init__(self, dir_path: str, images: List[BaseImage]):
        self.dir_path = dir_path
        # self.images = images
        self.thumbnails = [ThumbnailImage(img) for img in images]
        self.images = [MiniFileImage(img) for img in images]

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
            fname: str = res + "/" + scan

            if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
              ImgLogger.log(fname, " is not an image file. Ignoring")
            else:
              images.append(FileImage(fname))
            # print("opening: ", fname)
            # try:
            #     scanData = io.imread(fname)
            # except:
            #     print("Failed to open", fname)
            #     continue

            # print("finished imread")
            # print("WARNING: IMAGES ARE BEING DOWNSIZED")
            # images.append(Image(scanData[:: cls.downsample, :: cls.downsample], scan))
            # scanThumb = transform.resize(scanData, (scanData.shape[0] // 10, scanData.shape[1] // 10), anti_aliasing=True)
            # scanThumb = Image(np.asarray(scanData[::8, ::8], order='C'))
            # thumbnails.append({
            #     'fileName': scan,
            #     'img': base64.b64encode(scanThumb.to_png_bytes()).decode('ascii'),
            # })

        return cls(res, images)

    # def register_with_manager(self, imgMan: 'ImageDataManager'):
    #   for img in self.images:
    #     vfn = imgMan.ensure_image_stored(img)
    #     # img.virtualFileName = vfn
    #   for tn in self.thumbnails:
    #     vfn = imgMan.ensure_image_stored(tn)
        # tn.virtualFileName = vfn

    def register_images_on_session(self, session: 'Session'):
      for img in self.images:
        session.nameToImage[img.name] = img
      for img in self.thumbnails:
        session.nameToImage[img.name] = img

    # def get_raw_thumbnails(self):
      # return [
      #   Image(np.asarray(img.data[::8, ::8], order="C"))
      #   for img in self.images
      # ]
      # return [ThumbnailImage(img) for img in self.images]

    # def get_thumbnails(self):
    #     return [
    #         {
    #             "fileName": img.fname,
    #             "img": base64.b64encode(
    #                 Image(np.asarray(img.data[::8, ::8], order="C")).to_png_bytes()
    #             ).decode("ascii"),
    #         }
    #         for img in self.images
    #     ]

    def get_image_with_fname(self, fname: str) -> BaseImage:
        return [i for i in self.images if i.fname == fname][0]

    def get_ScanFolder_msg(self) -> ScanFolder:

        sf = ScanFolder()

        for img, tn in zip(self.images, self.thumbnails):
          fi = FolderImage()
          fi.file_name = img.name
          fi.thumbnail_img_v_f_n = tn.name

          sf.folder_images.append(fi)

        return sf



class BlotchCircle:

    id: int
    srcImage: BaseImage
    centerRow: float
    centerCol: float
    radius: float
    context: BaseImage
    compare: BaseImage
    pickStats: PickStats

    def __init__(
        self,
        id: int,
        srcImage: BaseImage,
        centerRow: float,
        centerCol: float,
        radius: float,
        context: BaseImage,
        compare: BaseImage,
        pickStats: PickStats,
    ):
        self.id = id
        self.srcImage = srcImage
        self.centerRow = centerRow
        self.centerCol = centerCol
        self.radius = radius
        self.context = context
        self.compare = compare
        self.pickStats = pickStats

    @classmethod
    def from_selected_circle(
        cls, id: int, centerRow: float, centerCol: float, radius: float, image: BaseImage
    ):

        context = image.get_circle_context(centerRow, centerCol, radius)
        compare = image.get_colour_display(centerRow, centerCol, radius)
        # avgColour = image.get_circle_colour(centerRow, centerCol, radius)

        return cls(
            id,
            image,
            centerRow,
            centerCol,
            radius,
            context,
            compare,
            image.get_circle_stats(centerRow, centerCol, radius),
        )

    def get_clipboard_str(self):
      pc = self.pickStats
      return '\t'.join(
        str(x) for x in [pc.mu_r ,pc.mu_g, pc.mu_b, pc.perc_r, pc.perc_g, pc.perc_b, pc.sigma_r, pc.sigma_g, pc.sigma_b]
      )

    def register_imgs_on_session(self, session: 'Session'):
      session.nameToImage[self.context.name] = self.context
      session.nameToImage[self.compare.name] = self.compare

    def get_ReadBlotch_msg(self) -> ReadBlotch:
      rb = ReadBlotch()

      pc = PickedCircle()
      pc.center_row = self.centerRow
      pc.center_col = self.centerCol
      pc.radius = self.radius
      pc.img_file_name = self.srcImage.name

      rb.circle = pc
      rb.stats = self.pickStats
      rb.context_v_f_n = self.context.name
      rb.compare_v_f_n = self.compare.name
      rb.blotch_i_d = self.id

      return rb


class ImageSession:

    image: BaseImage

    blotchCircles: List[BlotchCircle]
    nextBlotchId: int

    def __init__(self, image: BaseImage) -> None:
        self.image = image

        self.blotchCircles = []
        self.nextBlotchId = 0

    def add_circle(self, centerRow: float, centerCol: float, radius: float):
        self.blotchCircles.append(
            BlotchCircle.from_selected_circle(
                self.nextBlotchId, centerRow, centerCol, radius, self.image
            )
        )
        self.nextBlotchId += 1

    def remove_blotch(self, id: int):
        # import pdb; pdb.set_trace()
        for idx, bc in enumerate(self.blotchCircles):
            if bc.id == id:
                self.blotchCircles.pop(idx)
                return

    def get_clipboard_str(self) -> str:
      return '\n'.join(bc.get_clipboard_str() for bc in self.blotchCircles)

    def get_clipboard_content_msg(self) -> ClipboardContent:
      cc = ClipboardContent()

      for bc in self.blotchCircles:
        cc.rows.append(bc.pickStats)
        cc.blotch_i_ds.append(bc.id)

      return cc

    def get_ActiveImage_msg(self) -> ActiveImage:

      ai = ActiveImage()
      ai.file_name = self.image.name
      ai.img_data_v_f_n = self.image.name
      ai.read_blotches = [b.get_ReadBlotch_msg() for b in self.blotchCircles]
      ai.downsample_factor = 1 if type(self.image) is not MiniFileImage else self.image._downsampleFactor

      return ai

# class ImageDataManager:

#   _imagesByName: Dict[str, BaseImage]

#   def __init__(self) -> None:
#       super().__init__()

#       self._images = {}
#       self._image_to_vfn = {}

#   def ensure_image_stored(self, img: BaseImage) -> str:

#     if img in self._image_to_vfn:
#       return self._image_to_vfn[img]

#     # virtualFile = BytesIO()
#     # PILImage.fromarray(img.data).save(virtualFile, format="PNG")

#     vfn = uuid.uuid1().__str__() + ".png"
#     self._images[vfn] = img
#     self._image_to_vfn[img] = vfn
#     return vfn

#   def get_img(self, vfn: str) -> BytesIO:
#     if vfn not in self._images:
#       ImgLogger.log('Error: requested vfn {} not recognized'.format(vfn))
#       return BytesIO()
#     return self._images[vfn].pngBytesIO


class Session:

    imgFolder: ImageFolder
    currImgSession: ImageSession
    # imgDataManager: ImageDataManager
    nameToImage: Dict[str, BaseImage]
    currSelectedImgIdx: int

    def __init__(self) -> None:
        self.imgFolder = None
        self.currImgSession = None
        self.currSelectedImgIdx = 0
        self.nameToImage = {}

    def set_imgFolder(self, imgFolder: ImageFolder):
        self.imgFolder = imgFolder
        # todo: delete old img folder

    def set_currImgSession(self, imgSess: ImageSession):
      self.currImgSession = imgSess

    def get_UIState_msg(self) -> UIState:
      uiState = UIState()
      uiState.open_folder = self.imgFolder.get_ScanFolder_msg()
      uiState.selected_folder_img_idx = self.currSelectedImgIdx
      uiState.active_image = self.currImgSession.get_ActiveImage_msg()
      uiState.clipboard_content = self.currImgSession.get_clipboard_content_msg()

      ImgLogger.log('Created UIState:', str(uiState))

      return uiState

    def get_image_by_name(self, name: str) -> BaseImage:
      if name not in self.nameToImage:
        ImgLogger.log('Error: requested image name {} not recognized'.format(name))
        return None
      return self.nameToImage[name]

    def get_image_data_by_name(self, name: str) -> BytesIO:
      if name not in self.nameToImage:
        ImgLogger.log('Error: requested image name {} not recognized'.format(name))
        return BytesIO()

      return self.nameToImage[name].pngBytesIO


