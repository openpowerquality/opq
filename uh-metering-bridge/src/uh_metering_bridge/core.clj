(ns uh-metering-bridge.core
  (:require
    [uh-metering-bridge.server :as server])
  (:gen-class))

(defn -main
  "Starts the HTTP server for accessing UH meter data."
  []
  (server/start-server))