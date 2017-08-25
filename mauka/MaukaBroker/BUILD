cc_binary(
    name = "broker",
    srcs = glob(["*.cc", "*.hpp"]),
    linkopts = ["-lzmq", "-pthread"],
    copts = ["--std=c++17"],
    deps = ["//zmqpp:zmqpp"],
)
