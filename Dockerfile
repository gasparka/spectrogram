FROM ubuntu:18.04

# INSTALL BASIC STUFF
RUN apt-get update && apt-get install -y git build-essential software-properties-common

# ADD REPOS
RUN add-apt-repository -y ppa:myriadrf/drivers
RUN add-apt-repository -y ppa:pothosware/framework
RUN add-apt-repository -y ppa:pothosware/support
RUN add-apt-repository -y ppa:myriadrf/drivers
RUN apt-get update

# INSTALL SOAPY
RUN apt-get install -y soapysdr-tools python3-soapysdr python3-numpy


RUN git clone --recurse-submodules https://github.com/gasparka/realtime_spectrogram

# BUILD LIMESUITE
RUN apt-get install -y git g++ cmake libsqlite3-dev libsoapysdr-dev libi2c-dev libusb-1.0-0-dev
WORKDIR /realtime_spectrogram/LimeSuite/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr ..
RUN make install -j8
WORKDIR /realtime_spectrogram/LimeSuite/udev_rules
RUN sh install.sh
