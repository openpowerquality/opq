#ifndef STATISTICS_H
#define STATISTICS_H

#include <vector>

class Statistics {
    private:
        class TimeInterval {
            private:
                int64_t start;
                int64_t end;
            public:
                TimeInterval(int64_t start, int64_t end);
                int64_t getStart();
                void setStart(int64_t start);
                int64_t getEnd();
                void setEnd(int64_t end);
        };
        int id;
        int64_t last;
        std::vector<TimeInterval> uptimes;
        std::vector<TimeInterval> downtimes;
        void addUptime(int64_t start, int64_t end);
        void addDowntime(int64_t start, int64_t end);
    public:
        Statistics(int id);
        int getId();
        int64_t getLast();
        void setLast(int64_t last);
        void printUptimes();
        void printDowntimes();
        void addNewTime(int64_t time);
        void logStatistics(std::ofstream * logFile);
};

#endif
