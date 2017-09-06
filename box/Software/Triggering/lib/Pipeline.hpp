#ifndef ACQUISITION_PIPELINE_HPP
#define ACQUISITION_PIPELINE_HPP

#include "opqdata.hpp"
#include <thread>
namespace opq {
    namespace pipeline {

        /**
         * @brief Generalized multithreaded stream processing task.
         */
        class Slab {
        public:
            /**
             * @brief Create a new thread object.
             */
            Slab() {
            }

            /**
             * @brief Start the thread.
             * @param func Threaded function
             */
            void start(std::function<void(bool&) > func){
                _running = true;
                _t = std::thread([this,func] { func(_running); });
            }

            /**
             * @brief Stop the thread.
             */
            void stop(){
                _running = false;
                _t.join();
            }
        private:
            std::thread _t;
            bool _running;
        };

    };
};

#endif //ACQUISITION_PIPELINE_HPP
