#!/bin/bash

cd ..                                                                                                          && \
MAKAI_BIN=/usr/local/bin/makai                                                                                 && \
echo "Installing Makai binaries to ${MAKAI_BIN}"                                                               && \
mkdir -p                                                                                        ${MAKAI_BIN}   && \
cp AcquisitionBroker/target/release/ab                                                          ${MAKAI_BIN}/. && \
cp EventService/target/release/event_service                                                    ${MAKAI_BIN}/. && \
cp TriggeringBroker/target/release/tb                                                           ${MAKAI_BIN}/. && \
cp TriggeringService/target/release/makai                                                       ${MAKAI_BIN}/. && \
cp TriggeringService/plugins/health/target/release/libhealth_plugin.so                          ${MAKAI_BIN}/. && \
cp TriggeringService/plugins/napali_trigger/target/release/libnapali_plugin.so                  ${MAKAI_BIN}/. && \
cp TriggeringService/plugins/print/target/release/libprint_plugin.so                            ${MAKAI_BIN}/. && \
cp TriggeringService/plugins/threshold_trigger/target/release/libthreshold_trigger_plugin.so    ${MAKAI_BIN}/.

