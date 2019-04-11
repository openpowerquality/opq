FROM rust:1.31

COPY . /health

WORKDIR /health

RUN cargo install --path

CMD ["health"]
