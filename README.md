

Spectrogram accelerator for the LimeSDR-mini:
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/diagram.bmp "Diagram")

Average-pooling reduces the noise of the spectrogram 
and downsamples the datarate to 2.5MB/s, which allows remote deployment by using ARM board and SoapySDR-Remote. 
This repository provides necessary docker images.

NOTE: Your LimeSDR-Mini needs to have a cooling solution, see below for an example.

# Running the driver on ARM devices

Install Docker:

`curl -fsSL https://get.docker.com | sh`

For the first time, flash the FPGA:

`docker run -it --privileged soapy_fft LimeUtil --fpga=LimeSDR-Mini_GW/LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd`

You can always restore the default image by running:

`docker run -it --privileged --net=host soapy_fft LimeUtil --update`

Start the SoapySDR-Remote server (serves FFTs instead of IQ):

`docker run -it --privileged --net=host gasparka/soapy_fft_arm`

Test that the server is discoverable on a client machine:

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
* Raspberry Pi 3

# Realtime GUI

This is a Python GUI that plots the FFT frames from the remote diver in real-time, use 'Space' 
to pause the stream.

Turning on WiFi on my mobile:
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/wify.gif "Wify")

Run with:
`docker run -it --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" gasparka/spectrogram_gui`

There is also an ARM build `gasparka/spectrogram_gui:arm`, but it is quite slow.

# Cooling the LimeSDR-mini


Simplest way of cooling your Lime is to attach it to a piece of metal by using a 'thermal pad':

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9411.JPG)
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9408.JPG)

# Accuracy vs floating-point model


Accelerator is implemented in 18-bit fixed-point format, thus it might be interesting
to compare the accuracy against a floating-point model.


Here is a comparision with high-power input signal:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/vs_high.png)

In general the result is good, except for the one 'phantom' peak, which is due to the 9-bit twiddle
factors used in the FFT core. Note that this only happens when you have a very high power concentrated into one FFT bin.

Here is a comparision with low-power input signal:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/vs_low.png)

Result is decent, taking into account that the input has only 2-3 bits of useful information.

# Sources

Gateware sources can be found here:
https://github.com/gasparka/LimeSDR-Mini_GW/tree/fpga_fft

There is also a fork of LimeSuite that enables oversampling and has various hacks
related to the custom FPGA image:
https://github.com/gasparka/LimeSuite/tree/fpga_fft



