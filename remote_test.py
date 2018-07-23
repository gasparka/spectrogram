import numpy as np
import SoapySDR
from SoapySDR import *  # SOAPY_SDR_ constants
import sys

fft_size = 512
sdr_device = SoapySDR.Device({'driver': 'remote'})
sdr_device.setSampleRate(SOAPY_SDR_RX, 0, 1e6)

rx_stream = sdr_device.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, [0], {'remote:mtu': '2120', 'remote:prot': 'tcp'})
# rx_stream = sdr_device.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16)
sdr_device.activateStream(rx_stream)
mtu = sdr_device.getStreamMTU(rx_stream)


rx_packs = 2
rx_buff = np.empty(shape=(rx_packs, mtu), dtype=np.int32)

for i in range(rx_packs):
    sr = sdr_device.readStream(rx_stream, [rx_buff[i]], mtu)
    print(sr)
    if sr.ret != mtu:
        print('SHIT!!')

ret = np.hstack(rx_buff)

# find sync bit (LS bit is 1)
sync = 0
for i, x in enumerate(ret):
    if x & 1:
        sync = i
        break
if sync != 0:
    ret = ret[sync:]
    print(f'Sync was lost.. throw away {sync} samples')

n_packets = len(ret) // fft_size











