use std::error::Error;
use std::fs::File;
use std::io::Read;
use std::mem;
use std::path::Path;
use std::slice;
use std::sync::mpsc::Sender;
use std::thread;
//Local dependencies
use pod_types;

pub fn start_capture(
    tx: Sender<pod_types::RawPacket>,
    path_to_device: String,
) -> thread::JoinHandle<()> {
    thread::spawn(move || {
        let path = Path::new(&path_to_device);

        let mut file: File = match File::open(&path) {
            // The `description` method of `io::Error` returns a string that
            // describes the error
            Err(why) => panic!(
                "couldn't open device driver handle {}: {}",
                path.display(),
                why.description()
            ),
            Ok(file) => file,
        };

        let struct_size: usize = ::std::mem::size_of::<pod_types::RawPacket>();
        //Danger! bad things happen if something goes wrong here.
        //We are manipulating raw buffers, leaving things uninitialized
        unsafe {
            loop {
                let mut r: pod_types::RawPacket = mem::zeroed();
                let buffer = slice::from_raw_parts_mut(&mut r as *mut _ as *mut u8, struct_size);
                match file.read_exact(buffer) {
                    // The `description` method of `io::Error` returns a string that
                    // describes the error
                    Err(why) => panic!(
                        "couldn't read device driver handle {}: {}",
                        path.display(),
                        why.description()
                    ),
                    Ok(()) => (),
                }
                tx.send(r).unwrap();
            }
        }
    })
}
