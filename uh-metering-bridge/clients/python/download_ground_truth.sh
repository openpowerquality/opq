#!/bin/bash

declare -a features=("AVG_CURRENT_THD"
                     "AVG_VOLTAGE_THD"
                     "CURRENT_A_THD"
                     "CURRENT_B_THD"
                     "CURRENT_C_THD"
                     "Frequency"
                     "VAB"
                     "VAN"
                     "VBC"
                     "VBN"
                     "VCA"
                     "VCN"
                     "VOLAGE_CN_THD"
                     "VOLTAGE_AN_THD"
                     "VOLTAGE_BN_THD"
                     "VOLTAGE_CN_THD")

for feature in "${features[@]}"
do
    echo "Starting bridge for feature $feature"
    /usr/bin/java -jar /home/opquser/uh-metering-bridge-0.2.4-standalone.jar &
    sleep 2
    /usr/local/bin/python3 /home/opquser/uh-metering-bridge.py ${feature} 3600
    echo "Done."
done