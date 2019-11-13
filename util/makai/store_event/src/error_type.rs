#[derive(Debug, Fail)]
pub enum StoreError {
    #[fail(display = "no such event: {}", id)]
    NoSuchEvent { id: u32 },
    #[fail(display = "Could not create file or directory {}", path)]
    CouldNotCreate { path: String },
}
