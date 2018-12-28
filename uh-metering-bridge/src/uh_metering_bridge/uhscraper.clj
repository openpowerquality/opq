(ns uh-metering-bridge.uhscraper
  (:require [clj-http.client :as client]
            [clojure.data.json :as json]
            [uh-metering-bridge.config :as config]
            [uh-metering-bridge.resources :as resources])
  (:import (java.time Instant ZonedDateTime ZoneId LocalDateTime)
           (org.jsoup Jsoup)))

(def uh-manoa-site-id "17abfe2a-3ae5-471b-965c-3e88e42f28d8")

(defn extract-connection-id [html]
  (let [lines (map clojure.string/trim (clojure.string/split-lines html))
        conn-id-line (first (filter #(clojure.string/starts-with? % "Avise.Config.UrlManager.url") lines))]
    (second (re-find #"'([^' ]+)'" conn-id-line))))

(defn extract-client-id [html]
  (let [lines (map clojure.string/trim (clojure.string/split-lines html))
        client-id-line (first (filter #(clojure.string/starts-with? % "Avise.Config.UrlManager.SingleClientId") lines))]
    (second (re-find #"'([^' ]+)'" client-id-line))))

(defn extract-server-id [html]
  (let [lines (map clojure.string/trim (clojure.string/split-lines html))
        client-id-line (first (filter #(clojure.string/starts-with? % "Avise.Config.UrlManager.SingleServerId") lines))]
    (second (re-find #"'([^' ]+)'" client-id-line))))

(defn extract-credentials- [html]
  (let [document (Jsoup/parse html)
        req-token-element (.selectFirst document "[name=__RequestVerificationToken]")]
    {:request-verification-token (.val req-token-element)
     :connection-id              (extract-connection-id html)
     :client-id                  (extract-client-id html)
     :server-id                  (extract-server-id html)
     :site-id                    uh-manoa-site-id}))



(def extract-credentials (memoize extract-credentials-))

(defn timestamp-ms []
  (.toEpochMilli (Instant/now)))

(defn timestamp-s []
  (.getEpochSecond (Instant/now)))

(defn timestamps-from-past [past-seconds]
  (let [end-ts (timestamp-s)
        start-ts (- end-ts past-seconds)]
    [start-ts end-ts]))

(defn format-datetime [zdt]
  (let [full-hour (.getHour zdt)
        corrected-hour (if (> full-hour 12)
                         (- full-hour 12)
                         full-hour)
        am-or-pm (if (< full-hour 12)
                   "AM"
                   "PM")]
    (str "|" (.getMonthValue zdt) "/" (.getDayOfMonth zdt) "/" (.getYear zdt) " " corrected-hour ":" (format "%02d" (.getMinute zdt)) " " am-or-pm)))

(defn to-zdt [ts-s-utc]
  (let [instant (Instant/ofEpochSecond ts-s-utc)
        zdt (ZonedDateTime/ofInstant instant (ZoneId/of (get ZoneId/SHORT_IDS "HST")))]
    zdt))

(defn post-login [username password]
  (:body (client/post "https://energydata.hawaii.edu/Auth/Login"
                      {:form-params       {"UserName" username
                                           "Password" password}
                       :trace-redirects   true
                       :redirect-strategy :lax})))

(defn to-ts [formatted-datetime]
  (let [ldt (LocalDateTime/parse formatted-datetime)
        zdt (.atZone ldt (ZoneId/of "UTC"))
        instant (.toInstant zdt)]
    (.getEpochSecond instant)))

(defn transform-data-point [data-sample-map]
  {:meter-name  (get data-sample-map "EntityName")
   :sample-type (get data-sample-map "TagName")
   :ts-s        (to-ts (get data-sample-map "FullDateTimeUTC"))
   :actual      (get data-sample-map "Actual")
   :min         (get data-sample-map "Min")
   :max         (get data-sample-map "Max")
   :avg         (get data-sample-map "Mean")
   :stddev      (get data-sample-map "StDev")})

(defn parse-scraped-data [scraped-data]
  (let [data (json/read-str (:body scraped-data))
        _ (println scraped-data)]
    (map transform-data-point (get data "Graph"))))

(defn scrape-data [resource-id start-ts-s end-ts-s]
  (let [conf (config/config)
        username (config/username conf)
        password (config/password conf)
        credentials (extract-credentials (post-login username password))
        connection-id (:connection-id credentials)]
    (parse-scraped-data (client/get "https://energydata.hawaii.edu/api/reports/GetAnalyticsGraphAndGridData/GetAnalyticsGraphAndGridData"
                                    {:query-params               {:connectionId   connection-id
                                                                  :storedProcName "GetLogMinuteDataForTagIds"
                                                                  :rollupName     "Mean"
                                                                  :tableIndex     "1"
                                                                  :parameter1     (format-datetime (to-zdt start-ts-s))
                                                                  :parameter2     (format-datetime (to-zdt end-ts-s))
                                                                  :parameter3     "|-600"
                                                                  :parameter4     "|client"
                                                                  :parameter5     resource-id
                                                                  :_              (str timestamp-ms)}
                                     :__RequestVerificationToken (:request-verification-token credentials)
                                     :content-type               :json
                                     :socket-timeout 10000
                                     :conn-timeout 10000}))))

(defn scrape-data-for-meter [meter-name start-ts-s end-ts-s]
  (let [conf (config/config)
        username (config/username conf)
        password (config/password conf)
        credentials (extract-credentials (post-login username password))
        connection-id (:connection-id credentials)
        features (resources/available-features meter-name)
        resource-ids (apply str (interpose "," (map (partial resources/load-resource-id meter-name) features)))]
    (parse-scraped-data (client/get "https://energydata.hawaii.edu/api/reports/GetAnalyticsGraphAndGridData/GetAnalyticsGraphAndGridData"
                                    {:query-params               {:connectionId   connection-id
                                                                  :storedProcName "GetLogMinuteDataForTagIds"
                                                                  :rollupName     "Mean"
                                                                  :tableIndex     "1"
                                                                  :parameter1     (format-datetime (to-zdt start-ts-s))
                                                                  :parameter2     (format-datetime (to-zdt end-ts-s))
                                                                  :parameter3     "|-600"
                                                                  :parameter4     "|client"
                                                                  :parameter5     resource-ids
                                                                  :_              (str timestamp-ms)}
                                     :__RequestVerificationToken (:request-verification-token credentials)
                                     :content-type               :json
                                     :socket-timeout 20000
                                     :conn-timeout 20000}))))

(defn scrape-data-for-meter-past [meter-name past-seconds]
  (let [[start end] (timestamps-from-past past-seconds)]
    (scrape-data-for-meter meter-name start end)))

(defn scrape-data-with-resource-ids [resource-ids start-ts-s end-ts-s]
  (let [conf (config/config)
        username (config/username conf)
        password (config/password conf)
        credentials (extract-credentials (post-login username password))
        connection-id (:connection-id credentials)
        query-params {:connectionId   connection-id
                      :storedProcName "GetLogMinuteDataForTagIds"
                      :rollupName     "Mean"
                      :tableIndex     "1"
                      :parameter1     (format-datetime (to-zdt start-ts-s))
                      :parameter2     (format-datetime (to-zdt end-ts-s))
                      :parameter3     "|-600"
                      :parameter4     "|client"
                      :parameter5     (clojure.string/join "," resource-ids)
                      :_              (str timestamp-ms)}
        _ (println query-params)]
    (parse-scraped-data (client/get "https://energydata.hawaii.edu/api/reports/GetAnalyticsGraphAndGridData/GetAnalyticsGraphAndGridData"
                                    {:query-params query-params
                                     :__RequestVerificationToken (:request-verification-token credentials)
                                     :content-type               :json
                                     :socket-timeout 20000
                                     :conn-timeout 20000}))))

(defn scrape-all-data [start-ts end-ts]
  (scrape-data-with-resource-ids (resources/all-available-resource-ids) start-ts end-ts))

(defn scrape-all-data-past [past-seconds]
  (let [[start-ts end-ts] (timestamps-from-past past-seconds)]
    (scrape-all-data start-ts end-ts)))

(defn scrape-data-with-features [features start-ts end-ts]
  (scrape-data-with-resource-ids (resources/resource-ids-for-features features) start-ts end-ts))

(defn scrape-data-with-features-past [features past-seconds]
  (let [[start-ts end-ts] (timestamps-from-past past-seconds)]
    (scrape-data-with-features features start-ts end-ts)))
