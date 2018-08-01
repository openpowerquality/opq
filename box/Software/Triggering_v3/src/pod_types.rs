pub const POINTS_PER_PACKET: usize = 200;

#[repr(C, packed)]
pub struct RawPacket {
    datapoints: [i16; POINTS_PER_PACKET],
    last_gps_counter: u16,
    current_counter: u16,
    flags: u32,
}
