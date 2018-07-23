import numpy as np
import SoapySDR
from SoapySDR import *  # SOAPY_SDR_ constants
import sys

fft_size = 512
sdr_device = SoapySDR.Device({'driver': 'remote'})
sdr_device.setSampleRate(SOAPY_SDR_RX, 0, 1e6)
rx_buff = np.empty(shape=fft_size, dtype=np.int32)

# rx_stream = sdr_device.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, {'remote:mtu': '2048', "remote:scalar": "1024"})
rx_stream = sdr_device.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, [0])
sdr_device.activateStream(rx_stream)

while True:
    sr = sdr_device.readStream(rx_stream, [rx_buff], fft_size)
    if sr.ret == fft_size:
        break
