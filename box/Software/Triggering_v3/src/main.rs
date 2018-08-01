mod capture;
mod pod_types;
use capture::start_capture;
use std::sync::mpsc::channel;

fn main() {
    let (sender, receiver) = channel();
    start_capture(sender, "/dev/opq0".to_string());
}
