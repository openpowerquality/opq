use futures::future;
use hyper::{Body, Chunk, Request, Response, StatusCode};
use hyper::rt::{Future, Stream};
use serde::Serialize;
use serde::de::DeserializeOwned;
use std::collections::HashMap;
use std::hash::Hash;
use std::net::SocketAddr;
use std::str::FromStr;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant, SystemTime};
use tokio::timer::Interval;

type Clients = Vec<Client>;
type Channels<C> = HashMap<C, Clients>;

/// Push server implementing Server-Sent Events (SSE).
///
/// SSE allow pushing events to browsers over HTTP without polling.
/// This library uses async hyper to support many concurrent push
/// connections and is compatible with the Rocket framework. It
/// supports multiple parallel channels and client authentication.
///
/// The generic parameter `C` specifies the type used to distinguish
/// the different channels and can be chosen arbitrarily.
///
/// Because the Server implements `Sync`, it can e.g. be stored
/// in a static variable using `lazy_static`.
pub struct Server<C> {
    channels: Mutex<Channels<C>>,
    next_id: AtomicUsize,
}

#[derive(Deserialize, Serialize)]
struct AuthToken<C> {
    created: SystemTime,
    allowed_channel: Option<C>,
}

impl<C: DeserializeOwned + Eq + Hash + FromStr + Send + Serialize> Server<C> {
    /// Create a new SSE push-server.
    pub fn new() -> Server<C> {

        Server {
            channels: Mutex::new(HashMap::new()),
            next_id: AtomicUsize::new(0),
        }
    }

    /// Push a message for the event to all clients registered on the channel.
    ///
    /// The message is first serialized and then send to all registered
    /// clients on the given channel, if any.
    ///
    /// Returns an error if the serialization fails.
    pub fn push<S: Serialize>(&self, channel: C, event: &str, message: &S) -> Result<(), serde_json::error::Error> {
        let payload = serde_json::to_string(message)?;
        let message = format!("event: {}\ndata: {}\n\n", event, payload);

        self.send_chunk_to_channel(message, channel);

        Ok(())
    }

    /// Initiate a new SSE stream for the given request.
    pub fn create_stream(&self, request: &Request<Body>) -> Response<Body> {

        // Extract channel from uri path (last segment)
        let channel = request.uri().path()
            .rsplit('/').next()
            .and_then(|channel_str| C::from_str(channel_str).ok());

        // Check if the request contained a valid channel and token
        let channel = match channel {
            Some(channel) => (channel),
            _ => {
                return Response::builder()
                    .status(StatusCode::BAD_REQUEST)
                    .body(Body::empty())
                    .expect("Could not create response");
            }
        };


        let (sender, body) = Body::channel();
        self.add_client(channel, sender);

        Response::builder()
            .header("Cache-Control", "no-cache")
            .header("X-Accel-Buffering", "no")
            .header("Content-Type", "text/event-stream")
            .header("Access-Control-Allow-Origin", "*")
            .body(body)
            .expect("Could not create response")
    }


    /// Send hearbeat to all clients on all channels.
    pub fn send_heartbeats(&self) {
        self.send_chunk_to_all_clients(":\n\n".into());
    }

    /// Remove disconnected clients.
    pub fn remove_stale_clients(&self) {
        let mut channels = self.channels.lock().unwrap();

        channels.retain(|_, clients| {
            clients.retain(|client| {
                if let Some(first_error) = client.first_error {
                    if first_error.elapsed() > Duration::from_secs(5) {
                        return false;
                    }
                }
                true
            });

            !clients.is_empty()
        });
    }

    /// Run a push SSE server on the given address.
    ///
    /// Convenience function for starting a push server on a new thread.
    /// Maintenance is done automatically, so you don't have to call
    /// `send_heartbeats` or `remove_stale_clients`.
    ///
    /// This function will panic in the current thread if it cannot
    /// listen on the specified address.
    pub fn spawn(&'static self, listen: SocketAddr) -> JoinHandle<()> {
        use hyper::service::service_fn_ok;

        let sse_handler = move |req: Request<Body>| {
            self.create_stream(&req)
        };

        let http_server = hyper::Server::bind(&listen)
            .serve(move || service_fn_ok(sse_handler))
            .map_err(|e| panic!("Push server failed: {}", e));

        let maintenance = Interval::new(Instant::now(), Duration::from_secs(45))
            .for_each(move |_| {
                self.remove_stale_clients();
                self.send_heartbeats();
                future::ok(())
            })
            .map_err(|e| panic!("Push maintenance failed: {}", e));

        thread::spawn(move || {
            hyper::rt::run(
                http_server
                    .join(maintenance)
                    .map(|_| ())
            );
        })
    }

    fn add_client(&self, channel: C, sender: hyper::body::Sender) {
        self.channels
            .lock().unwrap()
            .entry(channel)
            .or_insert_with(Default::default)
            .push(Client {
                tx: sender,
                id: self.next_id.fetch_add(1, Ordering::SeqCst),
                first_error: None,
            });
    }

    fn send_chunk_to_channel(&self, chunk: String, channel: C) {
        let mut channels = self.channels.lock().unwrap();

        match channels.get_mut(&channel) {
            Some(clients) => {
                for client in clients.iter_mut() {
                    let chunk = Chunk::from(chunk.clone());
                    client.send_chunk(chunk).ok();
                }
            }
            None => {} // Currently no clients on the given channel
        };
    }

    fn send_chunk_to_all_clients(&self, chunk: String) {
        let mut channels = self.channels.lock().unwrap();

        for client in channels.values_mut().flat_map(IntoIterator::into_iter) {
            let chunk = Chunk::from(chunk.clone());
            client.send_chunk(chunk).ok();
        }
    }
}

#[derive(Debug)]
struct Client {
    tx: hyper::body::Sender,
    id: usize,
    first_error: Option<Instant>,
}

impl Client {
    fn send_chunk(&mut self, chunk: Chunk) -> Result<(), Chunk> {
        let result = self.tx.send_data(chunk);

        match (&result, self.first_error) {
            (Err(_), None) => {
                // Store time when an error was first seen
                self.first_error = Some(Instant::now());
            }
            (Ok(_), Some(_)) => {
                // Clear error when write succeeds
                self.first_error = None;
            }
            _ => {}
        }

        result
    }
}
