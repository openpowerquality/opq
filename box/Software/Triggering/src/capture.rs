use crossbeam_channel::Sender;
use std::error::Error;
use std::fs::File;
use std::io::Read;
use std::mem;
use std::path::Path;
use std::process::exit;
use std::slice;
use std::sync::Arc;
use std::thread;
//Local dependencies
use config::State;
use box_api::types;

pub fn start_capture(tx: Sender<types::Window>, state: Arc<State>) -> thread::JoinHandle<()> {
    thread::spawn(move || {
        let path_to_device = &state.settings.device_path;
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
        let cal_const = state.settings.calibration;
        let struct_size: usize = ::std::mem::size_of::<types::RawWindow>();
        //Danger! bad things happen if something goes wrong here.
        //We are manipulating raw buffers, leaving things uninitialized
        unsafe {
            loop {
                let mut raw_window: types::RawWindow = mem::zeroed();
                let buffer =
                    slice::from_raw_parts_mut(&mut raw_window as *mut _ as *mut u8, struct_size);
                if let Err(why) = file.read_exact(buffer) {
                    error!(
                        "couldn't read device driver handle {}: {}",
                        path.display(),
                        why.description()
                    );
                    exit(-1);
                }
                tx.send(types::Window::new(raw_window, cal_const));
            }
        }
    })
}
