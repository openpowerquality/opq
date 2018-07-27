use std::error::Error;
use std::fs::File;
use std::io::Read;
use std::path::Path;
use std::thread;
use std::sync::mpsc::Sender;
use std::slice;

//Local dependencies
use pod_types;

pub fn start_capture(tx : Sender<pod_types::RawPacket>, path_to_device : String) -> thread::JoinHandle<()> {
    thread::spawn(move || {
        let path = Path::new(&path_to_device);
        let mut file: File = match File::open(&path) {
            // The `description` method of `io::Error` returns a string that
            // describes the error
            Err(why) => panic!("couldn't open device driver handle {}: {}", path.display(),
                               why.description()),
            Ok(file) => file,
        };
        let struct_size = ::std::mem::size_of::<pod_types::RawPacket>();
        let mut reader = BufReader::new(try!(File::open(path)));
        let r = pod_types::RawPacket::new();
        unsafe {
            let mut buffer = slice::from_raw_parts_mut(r.as_mut_ptr() as *mut u8, struct_size);
            reader.read_exact(buffer)?;
            r.set_len(num_structs);
        }
    })
}