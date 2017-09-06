#include "Settings.hpp"
#include "util.hpp"
#include <string.h>
#include <fstream>

#include <boost/algorithm/string/trim.hpp>
#include <boost/algorithm/string/split.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/variant.hpp>
#include <boost/log/trivial.hpp>

using namespace opq;

Settings *Settings::_instance = NULL;

Settings::Settings() {
}

Settings *Settings::Instance() {
    if (_instance == NULL)
        _instance = new Settings();
    return _instance;
}

bool Settings::setSetting(std::string key, OPQSetting value) {
    boost::algorithm::trim(key);
    std::unique_lock<std::mutex> mlock(_mutex);

    std::map<std::string, SettingStruct>::iterator pos = _settings.lower_bound(key);
    if (pos == _settings.end() || (_settings.key_comp()(key, pos->first)))
        _settings[key].lastId = 0;
    _settings[key].setting = value;
    for(auto &func: _settings[key].callbacks){
                    func.second(value);
    }
    return true;
}

OPQSetting Settings::getSetting(std::string key) {
    boost::algorithm::trim(key);
    std::unique_lock<std::mutex> mlock(_mutex);
    std::map<std::string, SettingStruct>::iterator pos = _settings.lower_bound(key);
    if (pos != _settings.end() && !(_settings.key_comp()(key, pos->first))) {
        return pos->second.setting;
    }
    return "";
}

bool Settings::loadFromFile(std::string filename) {
    std::ifstream infile(filename.c_str());
    std::string line;
    if (!infile.is_open()) {
        BOOST_LOG_TRIVIAL(fatal) << "Could not load settings file "+ filename;
        return false;
    }
    std::unique_lock<std::mutex> mlock(_mutex);
    while (std::getline(infile, line)) {
        std::vector<std::string> strs;
        if (line[0] == '#')
            continue;
        boost::split(strs, line, boost::is_any_of(":"));
        if (strs.size() < 3)
            continue;
        std::string key = strs[0];
        std::string type = strs[1];
        std::string value = strs[2];
        for (size_t i = 3; i < strs.size(); i++) {
            value += ":" + strs[i];
        }
        boost::algorithm::trim(key);
        boost::algorithm::trim(type);
        boost::algorithm::trim(value);
        if (key.length() == 0 || type.length() == 0 || value.length() == 0)
            continue;
        OPQSetting setValue;
        try {
            switch (type.at(0)) {
                case 'U':
                    setValue = boost::lexical_cast<uint64_t>(value);
                    break;
                case 'F':
                    setValue = boost::lexical_cast<float>(value);
                    break;
                case 'I':
                    setValue = boost::lexical_cast<int>(value);
                    break;
                case 'S':
                    setValue = value;
                    break;
                case 'B':
                    if (value == "TRUE")
                        setValue = true;
                    else
                        setValue = false;
                    break;
                default:
                    BOOST_LOG_TRIVIAL(warning) <<  filename + " bad line: " + line;
                    throw boost::bad_lexical_cast();
            }
        }
        catch (boost::bad_lexical_cast &e) {
            continue;
        }
        _settings[key].setting = setValue;
    }
    return true;
}

bool Settings::saveToFile(std::string filename) {
    typedef std::map<std::string, SettingStruct> map_type;
    std::ofstream ofile(filename.c_str());
    std::string line;
    if (!ofile.is_open())
        return false;

    for(const map_type::value_type &myPair: _settings) {
                    OPQSetting val = myPair.second.setting;
                    std::string key = myPair.first;
                    line = key + ":";
                    switch (val.which()) {
                        case 0: //uint64_t
                            line += "U:" + boost::lexical_cast<std::string>(boost::get<uint64_t>(val));
                            break;
                        case 1: //float
                            line += "F:" + boost::lexical_cast<std::string>(boost::get<float>(val));
                            break;
                        case 2: //int
                            line += "I:" + boost::lexical_cast<std::string>(boost::get<int>(val));
                            break;
                        case 3: //string
                            line += "S:" + boost::get<std::string>(val);
                            break;
                        case 4: //bool
                            line += "B:";
                            if (boost::get<bool>(val))
                                line += "TRUE";
                            else
                                line += "FALSE";
                            break;
                    }
                    ofile << line << std::endl;
                }
    BOOST_LOG_TRIVIAL(info) <<  "exported " << filename;
    return true;
}

bool Settings::isSet(std::string key) {
    boost::algorithm::trim(key);
    std::unique_lock<std::mutex> mlock(_mutex);
    std::map<std::string, SettingStruct>::iterator pos = _settings.lower_bound(key);
    if (pos != _settings.end() && !(_settings.key_comp()(key, pos->first))) {
        return true;
    }
    return false;
}

OPQSetting Settings::erase(std::string key) {
    boost::algorithm::trim(key);
    std::unique_lock<std::mutex> mlock(_mutex);
    OPQSetting out;
    std::map<std::string, SettingStruct>::iterator pos = _settings.lower_bound(key);
    if (pos != _settings.end() && !(_settings.key_comp()(key, pos->first))) {
        out = pos->second.setting;
        _settings.erase(pos);
    }
    return out;
}

void Settings::clear() {
    std::unique_lock<std::mutex> mlock(_mutex);
    _settings.clear();
}

static void badget(std::string key){
    BOOST_LOG_TRIVIAL(info) <<  "Tried to access key " << key << " but it was not set or of wrong type";
}

uint64_t Settings::getUint64(std::string key) {
    try {
        return boost::get<uint64_t>(getSetting(key));
    }
    catch (boost::bad_get &e) {
        badget(key);
        return 0;
    }
}

float Settings::getFloat(std::string key) {
    try {
        return boost::get<float>(getSetting(key));
    }
    catch (boost::bad_get &e) {
        badget(key);
        return 0;
    }
}

int Settings::getInt(std::string key) {
    try {
        return boost::get<int>(getSetting(key));
    }
    catch (boost::bad_get &e) {
        badget(key);
        return 0;
    }
}

std::string Settings::getString(std::string key) {
    try {
        return boost::get<std::string>(getSetting(key));
    }
    catch (boost::bad_get &e) {
        badget(key);
        return "";
    }
}

bool Settings::getBool(std::string key) {
    try {
        return boost::get<bool>(getSetting(key));
    }
    catch (boost::bad_get &e) {
        badget(key);
        return false;
    }
}

int Settings::onChangeCallback(std::string key, std::function<void(OPQSetting)> func) {
    boost::algorithm::trim(key);
    std::unique_lock<std::mutex> mlock(_mutex);
    std::map<std::string, SettingStruct>::iterator pos = _settings.lower_bound(key);
    if (pos == _settings.end() || (_settings.key_comp()(key, pos->first))) {
        return -1;
    }
    _settings[key].lastId++;
    _settings[key].callbacks[_settings[key].lastId] = func;
    return _settings[key].lastId;
}

bool Settings::removeChangeCallback(std::string key, int id) {
    boost::algorithm::trim(key);
    std::unique_lock<std::mutex> mlock(_mutex);
    std::map<std::string, SettingStruct>::iterator pos = _settings.lower_bound(key);
    if (pos == _settings.end() || (_settings.key_comp()(key, pos->first))) {
        return false;
    }
    _settings[key].callbacks.erase(id);
    return true;
}