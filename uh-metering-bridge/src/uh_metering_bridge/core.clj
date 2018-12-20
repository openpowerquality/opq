(ns uh-metering-bridge.core
  (:require
    [uh-metering-bridge.server :as server])
  (:gen-class))

(defn -main
  "Starts the HTTP server for accessing UH meter data."
  []
  (server/start-server))

(server/start-server)
; http://127.0.01:13000/data/POST_MAIN_1/Frequency/1544043600/1544047200