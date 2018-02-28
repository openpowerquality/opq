#ifndef STATISTICS_H
#define STATISTICS_H

class Statistics {
    private:
        int64_t uptime;
        int64_t downtime;
        int id;
    public:
        Statistics(int id);
        int getId();
        int getUptime();
        void setUptime(int64_t uptime);
        int getDowntime();
        void setDowntime(int64_t downtime);
        void logStatistics(std::ofstream * logFile);
};

#endif
