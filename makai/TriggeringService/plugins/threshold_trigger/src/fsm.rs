use std::collections::HashMap;
use Trigger;
use {datetime, TriggerType};

type StateMap = HashMap<StateKey, StateEntry>;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum State {
    Nominal,
    Triggering,
}

#[derive(Debug)]
pub struct StateEntry {
    prev_state: State,
    prev_state_timestamp_ms: u64,
    latest_state: State,
    latest_state_timestamp_ms: u64,
}

#[derive(Debug, Hash, Eq, Clone)]
pub struct StateKey {
    box_id: u32,
    trigger_type: TriggerType,
}

impl StateEntry {
    pub fn new(state: State) -> StateEntry {
        let timestamp = datetime::timestamp_ms();
        StateEntry {
            prev_state: state.clone(),
            prev_state_timestamp_ms: timestamp,
            latest_state: state.clone(),
            latest_state_timestamp_ms: timestamp,
        }
    }

    fn mutable_update(&mut self, state: State) {
        self.prev_state = self.latest_state.clone();
        // Don't update timestamp if previous state was triggering
        if self.prev_state != State::Triggering {
            self.prev_state_timestamp_ms = self.latest_state_timestamp_ms;
        }
        self.latest_state = state;
        self.latest_state_timestamp_ms = datetime::timestamp_ms();
    }
}
impl StateKey {
    pub fn from(box_id: u32, trigger_type: TriggerType) -> StateKey {
        StateKey {
            box_id,
            trigger_type,
        }
    }
}

impl PartialEq for StateKey {
    fn eq(&self, other: &StateKey) -> bool {
        self.box_id == other.box_id && self.trigger_type == other.trigger_type
    }
}

#[derive(Debug, Default)]
pub struct Fsm {
    state_map: StateMap,
}

impl Fsm {
    pub fn new() -> Fsm {
        Fsm {
            state_map: HashMap::new(),
        }
    }

    pub fn update(&mut self, state_key: StateKey, new_state: State) {
        self.state_map
            .entry(state_key)
            .and_modify(|state_entry| state_entry.mutable_update(new_state))
            .or_insert(StateEntry::new(new_state));
    }

    pub fn is_triggering(&self, state_key: &StateKey) -> Option<Trigger> {
        match self.state_map.get(state_key) {
            Some(state_entry) => {
                if state_entry.prev_state == State::Triggering
                    && state_entry.latest_state == State::Nominal
                {
                    return Some(Trigger::from(state_key.box_id, state_entry));
                }
                None
            }
            _ => None,
        }
    }
}
