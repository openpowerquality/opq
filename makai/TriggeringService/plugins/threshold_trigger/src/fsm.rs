use std::collections::HashMap;
use Trigger;
use {datetime, TriggerType};

type StateMap = HashMap<StateKey, StateEntry>;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum State {
    Nominal,
    Triggering,
}

#[derive(Debug, Hash, Eq, Clone)]
pub struct StateKey {
    pub box_id: u32,
    pub trigger_type: TriggerType,
}

#[derive(Debug)]
pub struct StateEntry {
    pub prev_state: State,
    pub prev_state_timestamp_ms: u64,
    pub latest_state: State,
    pub latest_state_timestamp_ms: u64,
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

#[cfg(test)]
mod tests {
    use Fsm;
    use State;
    use StateKey;
    use TriggerType;

    #[test]
    fn test_fsm() {
        let mut fsm = Fsm::new();
        let state_key = StateKey::from(1, TriggerType::Frequency);

        fsm.update(state_key.clone(), State::Nominal);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), false);
        fsm.update(state_key.clone(), State::Nominal);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), false);
        fsm.update(state_key.clone(), State::Triggering);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), false);
        fsm.update(state_key.clone(), State::Triggering);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), false);
        fsm.update(state_key.clone(), State::Nominal);
        assert_eq!(fsm.is_triggering(&state_key).is_some(), true);
    }
}
