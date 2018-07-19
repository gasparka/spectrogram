# http://amyboyle.ninja/Pyqtgraph-live-spectrogram
import atexit
import multiprocessing
import queue
import signal
import sys
import time
from ctypes import c_bool
from multiprocessing import Queue

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from skimage.exposure import exposure
from fft_reader import FFTReader

import matplotlib.pyplot as plt

from util import cmapToColormap

PACKETS = 2000
PACKETS_PER = PACKETS // 20


class ImageMaker(multiprocessing.Process):
    output_queue = Queue()

    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.alive = multiprocessing.Value(c_bool, True, lock=False)
        self.img_array = np.zeros(shape=(PACKETS, 512))

    def run(self):
        while self.alive.value:
            try:
                fft = FFTReader.output_queue.get(timeout=10)
                self.img_array = np.vstack([self.img_array[PACKETS_PER:], fft])
                # p2, p98 = np.percentile(self.img_array, (2, 98))
                # ret = exposure.rescale_intensity(self.img_array, in_range=(p2, p98))
                ret = self.img_array / self.img_array.max()
                ImageMaker.output_queue.put(ret)
            except KeyboardInterrupt:
                pass

        while not ImageMaker.output_queue.empty():
            ImageMaker.output_queue.get()

        print('ImageMaker died!')


class SpectrogramWidget(pg.PlotWidget):
    def __init__(self):
        super(SpectrogramWidget, self).__init__()

        self.img = pg.ImageItem()
        self.addItem(self.img)

        pos, rgba_colors = zip(*cmapToColormap(plt.get_cmap("viridis")))
        # Set the colormap
        pgColormap = pg.ColorMap(pos, rgba_colors)
        lut = pgColormap.getLookupTable()
        self.img.setLookupTable(lut)
        self.img.setLevels([0, 1])

        # freq = np.arange((CHUNKSZ / 2) + 1) / (float(CHUNKSZ) / FS)
        # yscale = 1.0 / (self.img_array.shape[1] / freq[-1])
        # self.img.scale((1. / FS) * CHUNKSZ, yscale)

        self.setLabel('left', 'Frequency', units='Hz')

        self.last_call = time.time()
        self.show()

        self.img_array = np.zeros(shape=(PACKETS, 512))

    # @profile
    def main(self):
        while not FFTReader.output_queue.empty():
            fft = FFTReader.output_queue.get()
            self.img_array = np.vstack([self.img_array[PACKETS_PER:], fft])

        p2, p98 = np.percentile(self.img_array, (2, 98))
        ret = exposure.rescale_intensity(self.img_array, in_range=(p2, p98))

        self.img.setImage(ret, autoLevels=False)



if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL) # ctrl-c can kill QT event loop!
    app = QApplication(sys.argv)

    fft_reader = FFTReader(PACKETS_PER)
    fft_reader.start()

    # image_maker = ImageMaker()
    # image_maker.start()

    w = SpectrogramWidget()

    t = QtCore.QTimer()
    t.timeout.connect(w.main)
    t.start(0)

    app.exec_()
    fft_reader.alive.value = False
    fft_reader.join()

    # image_maker.alive.value = False
    # fft_reader.join()
