use crossbeam_channel::Sender;
use network_manager::NetworkManager;
use opqbox3::{Command, Command_oneof_command, GetInfoResponse, SendCommandToPlugin};
use pnet;
use protobuf::{parse_from_bytes, ProtobufError};
use std::sync::Arc;
use std::thread;

use config::Config;
use uptime_lib;
use zmq::{Context, Socket, PUSH, SUB};

//use pod_types::Window;

fn create_sub_socket(ctx: &Context, config: &Arc<Config>) -> Socket {
    let sub = ctx.socket(SUB).unwrap();
    sub.set_subscribe(config.settings.box_id.to_string().as_bytes())
        .unwrap();

    sub.set_curve_serverkey(&config.settings.server_public_key)
        .unwrap();

    sub.set_curve_publickey(&config.settings.box_public_key)
        .unwrap();
    sub.set_curve_secretkey(&config.settings.box_secret_key)
        .unwrap();
    sub.connect(&config.settings.cmd_sub_ep).unwrap();
    sub
}

fn create_push_socket(ctx: &Context, config: &Arc<Config>) -> Socket {
    let push = ctx.socket(PUSH).unwrap();

    push.set_curve_serverkey(&config.settings.server_public_key)
        .unwrap();

    push.set_curve_publickey(&config.settings.box_public_key)
        .unwrap();
    push.set_curve_secretkey(&config.settings.box_secret_key)
        .unwrap();
    push.connect(&config.settings.cmd_push_ep).unwrap();
    push
}

fn process_info_command(config: &Arc<Config>) -> GetInfoResponse {
    let mut resp = GetInfoResponse::new();
    let mut ips = String::new();
    let mut macs = String::new();
    for iface in pnet::datalink::interfaces() {
        if iface.is_loopback() {
            continue;
        }
        for ip in &iface.ips {
            ips += &ip.to_string();
            ips += "\n";
        }
        macs += &iface.mac_address().to_string();
        macs += "\n"
    }
    resp.set_mac_addr(macs);
    resp.set_ip(ips);
    let manager = NetworkManager::new();
    let mut ssids = String::new();
    for conn in manager.get_active_connections().unwrap() {
        ssids += conn.settings().ssid.as_str().unwrap();
        ssids += "\n";
    }
    resp.set_wifi_network(ssids);
    resp.set_calibration_constant(0);
    resp.set_pub_key(config.settings.box_public_key.clone());
    resp.set_uptime(uptime_lib::get().unwrap().num_seconds() as u64);
    resp
}

pub fn start_cmd_processor(
    tx_cmd_to_processing: Sender<SendCommandToPlugin>,
    config: Arc<Config>,
) -> thread::JoinHandle<()> {
    process_info_command(&config);
    thread::spawn(move || {
        let ctx = Context::default();
        let rx = create_sub_socket(&ctx, &config);
        let tx = create_push_socket(&ctx, &config);
        loop {
            let msg = rx.recv_multipart(0).unwrap();
            if msg.len() != 2 {
                //TODO log
                continue;
            }

            let msg: Result<Command, ProtobufError> = parse_from_bytes(&msg[1]);

            let cmd = match msg {
                Ok(msg) => msg,
                Err(_) => continue, //TODO log.
            };
            match cmd.command.unwrap() {
                Command_oneof_command::info_command(info) => {}
                Command_oneof_command::data_command(data) => {}
                Command_oneof_command::sampling_rate_command(sr) => {}
                Command_oneof_command::send_command_to_plugin(pc) => {}
            }
        }
    })
}
