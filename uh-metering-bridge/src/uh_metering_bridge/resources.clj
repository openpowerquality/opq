(ns uh-metering-bridge.resources
  (:require [clojure.data.json :as json]
            [clojure.java.io :as io]))

(defn load-resource-ids []
  (let [data (json/read-str (slurp (io/resource "resource_ids.json")))]
    data))

(defn load-resource-id [building feature]
  (let [data (load-resource-ids)
        building-data (get data building)
        resource-data (first (filter #(= (get % "Name") feature) building-data))]
    (str "BLUEPILLAR|" (get resource-data "tagID"))))

(defn building-resource-names []
  (let [data (load-resource-ids)]
    (keys data)))

(defn feature-names [meter-name]
  (let [data (load-resource-ids)
        building-data (get data meter-name)]
    (map #(get % "Name") building-data)))
