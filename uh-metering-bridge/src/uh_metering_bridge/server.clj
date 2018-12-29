(ns uh-metering-bridge.server
  (:require [org.httpkit.server :as server]
            [compojure.core :refer :all]
            [compojure.route :as route]
            [uh-metering-bridge.config :as config]
            [uh-metering-bridge.resources :as resources]
            [uh-metering-bridge.uhscraper :as scraper]
            [clojure.data.json :as json]))

(defn health-check-handler
  "Handler that always returns 200 OK. Used for health checks."
  [req]
  {:status 200})

(defn all-available-meters-handler
  "This function returns a JSON list of meter names."
  [req]
  {:status  200
   :headers {"Content-Type" "application/json"}
   :body    (json/write-str (resources/all-available-meters))})

(defn features-for-meter-handler [req]
  "This function returns a JSON list of feature names for a given meter."
  (let [meter-name (-> req :params :meter-name)]
    {:status  200
     :headers {"Content-Type" "application/json"}
     :body    (json/write-str (resources/available-features meter-name))}))

(defn all-available-features-handler [req]
  {:status  200
   :headers {"Content-Type" "application/json"}
   :body    (json/write-str (resources/all-available-features))})

(defn meters-for-feature-handler [req]
  "This function returns a JSON list of feature names for a given meter."
  (let [feature-name (-> req :params :feature-name)]
    {:status  200
     :headers {"Content-Type" "application/json"}
     :body    (json/write-str (resources/available-meters feature-name))}))

(defn meters-to-features-handler [req]
  {:status  200
   :headers {"Content-Type" "application/json"}
   :body    (json/write-str (resources/features-per-meter))})

(defn features-to-meters-handler [req]
  {:status  200
   :headers {"Content-Type" "application/json"}
   :body    (json/write-str (resources/meters-per-feature))})

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
     :headers {"Content-Type" "application/json"}
     :body (json/write-str (scraper/scrape-data (resources/load-resource-id meter-name feature-name) start-ts end-ts))}))

(defn meter-data-handler [req]
  "This handler returns data points as a JSON list given a meter name, feature name, and start and end timestamps."
  (let [meter-name (-> req :params :meter-name)
        start-ts (to-long (-> req :params :start-ts))
        end-ts (to-long (-> req :params :end-ts))]
    {:status 200
     :headers {"Content-Type" "application/json"}
     :body (json/write-str (scraper/scrape-data-for-meter meter-name start-ts end-ts))}))

(defn features-data-handler [req]
  "This handler returns data points as a JSON list given a meter name, feature name, and start and end timestamps."
  (let [past-seconds (to-long (-> req :params :past-seconds))
        features (into #{} (clojure.string/split (-> req :params :features) #";"))]
    {:status 200
     :headers {"Content-Type" "application/json"}
     :body (json/write-str (scraper/scrape-data-with-features-past features past-seconds))}))

(defn all-data-handler [req]
  "This handler returns data points as a JSON list given a meter name, feature name, and start and end timestamps."
  (let [past-seconds (to-long (-> req :params :past-seconds))]
    {:status 200
     :headers {"Content-Type" "application/json"}
     :body (json/write-str (scraper/scrape-all-data-past past-seconds))}))

(defn default-data-handler [req]
  "This handler returns data points as a JSON list given a meter name, feature name, and start and end timestamps."
  {:status 200
   :headers {"Content-Type" "application/json"}
   :body (json/write-str (scraper/scrape-default))})


(defroutes all-routes
           (GET "/" [] health-check-handler)
           (GET "/meters" [] all-available-meters-handler)
           (GET "/features" [] all-available-features-handler)
           (GET "/features/:meter-name" [] features-for-meter-handler)
           (GET "/meters/:feature-name" [] meters-for-feature-handler)
           (GET "/meters_to_features" [] meters-to-features-handler)
           (GET "/features_to_meters" [] features-to-meters-handler)
           (GET "/data/:meter-name/:start-ts/:end-ts" [] )
           (GET "/data/:meter-name/:feature-name/:start-ts/:end-ts" [] meter-data-handler)
           (GET "/past/features/:past-seconds/:features" [] features-data-handler)
           (GET "/past/all/:past-seconds" [] all-data-handler)
           (GET "/default" [] default-data-handler)
           (route/not-found "Content not found"))

(defonce server-inst (atom nil))

(defn stop-server []
  (when-not (nil? server-inst)
    (@server-inst :timeout 100)
    (reset! server-inst nil)))

(defn start-server []
  (let [port (config/port (config/config))]
    (reset! server-inst (server/run-server #'all-routes {:port port}))))

(defn restart-server []
  (do
    (stop-server)
    (start-server)))

