(ns uh-metering-bridge.server
  (:require [org.httpkit.server :as server]
            [compojure.core :refer :all]
            [compojure.route :as route]
            [uh-metering-bridge.resources :as resources]
            [uh-metering-bridge.uhscraper :as scraper]
            [clojure.data.json :as json]))

(defn health-check-handler
  "Handler that always returns 200 OK. Used for health checks."
  [req]
  {:status 200})

(defn meter-names-handler
  "This function returns a JSON list of meter names."
  [req]
  {:status  200
   :headers {"Content-Type" "application/json"}
   :body    (json/write-str (resources/building-resource-names))})

(defn feature-names-handler [req]
  "This function returns a JSON list of feature names for a given meter."
  (let [meter-name (-> req :params :meter-name)]
    {:status 200
     :headers {"Content-Type" "application/json"}
     :body (json/write-str (resources/feature-names meter-name))}))

(defn to-long [s]
  "Converts a string into a long."
  (Long/parseLong s))

(defn data-handler [req]
  "This handler returns data points as a JSON list given a meter name, feature name, and start and end timestamps."
  (let [meter-name (-> req :params :meter-name)
        feature-name (-> req :params :feature-name)
        start-ts (to-long (-> req :params :start-ts))
        end-ts (to-long (-> req :params :end-ts))]
    {:status 200
     :headers {"Conetent-Type" "application/json"}
     :body (json/write-str (scraper/scrape-data (resources/load-resource-id meter-name feature-name) start-ts end-ts))}))

(defroutes all-routes
           (GET "/" [] health-check-handler)
           (GET "/meters" [] meter-names-handler)
           (GET "/meters/:meter-name" [] feature-names-handler)
           (GET "/data/:meter-name/:feature-name/:start-ts/:end-ts" [] data-handler)
           (route/not-found "Content not found"))

(defonce server-inst (atom nil))

(defn stop-server []
  (when-not (nil? server-inst)
    (@server-inst :timeout 100)
    (reset! server-inst nil)))

(defn start-server []
  (reset! server-inst (server/run-server #'all-routes {:port 13000})))

(defn restart-server []
  (do
    (stop-server)
    (start-server)))

