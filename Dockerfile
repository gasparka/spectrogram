FROM ubuntu:18.04

# INSTALL REQUIREMENTS
RUN apt-get update && apt-get install -y build-essential \
                                            cmake \
                                            g++ \
                                            libi2c-dev \
                                            libusb-1.0-0-dev \
                                            avahi-daemon \
                                            libavahi-client-dev \
                                            wget \
                                            qtbase5-dev \
                                            libqt5svg5-dev \
                     && rm -rf /var/lib/apt/lists/*

# INSTALL SOAPY
COPY ./SoapySDR ./tmp
RUN mkdir tmp/build && cd tmp/build && cmake -DCMAKE_INSTALL_PREFIX=/usr .. && make install -j8 && rm -rf /tmp

# INSTALL SOAPY-REMOTE
COPY ./SoapyRemote ./tmp
RUN mkdir tmp/build && cd tmp/build && cmake -DCMAKE_INSTALL_PREFIX=/usr .. && make install -j8 && rm -rf /tmp

# INSTALL CUSTOM LIMESUITE
COPY ./LimeSuite ./tmp
RUN cd tmp/build && cmake -DCMAKE_INSTALL_PREFIX=/usr .. && make install -j8 && cd ../udev-rules/ && sh install.sh && rm -rf /tmp

# BUILD GQRX
COPY ./gqrx ./tmp
RUN mkdir tmp/build && cd tmp/build && cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_CXX_STANDARD_LIBRARIES="-lSoapySDR" .. && make install -j8 && rm -rf /tmp

WORKDIR /
COPY ./LimeSDR-Mini_GW/LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd ./
COPY ./gqrx/default.conf ./
COPY ./docker_entrypoint.sh /

EXPOSE 80
ENTRYPOINT ["/docker_entrypoint.sh"]

