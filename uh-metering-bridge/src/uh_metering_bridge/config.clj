(ns uh-metering-bridge.config
  (:require [aero.core :as aero]))

(defn resource [name]
  (clojure.java.io/resource name))

(defn config []
  (aero/read-config (resource "config.edn")))

(defn username [config]
  (get-in config [:uh-metering-bridge :user]))

(defn password [config]
  (get-in config [:uh-metering-bridge :pass]))

(defn port [config]
  (:port config))
