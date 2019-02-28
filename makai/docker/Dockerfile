FROM debian:buster-slim

WORKDIR /build

# Build tools and deps
RUN apt-get update &&   \
    apt-get install -y  \
        cmake           \
        curl            \
        g++             \
        gcc             \
        git             \
        libprotobuf17   \
        libprotobuf-dev \
        libzmq5         \
        libzmq5-dev     \
        perl            \
        pkg-config      \
        protobuf-compiler

# Rust
RUN curl -s https://sh.rustup.rs -sSf | sh -s -- -y && \
    $HOME/.cargo/bin/rustup install nightly         && \
    $HOME/.cargo/bin/rustup default nightly

ENV PATH="/root/.cargo/bin:$PATH"

# sccache
RUN curl -L -O https://github.com/mozilla/sccache/releases/download/0.2.8/sccache-0.2.8-x86_64-unknown-linux-musl.tar.gz    && \
    tar xf sccache-0.2.8-x86_64-unknown-linux-musl.tar.gz                                                                   && \
    rm sccache-0.2.8-x86_64-unknown-linux-musl.tar.gz                                                                       && \
    cp sccache-0.2.8-x86_64-unknown-linux-musl/sccache $HOME/.cargo/bin                                                     && \
    rm -rf sccache-0.2.8-x86_64-unknown-linux-musl

ENV RUSTC_WRAPPER="sccache"

# Mongo c driver
RUN curl -L -O https://github.com/mongodb/mongo-c-driver/archive/1.14.0.tar.gz                      && \
    tar xf 1.14.0.tar.gz                                                                            && \
    rm 1.14.0.tar.gz                                                                                && \
    echo "1.14.0" > mongo-c-driver-1.14.0/VERSION_CURRENT                                           && \
    cd mongo-c-driver-1.14.0/build                                                                  && \
    cmake -DENABLE_TESTS=OFF -DENABLE_AUTOMATIC_INIT_AND_CLEANUP=OFF -DCMAKE_BUILD_TYPE=Release ..  && \
    make -j 4 -C /build/mongo-c-driver-1.14.0/build                                                 && \
    make -C /build/mongo-c-driver-1.14.0/build install                                              && \
    rm -rf /build/mongo-c-driver-1.14.0

# Mongo c++ driver
RUN curl -L -O https://github.com/mongodb/mongo-cxx-driver/archive/r3.4.0.tar.gz    && \
    tar xf r3.4.0.tar.gz                                                            && \
    rm r3.4.0.tar.gz                                                                && \
    cd mongo-cxx-driver-r3.4.0/build                                                && \
    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..           && \
    make -j 4 -C /build/mongo-cxx-driver-r3.4.0/build                               && \
    make -C /build/mongo-cxx-driver-r3.4.0/build install                            && \
    rm -rf /build/mongo-cxx-driver-r3.4.0

# zmqpp
RUN curl -L -O https://github.com/zeromq/zmqpp/archive/4.2.0.tar.gz && \
    tar xf 4.2.0.tar.gz                                             && \
    rm 4.2.0.tar.gz                                                 && \
    make -j 4 -C zmqpp-4.2.0                                        && \
    make -C zmqpp-4.2.0 install                                     && \
    rm -rf zmqpp-4.2.0

# Add makai contents
ADD makai-build /build

# Acquisition broker
RUN mkdir -p /build/makai/AcquisitionBroker/build   && \
    cd /build/makai/AcquisitionBroker/build         && \
    cmake ..                                        && \
    make -j 4 -C /build/makai/AcquisitionBroker/build

# Triggering broker
RUN mkdir -p /build/makai/TriggeringBroker/build    && \
    cd /build/makai/TriggeringBroker/build          && \
    cmake ..                                        && \
    make -j 4 -C /build/makai/TriggeringBroker/build

# Triggering service and plugins
RUN sccache --start-server                                      && \
    cd /build/makai/TriggeringService                           && \
    cargo build --release                                       && \
    cd /build/makai/TriggeringService/plugins/health            && \
    cargo build --release                                       && \
    cd /build/makai/TriggeringService/plugins/print             && \
    cargo build --release                                       && \
    cd /build/makai/TriggeringService/plugins/threshold_trigger && \
    cargo build --release                                       && \
    sccache --stop-server

# Organize makai binaries and configurations
RUN mkdir -p /build/conf                                                                            && \
    cp /build/makai/AcquisitionBroker/acquisition_broker_config.json /build/conf                    && \
    cp /build/makai/TriggeringBroker/triggering_broker_config.json /build/conf                      && \
    cp /build/makai/TriggeringService/makai.json /build/conf                                        && \
    mkdir -p /build/bin                                                                             && \
    cp /build/makai/run-makai.sh /build/bin                                                         && \
    cp /build/makai/AcquisitionBroker/build/AcquisitionBroker /build/bin                            && \
    cp /build/makai/TriggeringBroker/build/TriggeringBroker /build/bin                              && \
    cp /build/makai/TriggeringService/target/release/makai /build/bin                               && \
    cp /build/makai/TriggeringService/plugins/health/target/release/libhealth_plugin.so /build/bin  && \
    cp /build/makai/TriggeringService/plugins/print/target/release/libprint_plugin.so /build/bin    && \
    cp /build/makai/TriggeringService/plugins/threshold_trigger/target/release/libthreshold_trigger_plugin.so /build/bin

# Cleanup
RUN rm -rf /build/makai     && \
    rm -rf /build/protocol  && \
    rm -rf $HOME/.cargo     && \
    rm -rf $HOME/.cache     && \
    rm -rf $HOME/.rustup    && \
    rm -rf $HOME/.multirust && \
    apt-get purge -y        \
        cmake               \
        curl                \
        g++                 \
        gcc                 \
        git                 \
        perl                \
        pkg-config          \
        protobuf-compiler   && \
    apt-get autoremove -y   && \
    rm -rf /var/lib/apt/lists/*

# Start Makai
RUN ["/bin/bash", "/build/bin/start-makai.sh"]

