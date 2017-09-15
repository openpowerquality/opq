#!/usr/bin/env bash

cd ../../mauka

echo "Generating static HTML documentation..."
python3 -m pydoc -w OpqMauka &&
python3 -m pydoc -w plugins &&
python3 -m pydoc -w plugins.FrequencyThresholdPlugin &&
python3 -m pydoc -w plugins.MeasurementPlugin &&
python3 -m pydoc -w plugins.MeasurementShimPlugin &&
python3 -m pydoc -w plugins.PrintPlugin &&
python3 -m pydoc -w plugins.StatusPlugin &&
python3 -m pydoc -w plugins.ThresholdPlugin &&
python3 -m pydoc -w plugins.VoltageThresholdPlugin &&
python3 -m pydoc -w plugins.base &&
python3 -m pydoc -w plugins.manager &&

echo "Moving files to gitbook..."
mv *.html ../gitbook/mauka/apis/. &&

echo "Deleting build cache..."
rm -rf __pycache__

echo "Done."