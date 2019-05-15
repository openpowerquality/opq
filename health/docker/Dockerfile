# select build image
FROM rust:1.34

WORKDIR /build

ADD build /build
RUN cd /build/health                                    && \
    cargo build --release                               && \
    mkdir -p /build/bin                                 && \
    cp /build/health/target/release/health /build/bin   && \
    cp /build/health/run-health.sh /build/bin           && \
    rm -rf /build/health




# set the startup command to run your binary
CMD ["/bin/bash", "/build/bin/run-health.sh"]
