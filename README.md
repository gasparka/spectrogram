

Spectrogram accelerator for LimeSDR-mini. Average-pooling reduces the noise of the spectrogram 
and downsamples the output datarate. Potentially usable on ARM devices.
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/diagram.bmp "Diagram")

Turning on WiFi on my mobile:
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/wify.gif "Wify")

You will need a heat-sink on your LimeSDR-mini to run this!

1. Program the FPGA:

This repository is divided into two parts.

    ```bash
    docker run -it --privileged gasparka/realtime_spectrogram python3 main.py --fpga_init
    ```
    Note: You need to unplug and replug your LimeSDR-Mini!
    
2. Run the application:
    ```bash
    docker run -it --privileged --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" gasparka/realtime_spectrogram python3 main.py --run
    ```
    
3. Once you are done, restore the FPGA:
    ```bash
    docker run -it --privileged gasparka/realtime_spectrogram python3 main.py --fpga_restore
    ```
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
Here is a demo:

Idea is to put most screen space for time_axsis, so you can see even short time events. For
example the Bluetooth transmissions:

To use it you must have a Remote Driver working somewhere and then easiest is to
use the dockerized version like this:

`docker run -it --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" spectrogram_gui`





Heatsinking the LimeSDR-mini
----------------------------

Simple way of heatsinking your Lime by using the 'thermal pad' and a piece of metal.

![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9411.JPG)
![alt text](https://github.com/gasparka/realtime_spectrogram/blob/master/doc/IMG_9408.JPG)
