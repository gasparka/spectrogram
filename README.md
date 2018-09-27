Spectrogram accelerator for LimeSDR-mini:
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/diagram.bmp "Diagram")

Average-pooling reduces the noise of the spectrogram 
and downsamples the datarate to 2.5MB/s, which allows remote deployment by using ARM board and SoapySDR-Remote. 
This repository provides the necessary docker images.

NOTE: LimeSDR-Mini needs to have a cooling solution, see below for an example.

# Running the driver on ARM devices

Install Docker:

`curl -fsSL https://get.docker.com | sh`

For the first time, flash the FPGA (drop the ':arm' tag to run on non-ARM devices):

`docker run -it --privileged gasparka/spectrogram_driver:arm LimeUtil --fpga=LimeSDR-Mini_GW/LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd`

You can always restore the default image by running:

`docker run -it --privileged --net=host gasparka/spectrogram_driver:arm LimeUtil --update`

Note that you need to power-cycle the Lime after the FPGA programming, this is a LimeSuite bug `#216 <https://github.com/myriadrf/LimeSuite/issues/216>`_ 

Next, start the SoapySDR-Remote server:

`docker run -it --privileged --net=host gasparka/spectrogram_driver:arm`

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

See the `Demo Notebook <https://github.com/gasparka/realtime_spectrogram/blob/master/driver/usage_demo.ipynb>`_
 on how to access the server, control the SDR and plot the spectrogram.

Tested on:
* ODROID-XU4
* Raspberry Pi 3 (power from USB3 port)

# Realtime GUI

This is a Python GUI that plots the FFT frames from the remote diver in real-time. Example of turning on WiFy on a handset:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/wifi.gif "Wifi")

Or turning on Bluetooth:
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/Bluetooth.gif "Bluetooth")


Run (add ':arm' to run on ARM devices-slow!):
`docker run -it --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" gasparka/spectrogram_gui`

Tip: Use 'Space' to pause the stream.

# Accuracy vs floating-point model


Accelerator is implemented in 18-bit fixed-point format, thus it might be interesting
to compare the accuracy against a floating-point model.

Comparision with high-power input signal:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/vs_high.png)

In general the result is good, except for the one 'phantom' peak, which is due to the 9-bit twiddle
factors used in the FFT core. Note that this only happens when you have a very high power concentrated into one FFT bin.

Comparision with low-power input signal:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/vs_low.png)

Result is decent, taking into account that the input has only 2-3 bits of useful information. 
Use SDR gains to make it better.

# Cooling the LimeSDR-mini

Simplest way of cooling the Lime is to attach it to a piece of metal by using a 'thermal pad':

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9411.JPG)
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9408.JPG)


# Sources

Gateware sources:
https://github.com/gasparka/LimeSDR-Mini_GW/tree/fpga_fft

There is also a fork of LimeSuite that enables oversampling and has various hacks
related to the custom FPGA image:
https://github.com/gasparka/LimeSuite/tree/fpga_fft



