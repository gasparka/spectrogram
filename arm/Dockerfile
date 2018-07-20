FROM arm32v7/ubuntu:18.04

COPY ./qemu-arm-static /usr/bin/qemu-arm-static

# INSTALL BASIC STUFF
RUN apt-get update && apt-get install -y git build-essential software-properties-common


# CLONES
RUN git clone --progress --verbose  https://github.com/pothosware/SoapySDR.git
RUN git clone --progress --verbose --recurse-submodules https://github.com/gasparka/realtime_spectrogram


# INSTALL SOAPY
RUN apt-get install -y cmake g++ libpython3-dev swig python3-distutils
WORKDIR /SoapySDR/build
RUN cmake ..
RUN make install -j8
RUN ldconfig


# BUILD LIMESUITE
RUN apt-get install -y git g++ cmake libsqlite3-dev libi2c-dev libusb-1.0-0-dev
WORKDIR /realtime_spectrogram/LimeSuite/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr/local ..
RUN make install -j8
WORKDIR /realtime_spectrogram/LimeSuite/udev-rules
RUN sh install.sh

# DEPENDS
WORKDIR /realtime_spectrogram
RUN apt-get install -y python3-pip
RUN apt-get install -y qtbase5-dev python3-pyqt5 python3-numpy # needed for pyqtgraph
ENV DEBIAN_FRONTEND noninteractive # disable bullshit prompts
ENV DEBCONF_NONINTERACTIVE_SEEN true # disable bullshit prompts
RUN apt-get install -y python3-tk # needed by matplotlib
RUN pip3 install pyqtgraph


#CMD ["python3", "main.py"]


