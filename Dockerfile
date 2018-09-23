FROM ubuntu:18.04


# INSTALL REQUIREMENTS
RUN apt-get update && apt-get install -y git build-essential nano cmake g++ libi2c-dev libusb-1.0-0-dev python3-pip qtbase5-dev python3-pyqt5 python3-numpy libpython3-dev swig
RUN pip3 install pyqtgraph --no-deps

# CLONES
RUN git clone --progress --verbose  https://github.com/pothosware/SoapySDR.git
RUN git clone --progress --verbose --recurse-submodules https://github.com/gasparka/realtime_spectrogram

# INSTALL SOAPY
WORKDIR /SoapySDR/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr ..
RUN make install -j8

# INSTALL LIMESUITE
WORKDIR /realtime_spectrogram/LimeSuite/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr ..
RUN make install -j8
WORKDIR /realtime_spectrogram/LimeSuite/udev-rules
RUN sh install.sh

# RUN APP
WORKDIR /realtime_spectrogram

