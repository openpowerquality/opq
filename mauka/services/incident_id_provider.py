import multiprocessing


class IncidentIdProvider:
    def __init__(self, next_available_incident_id: int):
        self.__next_available_incident_id = next_available_incident_id
        self.__lock = multiprocessing.RLock()

    def get_and_inc(self) -> int:
        with self.__lock:
            v = self.__next_available_incident_id
            self.__next_available_incident_id += 1
            return v


