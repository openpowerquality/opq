#!/usr/bin/env bash

/Users/anthony/python3/bin/python3 -m pydoc -w OpqMauka
/Users/anthony/python3/bin/python3 -m pydoc -w plugins
/Users/anthony/python3/bin/python3 -m pydoc -w plugins.FrequencyThresholdPlugin
/Users/anthony/python3/bin/python3 -m pydoc -w plugins.MeasurementPlugin
/Users/anthony/python3/bin/python3 -m pydoc -w plugins.MeasurementShimPlugin
/Users/anthony/python3/bin/python3 -m pydoc -w plugins.PrintPlugin
/Users/anthony/python3/bin/python3 -m pydoc -w plugins.StatusPlugin
/Users/anthony/python3/bin/python3 -m pydoc -w plugins.ThresholdPlugin
/Users/anthony/python3/bin/python3 -m pydoc -w plugins.VoltageThresholdPlugin
/Users/anthony/python3/bin/python3 -m pydoc -w plugins.base

mv *.html ../gitbook/mauka/apis/.
rm -rf __pycache__
