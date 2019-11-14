"""
This module provides a thread-safe incident id provider.
"""

import multiprocessing


class IncidentIdProvider:
    """
    A thread-safe incident id provider.
    """
    def __init__(self, next_available_incident_id: int):
        self.__next_available_incident_id = next_available_incident_id
        self.__lock = multiprocessing.RLock()

    def get_and_inc(self) -> int:
        """
        Atomically gets the next available incident id and then increments it.
        :return: The next available incident id.
        """
        with self.__lock:
            next_available_incident_id = self.__next_available_incident_id
            self.__next_available_incident_id += 1
            return next_available_incident_id
