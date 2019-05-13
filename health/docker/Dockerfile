# select build image
FROM rust:1.33 as build

# create a new empty shell project
RUN USER=root cargo new --bin health
WORKDIR /health

# copy over your manifests
COPY ./Cargo.toml ./Cargo.toml

# this build step will cache your dependencies
RUN cargo build --release
RUN rm src/*.rs

# copy your source tree
COPY ./src ./src

# build for release
RUN rm ./target/release/deps/health*
RUN cargo build --release

# our final base
FROM rust:1.33

# copy the build artifact from the build stage
COPY --from=build /health/target/release/health .
COPY --from=build /health/src ./src

# set the startup command to run your binary
CMD ["./health"]
