(defproject uh-metering-bridge "0.2.1"
  :description "Provides OPQ access to UH metering data"
  :url "https://github.com/openpowerquality/opq"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.clojure/clojure "1.10.0"]
                 [clj-http "3.9.1"]
                 [org.clojure/data.codec "0.1.1"]
                 [org.jsoup/jsoup "1.11.3"]
                 [org.clojure/data.json "0.2.6"]
                 [http-kit "2.3.0"]
                 [compojure "1.6.1"]
                 [cheshire "5.8.1"]
                 [aero "1.1.3"]]
  :main ^:skip-aot uh-metering-bridge.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all}})
