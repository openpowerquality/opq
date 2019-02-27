FROM alpine:3.9

WORKDIR /makai

# Build tools and deps
RUN apk --no-cache --update-cache add build-base cmake pkgconfig git perl protobuf zeromq

# Mongo c driver
RUN wget https://github.com/mongodb/mongo-c-driver/archive/1.14.0.tar.gz
RUN tar xf 1.14.0.tar.gz
RUN rm 1.14.0.tar.gz
RUN echo "1.14.0" > mongo-c-driver-1.14.0/VERSION_CURRENT
RUN cd mongo-c-driver-1.14.0/build && cmake -DENABLE_AUTOMATIC_INIT_AND_CLEANUP=OFF -DCMAKE_BUILD_TYPE=Release ..
RUN make -C mongo-c-driver-1.14.0/build
RUN make -C mongo-c-driver-1.14.0/build install
RUN rm -rf mongo-c-driver-1.14.0

# Build https://github.com/mongodb/mongo-cxx-driver
RUN wget https://github.com/mongodb/mongo-cxx-driver/archive/r3.4.0.tar.gz
RUN tar xf r3.4.0.tar.gz
RUN rm r3.4.0.tar.gz
RUN cd mongo-cxx-driver-r3.4.0/build && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..
RUN make -C mongo-cxx-driver-r3.4.0/build
RUN make -C mongo-cxx-driver-r3.4.0/build install
RUN rm -rf mongo-cxx-driver-r3.4.0

#Acquisition broker
RUN mkdir /makai/makai
RUN mkdir /makai/protocol
ADD ./makai/ /makai/makai
ADD protocol /makai/protocol
RUN mkdir -p /usr/local/include/google/protobuf/
RUN cp /makai/protocol/descriptor.proto /usr/local/include/google/protobuf/.
RUN mkdir -p /makai/makai/AcquisitionBroker/build
RUN cd /makai/makai/AcquisitionBroker/build && cmake ..
RUN make -C /makai/makai/AcquisitionBroker/build
RUN make -C /makai/makai/AcquisitionBroker/build install

# Triggering broker

# Triggering service

#  -DENABLE_TESTS=OFF