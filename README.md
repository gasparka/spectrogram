# 80MHz bandwidth with LimeSDR-Mini and GQRX
[![Build Status](https://travis-ci.org/gasparka/spectrogram.svg?branch=master)](https://travis-ci.org/gasparka/spectrogram)

![Bluetooth GIF](https://github.com/gasparka/spectrogram/blob/master/doc/demo.gif "Demo")

[LimeSDR-Mini](https://www.crowdsupply.com/lime-micro/limesdr-mini) diagram:

![Block diagram](https://github.com/gasparka/spectrogram/blob/master/doc/lime_and_diagram.jpg "Diagram")

_**Note:** DC-removal is based on [Linear-phase DC Removal Filter](https://www.dsprelated.com/showarticle/58.php) (Dual-MA 1024 taps)_

## Install

Install the helper script to bootstrap the Docker images (Linux PC/ARM architectures):

```pip install spectrogram```

_**Rasbian note:** Use ```pip3```. Executable is installed to ```/home/pi/.local/bin/spectrogram```, which is not on PATH by default._

_**Ubuntu 20 note:** Does not work! Use 18 :)_

## Usage

Invoking ```spectrogram``` does following:
1. If needed, programs the LimeSDR-Mini with FPGA accelerator ( restore with ``spectogram --fpga_restore``)
2. Starts the local 'SoapySDR-Remote' server
3. Starts GQRX

_**Warning:** You should **cool your LimeSDR-Mini**, especially the FPGA. It takes 2.5 minutes for FPGA temperature to rise from 30C to 80C, after which you risk damage!_

Works on RaspberryPi:

![Pi setup](https://github.com/gasparka/spectrogram/blob/master/doc/lime_mini_screen.jpg "lime_mini_screen")

_**Notes:** Current draw was around 1.25A@5V. 5’ TFT-Display created some noise in the spectrogram - this was not a problem with HDMI display.
OTOH HDMI supports higher resolution, which may cap the CPU if GQRX window is too big (updating the waterfall is expensive)._

### Remote usage

Pair your LimeSDR-Mini with RaspberryPi and execute ```spectrogram --server_only``` - this sets up a SoapySDR-Remote server.
Next, on the monitoring device, execute ```spectrogram``` - this scans for remote devices and opens GQRX if one is found.
Network bandwidth will be around 1 MB/s.


## MISC

### Using without GQRX
[See demo notebook](https://github.com/gasparka/spectrogram/blob/master/doc/usage_demo.ipynb)

### Accuracy vs floating-point model

This is a fixed-point accelerator, accuracy against the floating-point model has been verified.


![fix vs float accuracy](https://github.com/gasparka/spectrogram/blob/master/doc/fix_vs_float.png)

[Reproduce](https://github.com/gasparka/pyha/blob/develop/pyha/applications/spectrogram_limesdr/spectrogram_limesdr.ipynb)

### How is 512 point FFT comparable to 131k FFT??
It's about how many samples are averaged e.g. the 131k FFT averages 131k samples - same can be achieved with 512 point FFT and averaging 256 results - 512*256 = 131k.

![132k FFT vs 512 + averaging](https://github.com/gasparka/spectrogram/blob/master/doc/131k_vs_512.png)
[Reproduce](https://github.com/gasparka/spectrogram/blob/master/doc/131k_vs_512.ipynb)

In general this is a trade-off - hardware complexity is reduced, but you will lose ~3dB dynamic range.

### Cooling solutions

#### No cooling

![No cooling](https://github.com/gasparka/spectrogram/blob/master/doc/no_cools.JPG)

Took 5 minutes to go from cold to critical FPGA temperature.

**You will risk damaging your board!**


#### Heat-sink on FPGA

![FPGA sinked](https://github.com/gasparka/spectrogram/blob/master/doc/fpga_cools.JPG)

Temperature is stable at ~65C after 10 minutes.


#### Heat-sink everything

![Massive sink](https://github.com/gasparka/spectrogram/blob/master/doc/all_cools.JPG)

Temperature is stable at ~54C after 20 minutes.
