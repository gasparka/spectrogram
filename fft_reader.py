import multiprocessing
from multiprocessing import Queue

import numpy as np
import SoapySDR
from SoapySDR import *  # SOAPY_SDR_ constants
import sys


class FFTReader(multiprocessing.Process):
    sdr_device = None
    output_queue = Queue()

    def __init__(self):
        multiprocessing.Process.__init__(self)

        self.fs = 40e6
        self.fc = 2420e6
        self.bandwidth = self.fs

        self.fft_size = 512
        self.rx_buff = np.empty(shape=self.fft_size, dtype=np.int32)

    def init_devices(self):
        args = dict(driver='lime', cacheCalibrations='1')
        self.sdr_device = SoapySDR.Device(args)

        if self.sdr_device is None:
            print("[ERROR] No SDR device!", file=sys.stderr)
            return

        self.sdr_device.setAntenna(SOAPY_SDR_RX, 0, 'LNAH')
        self.sdr_device.setFrequency(SOAPY_SDR_RX, 0, self.fc)
        self.sdr_device.setSampleRate(SOAPY_SDR_RX, 0, self.fs)
        self.sdr_device.setBandwidth(SOAPY_SDR_RX, 0, self.bandwidth)

        self.sdr_device.setDCOffsetMode(SOAPY_SDR_RX, 0, True)

        if self.sdr_device.hasGainMode(SOAPY_SDR_RX, 0):
            self.sdr_device.setGainMode(SOAPY_SDR_RX, 0, False)

        self.rx_stream = self.sdr_device.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16)
        self.sdr_device.activateStream(self.rx_stream)

    def get_fft(self):

        while True:
            sr = self.sdr_device.readStream(self.rx_stream, [self.rx_buff], self.fft_size)
            if sr.ret == self.fft_size:
                break

        # throw away safety region
        # ret = self.rx_buff[self.throwaway_packets:]
        ret = self.rx_buff
        # throw away pack_start bit (LSB)
        ret = ret >> 1
        # convert to floats and rescale
        ret = ret.astype(float) * 2e-36
        # convert to spectrogram format
        # ret = ret.T

        return ret

    def run(self):
        self.init_devices()
        while True:
            fft_pack = self.get_fft()
            FFTReader.output_queue.put(fft_pack)
            print(len(FFTReader.output_queue))