#include <iostream>
#include <csignal>
#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/sinks/text_file_backend.hpp>
#include <boost/log/utility/setup/file.hpp>
#include "boost/log/utility/setup/console.hpp"
#include <boost/log/utility/setup/common_attributes.hpp>
#include <boost/log/sources/severity_logger.hpp>
#include <boost/log/sources/record_ostream.hpp>

#include "ZMQTrigger.hpp"
#include "Reader.hpp"
#include "Settings.hpp"
#include "LocalAnalysis.hpp"
#include "version.hpp"
#include "Pipeline.hpp"

using namespace std;
using namespace opq;
using namespace boost;

namespace logging = boost::log;
namespace src = boost::log::sources;
namespace sinks = boost::log::sinks;
namespace keywords = boost::log::keywords;


namespace
{
    ///Flag used to communicate with the signal handler.
    volatile std::sig_atomic_t gSignalStatus;
}

/**
 * Signal handler for a gracefull exit.
 * @param signum signul number.
 */
void bail_handler( int signum )
{
    BOOST_LOG_TRIVIAL(fatal) << "Triggering: Caught SIGINT. Exiting.";
    cout << "Exiting" << endl;
    gSignalStatus = 0;
}

int main(int argc, char** argv) {
    gSignalStatus = 1;
    https://github.com/openpowerquality/opqbox2.git
    //Enable logging to console while we set up the log.
    logging::core::get()->set_filter(
            logging::trivial::severity >= logging::trivial::info
    );
    logging::add_common_attributes();

    //Load the settings file.
    boost::log::add_console_log(std::cerr, keywords::format = "[%TimeStamp%]: %Message%");

    string setting_file;
    if(argc < 2){
        BOOST_LOG_TRIVIAL(warning) << "Started with no arguments. Attempting to load /etc/opq/settings.set";
        setting_file = "/etc/opq/settings.set";
    } else {
        setting_file = argv[1];
    }

    auto settings = opq::Settings::Instance();
    if(!settings->loadFromFile(setting_file)){
        return 1;
    }

    //Set up the log.
    string logPath = settings->getString("log.trg_path");
    if(logPath == "")
        logPath = "log.txt";

    logging::add_file_log(
            keywords::file_name = logPath,
            keywords::format = "[%TimeStamp%]: %Message%",
            keywords::auto_flush = true,
            keywords::min_free_space = 100 * 1024 * 1024
    );

    BOOST_LOG_TRIVIAL(info) << "Triggering " << opq::OPQ_TRG_MAJOR_VERSION << "." << opq::OPQ_TRG_MINOR_VERSION;

    //Create the queues and threads.
    auto readerQueue = opq::data::make_measurement_queue();
    auto analysisQueue = opq::data::make_analysis_queue();

    pipeline::Slab readerSlab;
    opq::Reader reader(readerQueue);

    pipeline::Slab analysisSlab;
    opq::LocalAnalysis analysis(readerQueue, analysisQueue);

    pipeline::Slab triggerSlab;
    opq::ZMQTrigger trigger(analysisQueue);

    //Start all the threads.
    triggerSlab.start([&trigger](bool &running) {trigger.loop(running);});
    readerSlab.start([&reader](bool &running) {reader.loop(running);});
    analysisSlab.start([&analysis](bool &running) {analysis.loop(running);});
    //Post Signal handler for the interrupt signal
    std::signal(SIGINT, bail_handler);
    //Sleep until we catch a signal.
    while(gSignalStatus != 0){
        sleep(1);
    }
    //stop all the threads.
    triggerSlab.stop();
    analysisSlab.stop();
    readerSlab.stop();
    return 0;
}