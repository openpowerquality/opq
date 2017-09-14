#!/usr/bin/env bash

python3 -m pydoc -w OpqMauka
python3 -m pydoc -w plugins
python3 -m pydoc -w plugins.FrequencyThresholdPlugin
python3 -m pydoc -w plugins.MeasurementPlugin
python3 -m pydoc -w plugins.MeasurementShimPlugin
python3 -m pydoc -w plugins.PrintPlugin
python3 -m pydoc -w plugins.StatusPlugin
python3 -m pydoc -w plugins.ThresholdPlugin
python3 -m pydoc -w plugins.VoltageThresholdPlugin
python3 -m pydoc -w plugins.base

mv *.html ../gitbook/mauka/apis/.
rm -rf __pycache__
