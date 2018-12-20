(ns uh-metering-bridge.resources
  (:require [clojure.data.json :as json]
            [clojure.java.io :as io]))

(def load-resource-ids (memoize (fn []
                                  (let [data (json/read-str (slurp (io/resource "resource_ids.json")))]
                                    data))))

(defn load-resource-id [building feature]
  (let [data (load-resource-ids)
        building-data (get data building)
        resource-data (first (filter #(= (get % "Name") feature) building-data))]
    (str "BLUEPILLAR|" (get resource-data "tagID"))))

(defn feature-map-has-name [feature-map name]
  (= (get feature-map "Name")
     name))

(defn available-meters [feature]
  (let [data (load-resource-ids)]
    (into [] (sort (keys (into {} (filter (fn [kv]
                                            (let [feature-maps (last kv)]
                                              (some #(feature-map-has-name % feature) feature-maps)))
                                          data)))))))

(defn all-available-meters []
  (let [data (load-resource-ids)]
    (sort (keys data))))

(defn available-features [meter-name]
  (let [data (load-resource-ids)
        building-data (get data meter-name)]
    (sort-by clojure.string/lower-case (map #(get % "Name") building-data))))

(defn all-available-features []
  (let [data (load-resource-ids)
        features (flatten (vals data))
        feature-names (into #{} (map #(get % "Name") features))]
    (sort-by clojure.string/lower-case feature-names)))

(defn features-per-meter []
  (let [data (load-resource-ids)]
    (reduce (fn [m [k v]]
              (assoc m k (into [] (sort-by clojure.string/lower-case (map #(get % "Name") v)))))
            {}
            data)))

(defn meters-per-feature []
  (let [features (all-available-features)]
    (into {} (map (fn [feature]
                    [feature (available-meters feature)]) features))))

