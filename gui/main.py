import logging
import signal
import sys
import time
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from gui.fft_reader import FFTReader
from gui.util import rescale_intensity
import pickle

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('main')

SCREEN_FFTS = 2000
SCREEN_FFTS_PACKETS = 60
PACKET_SIZE = SCREEN_FFTS // SCREEN_FFTS_PACKETS


class SpectrogramWidget(pg.PlotWidget):
    def __init__(self):
        super(SpectrogramWidget, self).__init__()

        self.img = pg.ImageItem()
        self.addItem(self.img)

        with open('./gui/viridis_lut.pickle', 'rb') as f:
            lut = pickle.load(f)
        self.img.setLookupTable(lut)
        self.img.setLevels([0, 1])

        # set x-axis labels
        xax = self.getAxis('bottom')
        tick_i = range(0, SCREEN_FFTS, SCREEN_FFTS//16)
        time_unit = (1/80e6) * (1024*8*8)
        vals = [f'{x*time_unit:.1f}' for x in tick_i]
        ticks = [list(zip(tick_i, vals))]
        xax.setTicks(ticks)
        self.setLabel('bottom', 'Time')

        # set y-axis labels
        xax = self.getAxis('left')
        vals = ['2.40', '2.41', '2.42', '2.43', '2.44', '2.45', '2.46', '2.47', '2.48']
        tick_i = np.linspace(0, 512, num=len(vals), endpoint=True)
        ticks = [list(zip(tick_i, vals))]
        xax.setTicks(ticks)
        self.setLabel('left', 'Frequency', units='GHz')

        self.last_call = time.time()
        self.show()

        self.img_array = np.zeros(shape=(SCREEN_FFTS, 512))
        self.plot_enabled = True

    def keyPressEvent(self, e):
        from PyQt5.QtCore import Qt
        if e.key() == Qt.Key_Space:
            self.plot_enabled = not self.plot_enabled

    def main(self):
        i = 0
        tmp = []

        while FFTReader.output_queue.qsize() != 0:
            fft = FFTReader.output_queue.get()
            tmp.append(fft)
            i += 1
            if i >= SCREEN_FFTS_PACKETS:
                # have already loaded full screen...
                log.warning('Plotting is slower than FFT interface...throwing away excess buffer..')
                while FFTReader.output_queue.qsize() != 0:
                    FFTReader.output_queue.get()
                break
        if i and self.plot_enabled:
            print(i)
            self.img_array = np.vstack([self.img_array[PACKET_SIZE*i:]] + tmp)
            self.img.setImage(self.img_array, autoLevels=False)


def init():
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # ctrl-c can kill QT event loop!
    app = QApplication(sys.argv)

    fft_reader = FFTReader(PACKET_SIZE)
    fft_reader.start()

    w = SpectrogramWidget()

    t = QtCore.QTimer()
    t.timeout.connect(w.main)
    t.start(0)

    app.exec_()
    fft_reader.alive.value = False
    fft_reader.join()

if __name__ == '__main__':
    init()
