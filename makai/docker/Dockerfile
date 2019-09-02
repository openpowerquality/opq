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
        protobuf-compiler \
        libmongoc-dev

# Rust
#RUN curl -s https://sh.rustup.rs -sSf | sh -s -- -y && \
#    $HOME/.cargo/bin/rustup install nightly         && \
#    $HOME/.cargo/bin/rustup default nightly

RUN curl -s https://sh.rustup.rs -sSf | sh -s -- -y

ENV PATH="/root/.cargo/bin:$PATH"

# sccache
RUN curl -L -O https://github.com/mozilla/sccache/releases/download/0.2.8/sccache-0.2.8-x86_64-unknown-linux-musl.tar.gz    && \
    tar xf sccache-0.2.8-x86_64-unknown-linux-musl.tar.gz                                                                   && \
    rm sccache-0.2.8-x86_64-unknown-linux-musl.tar.gz                                                                       && \
    cp sccache-0.2.8-x86_64-unknown-linux-musl/sccache $HOME/.cargo/bin                                                     && \
    rm -rf sccache-0.2.8-x86_64-unknown-linux-musl

ENV RUSTC_WRAPPER="sccache"

# Add makai contents
ADD makai-build /build

# Acquisition broker
RUN sccache --start-server                                      && \
    cd /build/makai/AcquisitionBroker/                          && \
    cargo build --release                                       && \
    cd /build/makai/TriggeringBroker/                           && \
    cargo build --release                                       && \
    cd /build/makai/TriggeringService                           && \
    cargo build --release                                       && \
    cd /build/makai/TriggeringService/plugins/health            && \
    cargo build --release                                       && \
    cd /build/makai/TriggeringService/plugins/print             && \
    cargo build --release                                       && \
    cd /build/makai/TriggeringService/plugins/threshold_trigger && \
    cargo build --release                                       && \
    cd /build/makai/TriggeringService/plugins/napali_trigger    && \
    cargo build --release                                       && \
    cd /build/makai/EventService                                && \
    cargo build --release                                       && \
    sccache --stop-server

# Organize makai binaries and configurations
RUN mkdir -p /build/bin                                                                                                     && \
    cp /build/makai/run-makai.sh /build/bin                                                                                 && \
    cp /build/makai/AcquisitionBroker/target/release/ab /build/bin                                                          && \
    cp /build/makai/TriggeringBroker/target/release/tb /build/bin                                                           && \
    cp /build/makai/TriggeringService/target/release/makai /build/bin                                                       && \
    cp /build/makai/EventService/target/release/event_service /build/bin                                                    && \
    cp /build/makai/TriggeringService/plugins/health/target/release/libhealth_plugin.so /build/bin                          && \
    cp /build/makai/TriggeringService/plugins/print/target/release/libprint_plugin.so /build/bin                            && \
    cp /build/makai/TriggeringService/plugins/threshold_trigger/target/release/libthreshold_trigger_plugin.so /build/bin    && \
    cp /build/makai/TriggeringService/plugins/napali_trigger/target/release/libnapali_plugin.so /build/bin

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

# These ports only need to be exposed to other containers.
EXPOSE 8080

EXPOSE 9899

EXPOSE 10000

# These ports must be exposed to the outside world. This is accomplished in the docker-compose.yml file.
EXPOSE 9880

EXPOSE 8196

EXPOSE 8194

EXPOSE 9881

EXPOSE 10001

# Start Makai
CMD ["/bin/bash", "/build/bin/run-makai.sh"]
