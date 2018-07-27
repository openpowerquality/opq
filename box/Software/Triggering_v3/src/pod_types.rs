pub const POINTS_PER_PACKET: usize = 200;

#[repr(C, packed)]
pub struct RawPacket{
    datapoints : [i16;POINTS_PER_PACKET],
    last_gps_counter : u16,
    current_counter : u16,
    flags : u32,
}

impl RawPacket {
    pub fn new() -> RawPacket{
        RawPacket{
            datapoints : [0; POINTS_PER_PACKET],
            last_gps_counter: 0,
            current_counter : 0,
            flags : 0
        }
    }
}

