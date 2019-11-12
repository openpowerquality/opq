

#[derive(Debug, Fail)]
pub enum StoreError {
    #[fail(display = "no such event: {}", id)]
    NoSuchEvent {
        id: u32,
    },
}
