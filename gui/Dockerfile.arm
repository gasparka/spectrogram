FROM arm32v7/ubuntu:18.04

COPY ./qemu-arm-static /usr/bin/qemu-arm-static

# INSTALL REQUIREMENTS
RUN apt-get update && apt-get install -y git build-essential cmake python3-pip qtbase5-dev python3-pyqt5 python3-numpy libpython3-dev swig
RUN pip3 install pyqtgraph --no-deps

# CLONES
RUN git clone --progress --verbose  https://github.com/pothosware/SoapyRemote.git
RUN git clone --progress --verbose  https://github.com/pothosware/SoapySDR.git

# INSTALL SOAPY
WORKDIR /SoapySDR/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr ..
RUN make install -j8

# INSTALL SOAPY-REMOTE
WORKDIR /SoapyRemote/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr ..
RUN make install -j8

# RUN APP
WORKDIR /
ADD ./ ./gui
ENV PYTHONPATH /
CMD python3 /gui/main.py
