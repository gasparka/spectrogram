# http://amyboyle.ninja/Pyqtgraph-live-spectrogram
import queue
import sys
import time

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from skimage.exposure import exposure
from fft_reader import FFTReader


class SpectrogramWidget(pg.PlotWidget):
    read_collected = QtCore.pyqtSignal(np.ndarray)

    def __init__(self):
        super(SpectrogramWidget, self).__init__()

        self.img = pg.ImageItem()
        self.addItem(self.img)

        self.img_array = np.random.normal(size=(1000,512))

        # bipolar colormap

        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0, 255, 255, 255], [255, 255, 0, 255], [0, 0, 0, 255], (0, 0, 255, 255), (255, 0, 0, 255)],
                         dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        self.img.setLookupTable(lut)
        # self.img.setLevels([-50, 40])

        # freq = np.arange((CHUNKSZ / 2) + 1) / (float(CHUNKSZ) / FS)
        # yscale = 1.0 / (self.img_array.shape[1] / freq[-1])
        # self.img.scale((1. / FS) * CHUNKSZ, yscale)

        self.setLabel('left', 'Frequency', units='Hz')

        # self.win = np.hanning(CHUNKSZ)
        self.show()

    def update(self, fft):
        # roll down one and replace leading edge with new data
        self.img_array = np.roll(self.img_array, -1, 0)
        self.img_array[-1:] = fft

        p2, p98 = np.percentile(self.img_array.T, (2, 98))
        ret = exposure.rescale_intensity(self.img_array.T, in_range=(p2, p98))

        self.img.setImage(ret.T, autoLevels=True)

    def main(self):
        while True:
        # print('LOL')
            try:
                fft = FFTReader.output_queue.get(timeout=1)
                # fft = np.random.normal(size=512)
                # self.update(fft)
            except queue.Empty:
                print("[INFO] IQ queue is empty!", file=sys.stderr)
                # continue


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fft_reader = FFTReader()
    fft_reader.start()

    w = SpectrogramWidget()
    w.main()

    # time (seconds) between reads

    # t = QtCore.QTimer()
    # t.timeout.connect(w.main)
    # t.start(0.000000000001)  # QTimer takes ms

    app.exec_()