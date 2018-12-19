(ns uh-metering-bridge.config
  (:require [aero.core :as aero]))


(defn config []
  (aero/read-config "config.edn"))

(defn username [config]
  (get-in config [:uh-metering-bridge :user]))

(defn password [config]
  (get-in config [:uh-metering-bridge :pass]))

(defn port [config]
  (:port config))

