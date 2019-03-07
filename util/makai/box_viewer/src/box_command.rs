use zmq;

use protobuf::{Message};
use crate::proto::opqbox3::{Command, GetInfoCommand, Command_oneof_command};
use crate::config::Settings;
use crate::util::timestamp;
pub enum CommandType {
    Info,
}

pub struct BoxCommand{
    acq_broker : zmq::Socket,
    identity : String
}

impl BoxCommand {
    pub fn new(config : &Settings, ctx: &zmq::Context) -> BoxCommand{
        let cmd = BoxCommand{
            acq_broker: ctx.socket(zmq::PUSH).unwrap(),
            identity : config.identity.clone().unwrap()
        };
        cmd.acq_broker.connect(&config.zmq_acquisition_endpoint).unwrap();
        cmd
    }

    pub fn send_command(&mut self, box_id: u32 ,cmd_type : CommandType) {
        let mut cmd = Command::new();
        cmd.timestamp_ms = timestamp();
        cmd.box_id = box_id as i32;
        cmd.identity = self.identity.clone();
        cmd.command = Some(match cmd_type {
            CommandType::Info => Command_oneof_command::info_command(GetInfoCommand::new()),
        });
        self.acq_broker.send(&cmd.write_to_bytes().unwrap(),0).unwrap();

    }

}
