(ns uh-metering-bridge.uhscraper
  (:require [clj-http.client :as client]
            [clojure.data.json :as json])
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

(defn extract-credentials [html]
  (let [document (Jsoup/parse html)
        req-token-element (.selectFirst document "[name=__RequestVerificationToken]")]
    {:request-verification-token (.val req-token-element)
     :connection-id              (extract-connection-id html)
     :client-id                  (extract-client-id html)
     :server-id                  (extract-server-id html)
     :site-id                    uh-manoa-site-id}))

(defn timestamp-ms []
  (.toEpochMilli (Instant/now)))

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
  (let [data (json/read-str (:body scraped-data))]
    (map transform-data-point (get data "Graph"))))

(defn scrape-data [resource-id start-ts-s end-ts-s]
  (binding [clj-http.core/*cookie-store* (clj-http.cookies/cookie-store)]
    (let [credentials (extract-credentials (post-login "achriste" "Password1"))
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
                                       :content-type               :json})))))

