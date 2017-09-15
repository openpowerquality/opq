/*! @mainpage Data acquisition and local processing daemon
 * @section Introduction
 * OPQ Acquisition is a userland daemon which runs on the raspberry pi zero. It is responsible for transferring data
 * from the kernel driver, processing it, storing the raw data in a local Redis server and sending the processed
 * "Triggering data" to the OPQ acquisition network.
 */

#ifndef TRIGGERING_VERSION_HPP
#define TRIGGERING_VERSION_HPP
namespace opq {
    ///Major Acquisition version.
    static const unsigned int OPQ_TRG_MAJOR_VERSION = 0;
    ///Minor Acquisition version.
    static const unsigned int OPQ_TRG_MINOR_VERSION = 9;
}
#endif //TRIGGERING_VERSION_HPP
