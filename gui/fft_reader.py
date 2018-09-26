import logging
import multiprocessing
from ctypes import c_bool
from multiprocessing import Queue
import numpy as np
import SoapySDR
from SoapySDR import *  # SOAPY_SDR_ constants
import sys

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('FFTReader')


class FFTReader(multiprocessing.Process):
    sdr_device = None
    output_queue = Queue()

    def __init__(self, packet_size):
        multiprocessing.Process.__init__(self)

        self.alive = multiprocessing.Value(c_bool, True, lock=False)
        self.packet_size = packet_size
        # PITFALL ALERT:
        # Sampling rate is known to work for 80e6 and 40e6. This restriction is due to the custom FPGA image.
        # Root cause is the LMS7 RX sampling clock, whose phase depends on the sample rate (see https://github.com/myriadrf/LMS7002M-docs/issues/2)
        self.fs = 80e6
        self.fc = 2440e6
        self.bandwidth = self.fs

        # todo: ideally these should be read from FPGA
        self.fft_size = 512
        self.fixed_gain = 2**-43 # PITFALL ALERT: this needs to change if avgpooling settings or fft size changes!
        self.rx_buff = np.empty(shape=(self.packet_size, self.fft_size), dtype=np.int32)

    def init_devices(self):
        self.sdr_device = SoapySDR.Device({'driver': 'remote'})
        # self.sdr_device = SoapySDR.Device({'driver': 'lime'})

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

        gains = {"LNA": 0, "TIA": 0, "PGA": -12}
        for gain, value in gains.items():
            self.sdr_device.setGain(SOAPY_SDR_RX, 0, gain, value)

        # MTU is hardcoded to get 512 samples i.e. one FFT frame.
        self.rx_stream = self.sdr_device.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, [0],
                                                     {'remote:mtu': '2120', 'remote:prot': 'tcp'})

        assert self.sdr_device.getStreamMTU(self.rx_stream) == self.fft_size

        self.sdr_device.activateStream(self.rx_stream)

    def get_fft(self):

        for i in range(self.packet_size):
            sr = self.sdr_device.readStream(self.rx_stream, [self.rx_buff[i]], self.fft_size)
            if sr.ret != self.fft_size:
                log.error('Bad samples from remote!')

        # convert the fixed point format to floats and decibels
        # TODO: Decibel stuff could be inside FPGA..
        ret = np.log10(self.rx_buff.astype(float) * self.fixed_gain) * 10
        return ret

    def run(self):
        try:
            self.init_devices()
            while self.alive.value:
                fft_pack = self.get_fft()
                FFTReader.output_queue.put(fft_pack)
        except KeyboardInterrupt:
            pass

        while not FFTReader.output_queue.empty():
            FFTReader.output_queue.get()

        log.warning('FFTReader died!')