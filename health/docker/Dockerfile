# select build image
FROM rust:1.34

WORKDIR /build

ADD build /build
RUN cd /build/health && \
    cargo build --release


# set the startup command to run your binary
CMD ["./build/health/target/release/health"]
