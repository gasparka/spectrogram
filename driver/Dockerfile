FROM ubuntu:18.04

# INSTALL REQUIREMENTS
RUN apt-get update && apt-get install -y git build-essential nano cmake g++ libi2c-dev libusb-1.0-0-dev avahi-daemon libavahi-client-dev

# CLONES
RUN git clone --progress --verbose  https://github.com/pothosware/SoapyRemote.git
RUN git clone --progress --verbose  https://github.com/pothosware/SoapySDR.git
RUN git clone -b fpga_fft --progress --verbose  https://github.com/gasparka/LimeSuite

# INSTALL SOAPY
WORKDIR /SoapySDR/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr ..
RUN make install -j8
RUN ldconfig

# INSTALL SOAPY-REMOTE
WORKDIR /SoapyRemote/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr ..
RUN make install -j8
RUN ldconfig

# INSTALL CUSTOM LIMESUITE
WORKDIR /LimeSuite/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr ..
RUN make install -j8
WORKDIR /LimeSuite/udev-rules
RUN sh install.sh

EXPOSE 80
CMD /etc/init.d/dbus start; /etc/init.d/avahi-daemon start; SoapySDRServer --bind="0.0.0.0:80"

