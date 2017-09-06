#ifndef ACQUISITION_READER_H
#define ACQUISITION_READER_H
#include "opqdata.hpp"
#include "Settings.hpp"

namespace opq {

    /**
     * @brief This class is responsible for data acquisition.
     * Reader class communicates with the opq kernel driver and transfers ADC samples into userland.
     */
    class Reader {
    public:
        /**
         * @brief Creates a new Reader and set it to output OPQCycle into the queue q.
         * @param q output queue.
         */
        Reader(opq::data::MeasurementQueue &q);
        /**
         * @brief  Close the device and release the queue.
         */
        ~Reader();

        void loop(bool &loop);

    private:
        void _onFramesPerMeasurementChange(OPQSetting s);

        int _frames_per_measurement;
        int _fpm_callback_id;
        opq::data::MeasurementQueue _q;
        int _fd;
    };

}

#endif //ACQUISITION_READER_H
