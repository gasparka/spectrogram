import argparse
import logging
import signal
import subprocess
import sys
import time
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from fft_reader import FFTReader
from util import rescale_intensity
import pickle

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('main')

SCREEN_FFTS = 2000
SCREEN_FFTS_PACKETS = 30
PACKET_SIZE = SCREEN_FFTS // SCREEN_FFTS_PACKETS


class SpectrogramWidget(pg.PlotWidget):
    def __init__(self):
        super(SpectrogramWidget, self).__init__()

        self.img = pg.ImageItem()
        self.addItem(self.img)

        with open('viridis_lut.pickle', 'rb') as f:
            lut = pickle.load(f)
        self.img.setLookupTable(lut)
        self.img.setLevels([0, 1])

        # freq = np.arange((CHUNKSZ / 2) + 1) / (float(CHUNKSZ) / FS)
        # yscale = 1.0 / (self.img_array.shape[1] / freq[-1])
        # self.img.scale((1. / FS) * CHUNKSZ, yscale)

        self.setLabel('left', 'Frequency', units='Hz')

        self.last_call = time.time()
        self.show()

        self.img_array = np.zeros(shape=(SCREEN_FFTS, 512))

    # @profile
    def main(self):
        i = 0
        l = []
        while FFTReader.output_queue.qsize() != 0:
            fft = FFTReader.output_queue.get()
            l.append(fft)
            i += 1
            if i >= SCREEN_FFTS_PACKETS:
                # have already loaded full screen...
                log.warning('Plotting is slower than FFT interface...throwing away excess buffer..')
                while FFTReader.output_queue.qsize() != 0:
                    FFTReader.output_queue.get()
                break

        self.img_array = np.vstack([self.img_array[PACKET_SIZE*i:]] + l)
        print(i)
        p2, p98 = np.percentile(self.img_array, (2, 98))
        ret = rescale_intensity(self.img_array, in_range=(p2, p98))

        self.img.setImage(ret, autoLevels=False)


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
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--fpga_init', help='Description for foo argument', action='store_true')
    parser.add_argument('--fpga_restore', help='Description for foo argument', action='store_true')
    parser.add_argument('--run', help='Description for foo argument', action='store_true')
    args = vars(parser.parse_args())

    if args['fpga_init']:
        log.info('Programming FPGA, takes ~20 sec...')
        subprocess.run(
            ["LimeUtil", "--fpga=./LimeSDR-Mini_GW/LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd"])
        log.info('Please unplug and replug the LimeSDR-Mini...')
    elif args['fpga_restore']:
        log.info('Restoring default LimeSuite FPGA image, takes ~20 sec...')
        subprocess.run(["LimeUtil", "--update"])
    elif args['run']:
        init()
    else:
        init()
