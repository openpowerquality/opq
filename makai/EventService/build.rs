extern crate protoc_rust;
use std::fs;

fn main() {
    fs::create_dir_all("src/proto").unwrap();
    protoc_rust::run(protoc_rust::Args {
        out_dir: "src/proto",
        input: &["../../protocol/opqbox3.proto"],
        includes: &["../../protocol/"],
        customize: Default::default(),
    })
    .expect("protoc");
}
