FROM ubuntu:18.04
# https://github.com/davidecavestro/mariadb-docker-armhf/tree/756c3f31a117341896c37976640055fb43d5b004

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


WORKDIR /
COPY ./ ./src/

# INSTALL SOAPY
WORKDIR /src/SoapySDR/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr .. && make install -j8

# INSTALL SOAPY-REMOTE
WORKDIR /src/SoapyRemote/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr .. && make install -j8

# INSTALL CUSTOM LIMESUITE
WORKDIR /src/LimeSuite/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr .. && make install -j8
WORKDIR /src/LimeSuite/udev-rules
RUN sh install.sh

# BUILD GQRX
WORKDIR /src/gqrx/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_CXX_STANDARD_LIBRARIES="-lSoapySDR" .. && make install -j8

WORKDIR /
COPY ./LimeSDR-Mini_GW/LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd ./
COPY ./gqrx/default.conf ./
COPY ./docker_entrypoint.sh /
RUN rm -rf /src

EXPOSE 80
ENTRYPOINT ["/docker_entrypoint.sh"]

