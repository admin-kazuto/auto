import os
import io
import base64

import numpy as np
from PIL import Image

from hangar.external import BasePlugin


class HangarPIL(BasePlugin):
    def __init__(self):
        provides = ['load', 'save', 'board_show']
        accepts = ['jpg', 'jpeg', 'png', 'ppm', 'bmp', 'pgm', 'tif', 'tiff', 'webp']
        super().__init__(provides, accepts)

    def load(self, fpath, height=None, width=None):
        """
        Load an image from file and returns the numpy array of the image along
        with the name which will be used by hangar as sample name

        Parameters
        ----------
        fpath : str
           File path. eg: path/to/test.jpg
        height : int, float
            height of the image
        width : int, float
            Width of the image


        Notes
        -----
        Files are read using the Python Imaging Library.
        See PIL docs [1]_ for a list of supported formats.

        References
        ----------
        .. [1] http://pillow.readthedocs.org/en/latest/handbook/image-file-formats.html
        """
        im = Image.open(fpath)
        if height and width:
            shape = (int(height), int(width))
            im = im.resize(shape)
        return np.array(im), self.sample_name(fpath)

    def save(self, arr, outdir, sample_n, format_str, **kwargs):
        """
        Save an image to disk.

        Parameters
        ----------
        fname : str or file-like object
            Name of destination file.
        arr : ndarray of uint8 or float
            Array (image) to save.  Arrays of data-type uint8 should have
            values in [0, 255], whereas floating-point arrays must be
            in [0, 1].
        format_str: str
            Format to save as, this is defaulted to PNG if using a file-like
            object; this will be derived from the extension if fname is a string
        kwargs: dict
            Keyword arguments to the Pillow save function (or tifffile save
            function, for Tiff files). These are format dependent. For example,
            Pillow's JPEG save function supports an integer ``quality`` argument
            with values in [1, 95], while TIFFFile supports a ``compress``
            integer argument with values in [0, 9].

        Notes
        -----
        Use the Python Imaging Library.
        See PIL docs [1]_ for a list of other supported formats.

        References
        ----------
        .. [1] http://pillow.readthedocs.org/en/latest/handbook/image-file-formats.html
        """
        # default to PNG
        if format_str is None:
            format_str = "PNG"
        fpath = os.path.join(outdir, f"{sample_n}.{format_str}")

        if arr.dtype.kind == 'b':
            arr = arr.astype(np.uint8)

        if arr.ndim not in (2, 3):
            raise ValueError("Invalid shape for image array: %s" % (arr.shape, ))

        if arr.ndim == 3:
            if arr.shape[2] not in (3, 4):
                raise ValueError("Invalid number of channels in image array.")

        img = Image.fromarray(arr)
        img.save(fpath)

    def board_show(self, arr, format_str=None, **kwargs):
        """
        Conver the numpy array from hangar to image and return that as base64
        encoded to display in hangarboard

        Parameters
        ----------
        arr : ndarray of uint8 or float
            Array (image) to save.  Arrays of data-type uint8 should have
            values in [0, 255], whereas floating-point arrays must be
            in [0, 1].
        format_str: str
            Format to save as, this is defaulted to PNG if using a file-like
            object; this will be derived from the extension if fname is a string
        kwargs: dict
            Keyword arguments to the Pillow save function (or tifffile save
            function, for Tiff files). These are format dependent. For example,
            Pillow's JPEG save function supports an integer ``quality`` argument
            with values in [1, 95], while TIFFFile supports a ``compress``
            integer argument with values in [0, 9].
        """
        buffer = io.BytesIO()
        self.save(buffer, arr, format_str, **kwargs)
        buffer.seek(0)
        decoded = base64.b64encode(buffer.read()).decode('ascii')
        return f"image/{format_str};base64,{decoded}"
