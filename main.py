# http://amyboyle.ninja/Pyqtgraph-live-spectrogram
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui

FS = 44100  # Hz

CHUNKSZ = 1024  # samples


class MicrophoneRecorder():
    def __init__(self, signal):
        self.signal = signal

    def read(self):
        data = np.random.normal(size=CHUNKSZ)
        self.signal.emit(data)


class SpectrogramWidget(pg.PlotWidget):
    read_collected = QtCore.pyqtSignal(np.ndarray)

    def __init__(self):
        super(SpectrogramWidget, self).__init__()

        self.img = pg.ImageItem()
        self.addItem(self.img)

        self.img_array = np.zeros((1000, CHUNKSZ // 2 + 1))

        # bipolar colormap

        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0, 255, 255, 255], [255, 255, 0, 255], [0, 0, 0, 255], (0, 0, 255, 255), (255, 0, 0, 255)],
                         dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        self.img.setLookupTable(lut)
        self.img.setLevels([-50, 40])

        freq = np.arange((CHUNKSZ / 2) + 1) / (float(CHUNKSZ) / FS)
        yscale = 1.0 / (self.img_array.shape[1] / freq[-1])
        self.img.scale((1. / FS) * CHUNKSZ, yscale)

        self.setLabel('left', 'Frequency', units='Hz')

        self.win = np.hanning(CHUNKSZ)
        self.show()

    def update(self, chunk):
        # normalized, windowed frequencies in data chunk

        spec = np.fft.rfft(chunk * self.win) / CHUNKSZ
        # get magnitude

        psd = abs(spec)
        # convert to dB scale

        psd = 20 * np.log10(psd)

        # roll down one and replace leading edge with new data

        self.img_array = np.roll(self.img_array, -1, 0)
        self.img_array[-1:] = psd

        self.img.setImage(self.img_array, autoLevels=False)
        self.img.


if __name__ == '__main__':
    app = QtGui.QApplication([])


    w = SpectrogramWidget()
    w.read_collected.connect(w.update)

    mic = MicrophoneRecorder(w.read_collected)

    # time (seconds) between reads

    interval = FS / CHUNKSZ
    t = QtCore.QTimer()
    t.timeout.connect(mic.read)
    t.start(1000 / interval)  # QTimer takes ms

    app.exec_()