use crossbeam_channel::Sender;
use network_manager::NetworkManager;
use opqbox3::{Command, Command_oneof_command, SendCommandToPlugin,
              Response, SetMeasurementRateResponse, SendCommandToPluginResponse, GetInfoResponse};
use pnet;
use protobuf::{parse_from_bytes, ProtobufError, Message};
use std::sync::Arc;
use std::thread;

use config::{State, WINDOWS_PER_MEASUREMENT};
use uptime_lib;
use zmq::{Context, Socket, PUSH, SUB};
use std::time::{SystemTime, UNIX_EPOCH};

//use pod_types::Window;

fn create_sub_socket(ctx: &Context, state: &Arc<State>) -> Socket {
    let sub = ctx.socket(SUB).unwrap();
    sub.set_subscribe(state.settings.box_id.to_string().as_bytes())
        .unwrap();

    sub.set_curve_serverkey(&state.settings.server_public_key)
        .unwrap();

    sub.set_curve_publickey(&state.settings.box_public_key)
        .unwrap();
    sub.set_curve_secretkey(&state.settings.box_secret_key)
        .unwrap();
    sub.connect(&state.settings.cmd_sub_ep).unwrap();
    sub
}

fn create_push_socket(ctx: &Context, state: &Arc<State>) -> Socket {
    let push = ctx.socket(PUSH).unwrap();

    push.set_curve_serverkey(&state.settings.server_public_key)
        .unwrap();

    push.set_curve_publickey(&state.settings.box_public_key)
        .unwrap();
    push.set_curve_secretkey(&state.settings.box_secret_key)
        .unwrap();
    push.connect(&state.settings.cmd_push_ep).unwrap();
    push
}

fn process_info_command(state: &Arc<State>) -> Response {
    let mut info = GetInfoResponse::new();
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
    info.set_mac_addr(macs);
    info.set_ip(ips);
    let manager = NetworkManager::new();
    let mut ssids = String::new();
    for conn in manager.get_active_connections().unwrap() {
        ssids += conn.settings().ssid.as_str().unwrap();
        ssids += "\n";
    }
    info.set_wifi_network(ssids);
    info.set_calibration_constant(0);
    info.set_pub_key(state.settings.box_public_key.clone());
    info.set_uptime(uptime_lib::get().unwrap().num_seconds() as u64);

    let mut resp = Response::new();
    resp.set_info_response(info);
    resp
}

pub fn start_cmd_processor(
    tx_cmd_to_processing: Sender<SendCommandToPlugin>,
    state: Arc<State>,
) -> thread::JoinHandle<()> {

    thread::spawn(move || {
        let ctx = Context::default();
        let rx = create_sub_socket(&ctx, &state);
        let tx = create_push_socket(&ctx, &state);
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
            let mut response  = match cmd.command.clone().unwrap() {
                Command_oneof_command::info_command(_info) => process_info_command(&state),
                Command_oneof_command::data_command(data) => {

                    let start = data.get_start_ms();
                    let end = data.get_end_ms();
                    let std_duration =SystemTime::duration_since(UNIX_EPOCH).unwrap();

                    let mut resp = Response::new();
                    resp
                },
                Command_oneof_command::sampling_rate_command(sr) => {
                    let last_sp = state
                        .get_state(&WINDOWS_PER_MEASUREMENT.to_string())
                        .unwrap() as u32;
                    state.set_state(&WINDOWS_PER_MEASUREMENT.to_string(),sr.get_measurement_window_cycles() as f32);
                    let mut cmd_response = SetMeasurementRateResponse::new();
                    cmd_response.set_old_rate_cycles(last_sp);
                    let mut response = Response::new();
                    response.set_message_rate_reponse(cmd_response);
                    response
                },
                Command_oneof_command::send_command_to_plugin(pc) => {
                    tx_cmd_to_processing.send(pc);
                    let mut response = Response::new();
                    let mut cmd_response = SendCommandToPluginResponse::new();
                    cmd_response.set_ok(true);
                    response.set_command_to_plugin_response(cmd_response);
                    response
                }
            };

            response.set_box_id(state.settings.box_id as i32);
            response.set_seq(cmd.get_seq());
            let since_the_epoch = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
            response.timestamp_ms = since_the_epoch.as_secs() * 1000 +
                since_the_epoch.subsec_nanos() as u64 / 1_000_000;;
            let res = tx.send(&response.write_to_bytes().unwrap(), 0);
            match res{
                Ok(_) => {},
                Err(e) => {
                    warn!(
                        "Could not repond to command {:?}", e
                    );
                },
            }
        }
    })
}
