#!/usr/bin/env bash

cd ../../mauka

echo "Generating static HTML documentation..."
python3 -m pydoc -w OpqMauka &&
python3 -m pydoc -w plugins &&
python3 -m pydoc -w plugins.acquisition_trigger_plugin &&
python3 -m pydoc -w plugins.base_plugin &&
python3 -m pydoc -w plugins.frequency_threshold_plugin &&
python3 -m pydoc -w plugins.frequency_variation_plugin &&
python3 -m pydoc -w plugins.ieee1159_voltage_plugin &&
python3 -m pydoc -w plugins.itic_plugin &&
python3 -m pydoc -w plugins.makai_event_plugin &&
python3 -m pydoc -w plugins.mock_plugin &&
python3 -m pydoc -w plugins.outage_plugin &&
python3 -m pydoc -w plugins.print_plugin &&
python3 -m pydoc -w plugins.semi_f47_plugin &&
python3 -m pydoc -w plugins.status_plugin &&
python3 -m pydoc -w plugins.thd_plugin &&
python3 -m pydoc -w plugins.threshold_plugin &&
python3 -m pydoc -w plugins.voltage_threshold_plugin &&

python3 -m pydoc -w protobuf.util &&

python3 -m pydoc -w services.brokers &&
python3 -m pydoc -w services.plugin_manager &&

python3 -m pydoc -w analysis &&
python3 -m pydoc -w config &&
python3 -m pydoc -w constants &&
python3 -m pydoc -w log &&
python3 -m pydoc -w mongo &&
python3 -m pydoc -w opq_mauka &&

#echo "Moving files to gitbook..."
#mv *.html ../gitbook/mauka/apis/. &&

echo "Moving files to 'api_docs'"
mkdir -p api_docs
mv *.html api_docs

echo "Deleting build cache..."
rm -rf __pycache__

echo "Done."