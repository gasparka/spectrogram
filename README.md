# Spectrogram (80MHz bandwidth) accelerator for LimeSDR-Mini

Turning on WiFi on a handset:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/wifi.gif "Wifi")

Or turning on Bluetooth:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/blue.gif "Bluetooth")

Block diagram:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/diagram.bmp "Diagram")

Average-pooling reduces the noise of the spectrogram 
and downsamples the USB bandwidth to 2.5MB/s, which allows remote deployment by using SoapySDR-Remote on RaspberryPi3. 

**NOTE: LimeSDR-Mini needs to have a cooling solution, see below for an example.**

# Running the driver on ARM devices

Install Docker:

`curl -fsSL https://get.docker.com | sh`

For the first time, flash the FPGA (drop the ':arm' tag to run on non-ARM devices):

`docker run -it --privileged gasparka/spectrogram_driver:arm LimeUtil --fpga=LimeSDR-Mini_GW/LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd`

You can always restore the default image by running:

`docker run -it --privileged --net=host gasparka/spectrogram_driver:arm LimeUtil --update`

Note that you need to power-cycle the Lime after the FPGA programming, this is a LimeSuite bug [#216](https://github.com/myriadrf/LimeSuite/issues/216).

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

See the [Demo Notebook](https://github.com/gasparka/realtime_spectrogram/blob/master/driver/usage_demo.ipynb)
 on how to access the server, control the SDR and plot the spectrogram.

Tested on:
* ODROID-XU4
* RaspberryPi3 - Pi was powered from a USB3 port, Lime connected to USB2 port of Pi. 

# Realtime GUI

Python GUI that plots the FFT frames from the remote diver in real-time. 

Run (add ':arm' to run on ARM devices-slow!):

`docker run -it --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" gasparka/spectrogram_gui`

Tip: Use 'Space' to pause the stream.

# Accuracy vs floating-point model


Accelerator is implemented mostly in 18-bit fixed-point format, thus it might be interesting
to compare the accuracy against 64-bit floating-point model.

High power input signal:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/vs_high.png)

The 'phantom' peak at -5MHz is due to the 9-bit twiddle
factors used in the FFT core. This happens only when a very high power is concentrated into one FFT bin.

Low power input signal:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/vs_low.png)

Accelerator can detect low power input signals. Accuracy vs floating-point model
is degraded due to the input having only ~2 bits of useful information - using SDR gains improves the situation.

# Cooling the LimeSDR-mini

Using a '~2mm thermal pad' and a piece of metal:

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9411.JPG)
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9408.JPG)

Using small heatsinks wont cut it:
https://discourse.myriadrf.org/t/rpi3-heat-sinks-on-limesdr-mini/3523


# Sources

Gateware sources:

https://github.com/gasparka/LimeSDR-Mini_GW/tree/fpga_fft/LimeSDR-Mini_lms7_trx/src/fft

There is also a fork of LimeSuite that enables oversampling and has various hacks
related to the custom FPGA image:

https://github.com/gasparka/LimeSuite/tree/fpga_fft



