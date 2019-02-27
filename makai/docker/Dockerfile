FROM debian:buster-slim

WORKDIR /build

# Build tools and deps
RUN apt-get update &&   \
    apt-get install -y  \
    cmake               \
    curl                \
    g++                 \
    gcc                 \
    git                 \
    libprotobuf17       \
    libprotobuf-dev     \
    libzmq5             \
    libzmq5-dev         \
    perl                \
    pkg-config          \
    protobuf-compiler

# Rust
RUN curl -s https://sh.rustup.rs -sSf | sh -s -- -y && \
    $HOME/.cargo/bin/rustup install nightly         && \
    $HOME/.cargo/bin/rustup default nightly

# Mongo c driver
RUN curl -L -O https://github.com/mongodb/mongo-c-driver/archive/1.14.0.tar.gz  && \
    tar xf 1.14.0.tar.gz                                                        && \
    rm 1.14.0.tar.gz                                                            && \
    echo "1.14.0" > mongo-c-driver-1.14.0/VERSION_CURRENT

RUN cd mongo-c-driver-1.14.0/build && \
    cmake -DENABLE_TESTS=OFF -DENABLE_AUTOMATIC_INIT_AND_CLEANUP=OFF -DCMAKE_BUILD_TYPE=Release ..

RUN make -C mongo-c-driver-1.14.0/build         && \
    make -C mongo-c-driver-1.14.0/build install && \
    rm -rf mongo-c-driver-1.14.0

# Mongo c++ driver
RUN curl -L -O https://github.com/mongodb/mongo-cxx-driver/archive/r3.4.0.tar.gz    && \
    tar xf r3.4.0.tar.gz                                                            && \
    rm r3.4.0.tar.gz

RUN cd mongo-cxx-driver-r3.4.0/build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..

RUN make -C mongo-cxx-driver-r3.4.0/build           && \
    make -C mongo-cxx-driver-r3.4.0/build install   && \
    rm -rf mongo-cxx-driver-r3.4.0

# zmqpp
RUN curl -L -O https://github.com/zeromq/zmqpp/archive/4.2.0.tar.gz && \
    tar xf 4.2.0.tar.gz                                             && \
    rm 4.2.0.tar.gz

RUN make -C zmqpp-4.2.0         && \
    make -C zmqpp-4.2.0 install && \
    rm -rf zmqpp-4.2.0

# Add makai contents
ADD makai-build /build

# Acquisition broker
RUN mkdir -p /build/makai/AcquisitionBroker/build
RUN cd /build/makai/AcquisitionBroker/build && \
    cmake ..
RUN make -C /build/makai/AcquisitionBroker/build

# Triggering broker
RUN mkdir -p /build/makai/TriggeringBroker/build
RUN cd /build/makai/TriggeringBroker/build && \
    cmake ..
RUN make -C /build/makai/TriggeringBroker/build

# Triggering service
