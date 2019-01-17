extern crate protoc_rust;
use std::fs;

fn main() {
    fs::create_dir_all("src/proto");
    protoc_rust::run(protoc_rust::Args {
        out_dir: "src/proto",
        input: &["../../protocol/opqbox3.proto"],
        includes: &["../../protocol/"],
    }).expect("protoc");

    protoc_rust::run(protoc_rust::Args {
        out_dir: "src/proto",
        input: &["../../protocol/makai.proto"],
        includes: &["../../protocol/"],
    }).expect("protoc");

}
