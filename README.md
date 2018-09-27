

Spectrogram accelerator for the LimeSDR-mini:
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/diagram.bmp "Diagram")

Average-pooling reduces the noise of the spectrogram 
and downsamples the output-rate to 2.5MB/s, which makes it possible to deploy to remote location by using
some ARM board and SoapySRD Remote integration. This repository provides an Docker image to 
run this setup super easily!

This repository contains 2 applications. First the driver with an SoapySDR integraton and a realtime GUI.

# 1. Remote driver - Running the remote driver on ARM devices
Pair your LimeSDR-Mini with a cheap ARM board to turn it into a remote FFT server.

Install Docker:

`curl -fsSL https://get.docker.com | sh`

For the first time, you need to write the FPGA image to the flash:
`docker run -it --privileged --net=host soapy_fft LimeUtil --fpga=LimeSDR-Mini_GW/LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd`

You can always restore the default image with running:
`docker run -it --privileged --net=host soapy_fft LimeUtil --update`

Setup the device as an SoapySDR-Remote server:

`sudo docker run -it --privileged --net=host gasparka/soapy_fft_arm`

Test that the server works by running on client machine:

```
~> SoapySDRUtil --find="driver=remote"
######################################################
## Soapy SDR -- the SDR abstraction library
######################################################

Found device 0
  addr = 24607:1027
  driver = remote
  label = LimeSDR Mini [USB 3.0] 1D40EC49F23932
  media = USB 3.0
  module = FT601
  name = LimeSDR Mini
  remote = tcp://192.168.1.136:55132
  remote:driver = lime
  serial = 1D40EC49F23932
```

See the NOTEBOOK on how to get the FFT frames from the server and plot them.

Tested on:
* ODROID-XU4
* Rasberry Pi 3

# 2. Realtime GUI
This is a Python GUI that plots the FFT frames from the remote diver in real-time.

Turning on WiFi on my mobile:
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/wify.gif "Wify")

Idea is to put most screen space for time_axsis, so you can see even short time events. For
example the Bluetooth transmissions:

To use it you must have a Remote Driver working somewhere and then easiest is to
use the dockerized version like this:

`docker run -it --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" gasparka/spectrogram_gui`

This GUI is also built for ARM targets, specify the 'gasparka/spectrogram_gui:arm' tag to try it out.

Heatsinking the LimeSDR-mini
----------------------------

Simple way of heatsinking your Lime by using the 'thermal pad' and a piece of metal.

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9411.JPG)
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9408.JPG)

Accuracy compared to model
--------------------------

FPGA accelerator is implemented in mostly 18-bit fixedpoint format, thus it might be interesting to compare it
againts the floating point model.

Here is a comparision plot on high-power input signal:

In general the result is good, execpt for one of the 'phantom' peaks, which is due to the 9-bit twiddle
factors used in the FFT core.

Here is a plot for a very low power signal:

Here we can see that the 8192 point FFT is a bit too much for the 18-bit format, but good enough for visuals.

