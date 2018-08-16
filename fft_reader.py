import logging
import multiprocessing
from collections import deque
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

        self.fft_size = 512
        self.rx_buff = np.empty(shape=(self.packet_size, self.fft_size), dtype=np.int32)

        # AGC
        self.agc_enabled = True
        self.gain_level = 0
        self.max_power_history = deque(maxlen=512)

    def init_devices(self):
        self.sdr_device = SoapySDR.Device({'driver': 'lime'})

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

    def automatic_gain_control(self, ffts):
        if not self.agc_enabled:
            return

        def get_max_power():
            try:
                return np.max(list(self.max_power_history))
            except ValueError:  # empty list?
                return 0.0

        old_gain = self.gain_level

        # take maximum IQ float value
        max_fft_sum = np.max(np.sum(ffts, axis=0))
        self.max_power_history.append(max_fft_sum)

        max_power = get_max_power()
        # TODO: should ignore the bins with DC? or not
        if len(self.max_power_history) == self.max_power_history.maxlen:
            # print(max_power)
            if max_power > 1e-27:
                self.gain_level -= 6
                self.max_power_history.clear()
            elif max_power < 1e-29:
                self.gain_level += 6
                self.max_power_history.clear()

            if self.gain_level > 60:
                self.gain_level = 60
            elif self.gain_level < 0:
                self.gain_level = 0

            if old_gain != self.gain_level:
                log.info(f'Gain {old_gain} -> {self.gain_level}, max_pow: {max_power}')

                if self.gain_level <= 30:
                    gains = {"LNA": self.gain_level, "TIA": 0, "PGA": -12}
                else:
                    gains = {"LNA": 30, "TIA": 0, "PGA": self.gain_level - 30 - 12}

                # set gains
                for gain, value in gains.items():
                    self.sdr_device.setGain(SOAPY_SDR_RX, 0, gain, value)

    def get_fft(self):

        for i in range(self.packet_size):
            sr = self.sdr_device.readStream(self.rx_stream, [self.rx_buff[i]], self.fft_size)
            if sr.ret != self.fft_size:
                log.error('Bad samples from remote!')

        # throw away pack_start bit (LSB)
        ret = self.rx_buff >> 1
        # convert to floats and rescale
        ret = ret.astype(float) * 2e-36

        return ret

    def run(self):
        try:
            self.init_devices()
            while self.alive.value:
                fft_pack = self.get_fft()
                self.automatic_gain_control(fft_pack)
                FFTReader.output_queue.put(fft_pack)
        except KeyboardInterrupt:
            pass

        while not FFTReader.output_queue.empty():
            FFTReader.output_queue.get()

        log.warning('FFTReader died!')