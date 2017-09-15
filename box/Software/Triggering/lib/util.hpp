#ifndef ACQUISITION_UTILL_HPP
#define ACQUISITION_UTILL_HPP
#include <string>
#include "opq.pb.h"
#include "opqdata.hpp"
#include <regex>
#include <fstream>
#include <chrono>

using std::string;

namespace opq{
    /**
     * OPQ Acqisition utility functions.
     */
    namespace util{

        /**
         * @brief Create a millisecond timestamp from a chrono::time_point.
         * @param time timestamp to convert.
         * @return millisecond timestamp.
         */
        inline uint64_t crono_to_mili(std::chrono::time_point<std::chrono::high_resolution_clock > time){
            std::chrono::time_point<std::chrono::high_resolution_clock > epoch;
            auto elapsed = time - epoch;
            return std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
        }

        inline std::chrono::time_point<std::chrono::high_resolution_clock > mili_to_crono(uint64_t time_stamp){
		auto epoch = std::chrono::time_point<std::chrono::high_resolution_clock>();
		auto since_epoch = std::chrono::milliseconds(time_stamp);
		auto timestamp = epoch + since_epoch;
		return timestamp;
        }


        /**
         * @brief serialize data::OPQAnalysisPtr using google's protobuf protocol.
         * @param id id of the client device.
         * @param message analysis result ready to be transmitted.
         * @return string containing a serialized data::OPQAnalysisPtr.
         */
        inline string serialize_to_protobuf(int id, data::OPQAnalysisPtr message){
            proto::TriggerMessage protomessage;
            std::string out;
            protomessage.set_id(id);
            protomessage.set_frequency(message->frequency);
            protomessage.set_rms(message->RMS);
            protomessage.set_time(crono_to_mili(message->start));
            protomessage.set_current_count(message->current_counter);
            protomessage.set_last_gps(message->last_gps_counter);
            protomessage.set_flags(message->flags);
            protomessage.SerializeToString(&out);
            return out;
        }

        /**
         * @brief serialize data::OPQMeasurementPtr using google's protobuf protocol.
         * @param id id of the client device.
         * @param message analysis result ready to be transmitted.
         * @return string containing a serialized data::OPQMeasurementPtr.
         */
        inline string serialize_to_protobuf(int id, data::OPQMeasurementPtr message){
            opq::proto::DataMessage protomessage;
            protomessage.set_id(id);
            for (size_t mnum = 0; mnum< message->cycles.size();mnum++){
                auto &cycle = message->cycles[mnum];
                opq::proto::Cycle *protocycle = protomessage.add_cycles();
                for(size_t i =0; i < data::SAMPLES_PER_CYCLE; i++){
                    protocycle->add_data(cycle.data[i]);
                }
                protocycle->set_time(crono_to_mili(message->timestamps[mnum]));
                protocycle->set_last_gps(message->cycles[mnum].last_gps_counter);
                protocycle->set_current_count(message->cycles[mnum].current_counter);
                protocycle->set_flags(message->cycles[mnum].flags);
            }
            std::string out;
            protomessage.SerializeToString(&out);
            return out;
        }


        using std::regex;
        using std::regex_search;

        inline auto load_certificate(string const &path) -> std::pair<string, string> {
            auto public_re = regex{R"r(public-key\s+=\s+"(.+)")r"};
            auto private_re = regex{R"r(secret-key\s+=\s+"(.+)")r"};

            auto file = std::ifstream{ path };
            assert(file);

            auto ss = std::stringstream{};
            ss << file.rdbuf();
            auto contents = ss.str();

            auto public_sm = std::smatch{}, private_sm = std::smatch{};

            auto has_public = regex_search(contents, public_sm, public_re);
            auto has_private = regex_search(contents, private_sm, private_re);

            return {has_public ? public_sm[1] : std::string{},
                    has_private ? private_sm[1] : std::string{}};
        }

    }
}


#endif //ACQUISITION_UTILL_HPP
