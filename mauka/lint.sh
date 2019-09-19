#!/bin/bash

pylint plugins      && \
pylint protobuf     && \
pylint services     && \
pylint analysis     && \
pylint config.py    && \
pylint constants    && \
pylint log          && \
pylint mongo        && \
pylint opq_mauka
