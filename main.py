# http://amyboyle.ninja/Pyqtgraph-live-spectrogram
import multiprocessing
import queue
import sys
import time
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
        self.img_array = np.zeros(shape=(PACKETS, 512))

    def run(self):
        while True:
            try:
                fft = FFTReader.output_queue.get(timeout=1)
                self.img_array = np.vstack([self.img_array[PACKETS_PER:], fft])
                # p2, p98 = np.percentile(self.img_array, (2, 98))
                # ret = exposure.rescale_intensity(self.img_array, in_range=(p2, p98))
                ret = self.img_array / self.img_array.max()
                ImageMaker.output_queue.put(ret)
            except queue.Empty:
                print("[INFO] IQ queue is empty!", file=sys.stderr)


class SpectrogramWidget(pg.PlotWidget):
    read_collected = QtCore.pyqtSignal(np.ndarray)

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


    def main(self):
        # while True:
        # print('LOL')
        # ss = time.time()
        try:
            image = ImageMaker.output_queue.get(timeout=1)
            self.img.setImage(image, autoLevels=False)
        except queue.Empty:
            print("[INFO] IQ queue is empty!", file=sys.stderr)
            # continue
        ee = time.time()
        print(f'{1 / (ee-self.last_call)} fps')

        self.last_call = time.time()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fft_reader = FFTReader(PACKETS_PER)
    fft_reader.start()

    image_maker = ImageMaker()
    image_maker.start()

    w = SpectrogramWidget()
    # w.main()

    # time (seconds) between reads

    t = QtCore.QTimer()
    t.timeout.connect(w.main)
    t.start(0)

    app.exec_()
