FROM python:3.7-slim-stretch

RUN apt-get update -y       \
    && apt-get install -y   \
           gcc              \
           curl             \
           python3-dev

# Rust
RUN curl -s https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain nightly
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /build

ADD build /build

# Some of the requirements depend on numpy to be installed first (looking at you Pandas)
RUN pip3 install --no-cache --trusted-host pypi.python.org numpy \
    && pip3 install --no-cache --trusted-host pypi.python.org -r mauka/requirements.txt \
    && cd /build/mauka/native/mauka_native_py \
    && maturin build --release --strip  \
    && cd /build/mauka/native \
    && pip3 install target/wheels/mauka_native_py-0.1.0-cp37-cp37m-manylinux1_x86_64.whl

# Cleanup
RUN apt-get purge -y            \
        gcc                     \
        curl                    \
        python3-dev             \
    && apt-get autoremove -y    \
    && rm -rf /var/lib/apt/lists/*

# Health interface
EXPOSE 8911

# CLI interface
EXPOSE 12000

# ZMQ triggering interface
EXPOSE 9881

# ZMQ event interface
EXPOSE 9899

# Mauka pub/sub interfaces
EXPOSE 9882
EXPOSE 9883

# Makai push interface
EXPOSE 9884

CMD ["python3", "mauka/opq_mauka.py"]
