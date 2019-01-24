# Spectrogram (80MHz bandwidth) with LimeSDR and GQRX

![Bluetooth GIF](https://github.com/gasparka/spectrogram/blob/master/doc/demo.gif "Demo")


![Block diagram](https://github.com/gasparka/spectrogram/blob/master/doc/lime_and_diagram.jpg "Diagram")

## Install

This application comes in a docker image (Linux PC/ARM architectures). 
Bootstrapping the image is handled by the ``spectrogram`` executable (```pip install spectrogram```).

_**Note:** Use pip3 on Rasbian. Also, Rasbian fails to add the executable to PATH, use ```/home/pi/.local/bin/spectrogram```_

## Local usage 

Invoking ```spectrogram``` does following:
1. If needed, programs the local LimeSDR-Mini with proper FPGA image ( restore with  ``spectogram --fpga_restore``)
2. Starts the local 'SoapySDR-Remote' server
3. Starts GQRX for spectrogram display

_**Warning:** You should cool your LimeSDR-Mini, especially the FPGA. It takes 2.5 minutes for FPGA temperature to rise from 30C to 80C, after which you risk damage!_

_**Note:** Works on RaspberryPi, but currently the GUI needs optimizations ([#8](https://github.com/gasparka/spectrogram/issues/8))._


## Remote usage

You want to pair your LimeSDR-Mini with RaspberryPi. On the Pi, execute ```spectrogram --server_only```.
Now, on the monitoring device, execute ```spectrogram```. GQRX will start, if the Pi is visible to the monitoring device.

_**Note:** Network bandwidth is around 1 MB/s._

_**Note:** [LimeNet-Micro](https://www.crowdsupply.com/lime-micro/limenet-micro) is ideal for remote applications - it has LimeSDR, RaspberryPi and power-over-ethernet on single board. Work in progress ([#9](https://github.com/gasparka/spectrogram/issues/9))._


## MISC
### Accuracy vs floating-point model

This is a fixed-point accelerator, accuracy against the floating-point model has been verified.


![fix vs float accuracy](https://github.com/gasparka/spectrogram/blob/master/doc/fix_vs_float.png)

[Reproduce](https://github.com/gasparka/pyha/blob/develop/pyha/applications/spectrogram_limesdr/spectrogram_limesdr.ipynb)

### How is 512 point FFT comparable to 131k FFT??
It's about how many samples are averaged. 131k FFT averages 131k samples - same can be achieved with 512 point FFT and averaging 256 results i.e. 512*256 = 131k.

![132k FFT vs 512 + averaging](https://github.com/gasparka/spectrogram/blob/master/doc/131k_vs_512.png)
[Reproduce](https://github.com/gasparka/spectrogram/blob/master/doc/131k_vs_512.ipynb)

In general you lose ~3dB dynamic range. Also, 512 point FFT is much worse at detecting narrow spectral peaks - this could be considered a feature or a bug, depending on the application.

### Cooling solutions

#### No cooling

![No cooling](https://github.com/gasparka/spectrogram/blob/master/doc/no_cools.JPG)
Took 5 minutes to go from cold to critical FPGA temperature. You will risk damaging your board!


#### Heat-sink on FPGA

![FPGA sinked](https://github.com/gasparka/spectrogram/blob/master/doc/fpga_cools.JPG)
Temperature is stable at ~65C after 10 minutes.


#### Heat-sink everything

![Massive sink](https://github.com/gasparka/spectrogram/blob/master/doc/all_cools.JPG)
Temperature is stable at ~54C after 20 minutes.