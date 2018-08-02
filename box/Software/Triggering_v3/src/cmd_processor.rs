use config::Settings;
use opqbox3::{Command,GetInfoCommand, GetInfoResponse, Command_oneof_command};
use protobuf::{parse_from_bytes, ProtobufError};
use std::sync::mpsc::Receiver;
use std::thread;
use zmq::{Context, CurveKeyPair, Message, Socket, PUSH, SUB};
use pnet;
use network_manager::{AccessPoint, AccessPointCredentials, Device, DeviceType, NetworkManager};
use uptime_lib;
//use pod_types::Window;

fn create_sub_socket(ctx: &Context, settings: &Settings) -> Socket {
    let sub = ctx.socket(SUB).unwrap();
    sub.set_subscribe(settings.box_id.to_string().as_bytes())
        .unwrap();

    sub.set_curve_serverkey(&settings.server_public_key)
        .unwrap();

    sub.set_curve_publickey(&settings.box_public_key).unwrap();
    sub.set_curve_secretkey(&settings.box_secret_key).unwrap();
    sub.connect(&settings.cmd_sub_ep).unwrap();
    sub
}

fn create_push_socket(ctx: &Context, settings: &Settings) -> Socket {
    let push = ctx.socket(PUSH).unwrap();

    push.set_curve_serverkey(&settings.server_public_key)
        .unwrap();

    push.set_curve_publickey(&settings.box_public_key).unwrap();
    push.set_curve_secretkey(&settings.box_secret_key).unwrap();
    push.connect(&settings.cmd_push_ep).unwrap();
    push
}

fn process_info_command(id: u32, pub_key: String) -> GetInfoResponse{
    let mut resp = GetInfoResponse::new();
    let mut ips = String::new();
    let mut macs = String::new();
    for iface in pnet::datalink::interfaces(){
        if iface.is_loopback() {
            continue;
        }
        for ip in &iface.ips{
            ips += &ip.to_string();
            ips += "\n";
        }
        macs +=  &iface.mac_address().to_string();
        macs += "\n"
    }
    resp.set_mac_addr(macs);
    resp.set_ip(ips);
    let manager = NetworkManager::new();
    let mut ssids = String::new();
    for conn in manager.get_active_connections().unwrap(){
        ssids += conn.settings().ssid.as_str().unwrap();
        ssids += "\n";
    }
    resp.set_wifi_network(ssids);
    resp.set_calibration_constant(0);
    resp.set_pub_key(pub_key);
    resp.set_uptime(uptime_lib::get().unwrap().num_seconds() as u64);
    resp
}

pub fn start_cmd_processor(setting: &Settings) -> thread::JoinHandle<()> {
    let ctx = Context::default();
    let rx = create_sub_socket(&ctx, setting);
    let tx = create_push_socket(&ctx, setting);
    let id = setting.box_id.clone();
    let pub_key = setting.box_public_key.clone();
    process_info_command(id, pub_key);
    thread::spawn(move || {
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
            match cmd.command.unwrap(){
                Command_oneof_command::info_command(info) => {},
                Command_oneof_command::data_command(data) => {},
                Command_oneof_command::sampling_rate_command(sr) => {},
            }
        }
    })
}
