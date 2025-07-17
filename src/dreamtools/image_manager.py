import copy

_all_ = ['ImageManager']
# -*- coding: utf-8 -*-
# project/dreamtools-dreamgeeker/image_manager.py

import os
from io import BytesIO

from PIL import Image, ImageFile, ImageDraw
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import ImageFileDirectory_v2

from . import file_manager
from .controller_manager import ControllerEngine
from .tracking_manager import TrackingManager

TYPE_IMG_JPEG = 'JPEG'
TYPE_IMG_PNG = 'PNG'
TYPE_IMG_GIF = 'GIF'
TYPE_IMG_WEBP = 'WEBP'

"""
Class CImagine
=============================

Class permettant le traitement d'une image png convertit en jpg avec prise en charge de la transparence (fond blanc)


pathfile : dreamtools-dreamgeeker/pyimaging

"""

MAX_SIZE = 640
MIN_SIZE = 200

class ImageManager(object):
    size_max:int
    size_thumb_max:int
    
    def __init__(self, src, dest, size_max=MAX_SIZE, size_thumb_max=MIN_SIZE):
        """
        Preparation image  pour traitement
        ==================================
        Les images sont convertit au format JPEG

        :param int size_max: taille maximum d'une image
        :param int size_thumb_max: taille miniature et minimum

        """
        self.extension = file_manager.file_extension(src).upper()

        if self.extension == "JPG":
            self.extension = TYPE_IMG_JPEG

        if self.extension not in [TYPE_IMG_JPEG, TYPE_IMG_PNG, TYPE_IMG_GIF, TYPE_IMG_WEBP]:
            raise ValueError("Format image non supporté")

        self.size_max = size_max
        self.size_thumb_max = size_thumb_max
        
        self.img = Image.open(src)
        self.exif = None

        self._size = self.img.size
        self.format = self.img.format

        self.file = file_manager.file_extension_less(dest)     # on s'assure de retirer l'extension

        self.resize(size_max)
    def __enter__(self):
        return self

    @property
    def _size(self):
        return self.w, self.h

    @_size.setter
    def _size(self, s):
        self.w, self.h = s

    def save_image_jpeg(self, file_name, img=None):
        if img is None:
            img = copy.deepcopy(self.img)  # copie profonde (réplique récursive)

        ImageManager.image_to_rgb(img)
        file_name = f'{file_name}.jpeg'

        if self.exif:
            img.save(file_name, TYPE_IMG_JPEG, exif=self.exif)
        else:
            img.save(file_name, TYPE_IMG_JPEG)

    def image_to_rgb(self):
        if self.img.mode != 'RGB':
            self.img = self.img.convert('RGB')

    def white_background(self):
        """
        Retourne l'image avec un fond blanc appliqué si l'image comporte de la transparence.
        :return: PIL.Image avec fond blanc
        """

        # Si l'image a un canal alpha (RGBA), on l’utilise comme masque
        if self.img.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", self._size, (255, 255, 255))
            bg.paste(self.img, (0, 0), self.img)
            return bg
        return self.img

    def redraw_border(self, shape="rect", wc=False):
        """
            fs = '/home/dreamgeeker/Images/2151910934.jpg'
            fs_out = '/home/dreamgeeker/Images/tests.jpg'

            imager = ImageManager(fs, fs_out.format('circ'))
            imager.img = imager.redraw_border('circ')
            imager.save('png')
            imager = ImageManager(fs, fs_out.format('circ_border'))
            imager.img = imager.redraw_border('circ', True)
            imager.save('png')"""

        padding = 10 if wc else 0
        diameter = 2 * padding
        box = (self.img.width + diameter, self.img.height + diameter)

        if shape == "rect":
            bg = Image.new("RGB", box, (255, 255, 255))
            bg.paste(self.img, (padding, padding))
        else:  # shape == "circ":
            self.img.convert("RGBA")
            bg = Image.new("RGBA", box, (0, 0, 0, 0))
            if wc:
                draw = ImageDraw.Draw(bg)
                draw.ellipse((0, 0, box[0], box[1]), fill=(255, 255, 255, 255))

            # Masque circulaire
            mask = Image.new("L", self.img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, self.img.width, self.img.height), fill=255)

            pos_x = padding
            pos_y =padding

            # Coller l'image sur le cercle blanc au centre
            bg.paste(self.img, (pos_x, pos_y), mask)

        return bg

    def resize(self, size_max=MAX_SIZE, size_min=MIN_SIZE):
        """ Redimensionnement de l'image au format jpg

        :param size_min: taille minimum (carré)
        :param size_max:  taille maximum de l'image

        :return:
        """
        if self.h < size_min or self.w < size_min:
            raise Exception("Image trop petite")
        elif self.h < size_max or self.w < size_max:
            return

        if self.w >= self.h:
            h = self.h * self.size_max // self.w
            w = self.w
        else:
            w = self.w * self.size_max // self.h
            h = self.size_max

        self.img.resize((w, h))

    def generate_thumb(self, s=(MIN_SIZE,MIN_SIZE))->ImageFile:
        """ Thumb Image

        :param tuple[int, int] s: taille image, defaul (200, 200à

        """
        img = self.img.convert('L')
        img.thumbnail(s)
        return img

    def save(self, frm:str|None= None):
        """ Thumb Image
        :param frm:
        """
        frm = frm.lower() if frm else self.extension.lower()
        file_name = self.file + '.' + frm
        self.img.save(file_name, frm.upper())


    def save_thumb_image(self):
        """ Thumb Image
        """
        thumb = self.generate_thumb()
        self.save_image_jpeg(self.file + "_thumb", thumb)

    def protected(self, artist, description):
        """Ajoute un nom d'artist et le copyright d'une image"""

        _TAGS_r = dict(((v, k) for k, v in TAGS.items()))

        # Image File Directory
        ifd = ImageFileDirectory_v2()
        ifd[_TAGS_r["Artist"]] = artist
        ifd[_TAGS_r["Copyright"]] = 'Tous droits reserves'
        ifd[_TAGS_r["Description"]] = description

        out = BytesIO()
        ifd.save(out)

        self.exif = b"Exif\x00\x00" + out.getvalue()
        self.img.save(self.file, TYPE_IMG_JPEG, exif=self.exif)

    @staticmethod
    def directory_parsing(main_directory:str):
        """
        Redimensionne toutes les images contenu dans un répertoire donné + thumb
        :param main_directory:
        """
        for f in os.listdir(main_directory):
            f_path = os.path.join(main_directory, f)
            if os.path.isfile(f_path):
                imager = ImageManager(f_path, f_path)
                imager.save()
                imager.save_thumb_image()


    @staticmethod
    def treat_uploading(fs, fp):
        """
        Enregistrement d'une image uploaded (byte)

        :param file fs: filestream from flask request
        :param str fp: filepath d'enregistrement
        :return:
        """
        import uuid

        tmp = uuid.uuid1().int >> 64
        tmp_image = file_manager.path_build(ControllerEngine.TMP_DIR, str(tmp))

        try:
            TrackingManager.flag(f'[imgrecorder] Image temp recording : {tmp}')
            fs.save(tmp_image)

            TrackingManager.flag(f'[imgrecorder] Image treatment: {tmp} | {fp}')
            o = ImageManager(tmp_image, fp)
            o.save()

            TrackingManager.flag('[imgrecorder] Image thumbing')
            o.save_thumb_image()

            file_manager.remove_file(tmp_image)

            return True
        except Exception as e:
            TrackingManager.exception_tracking(e, '[imgrecorder] Aïe')
            return False