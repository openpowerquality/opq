#include "Settings.hpp"
#include "util.hpp"
#include "json.hpp"
#include <string.h>
#include <fstream>

#include <boost/algorithm/string/trim.hpp>
#include <boost/algorithm/string/split.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/variant.hpp>
#include <boost/log/trivial.hpp>

using namespace opq;

using json = nlohmann::json;

Settings *Settings::_instance = NULL;

Settings::Settings() {
}

Settings *Settings::Instance() {
    if (_instance == NULL)
        _instance = new Settings();
    return _instance;
}

bool Settings::setSettingUnsafe(std::string key, OPQSetting value) {
  std::map<std::string, SettingStruct>::iterator pos = _settings.lower_bound(key);
  if (pos == _settings.end() || (_settings.key_comp()(key, pos->first)))
    _settings[key].lastId = 0;
  _settings[key].setting = value;
  for(auto &func: _settings[key].callbacks){
    func.second(value);
  }
  return true;
}

bool Settings::setSetting(std::string key, OPQSetting value) {
    boost::algorithm::trim(key);
    std::unique_lock<std::mutex> mlock(_mutex);
    return setSettingUnsafe(key, value);
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

    auto settings_json = json{};
    infile >> settings_json;

    for(auto it = settings_json.begin(); it != settings_json.end(); ++it) {
      auto t = it.value().type();

      switch(t) {
        case json::value_t::number_integer:
        case json::value_t::number_unsigned:
          setSettingUnsafe(it.key(), (int)it.value());
          break;

        case json::value_t::number_float:
          setSettingUnsafe(it.key(), (float)it.value());
          break;

        case json::value_t::string:
          setSettingUnsafe(it.key(), it.value().get<std::string>());
          break;

        case json::value_t::boolean:
          setSettingUnsafe(it.key(), (bool)it.value());
          break;

        default:
          throw std::runtime_error{"unknown json type"};
      }
    }

    return true;
}

bool Settings::saveToFile(std::string filename) {
    typedef std::map<std::string, SettingStruct> map_type;
    std::ofstream ofile(filename.c_str());
    std::string line;
    if (!ofile.is_open())
        return false;

    auto j = json{};

    for(const map_type::value_type &myPair: _settings) {
                    OPQSetting val = myPair.second.setting;
                    std::string key = myPair.first;

                    switch (val.which()) {
                        case 0: //uint64_t
                            j[key] = boost::get<int>(val);
                            break;
                        case 1: //float
                            j[key] = boost::get<float>(val);
                            break;
                        case 2: //int
                            j[key] = boost::get<int>(val);
                            break;
                        case 3: //string
                            line += "S:" + boost::get<std::string>(val);
                            j[key] = boost::get<std::string>(val);
                            break;
                        case 4: //bool
                            line += "B:";
                            j[key] = boost::get<bool>(val);
                            break;
                    }
                }
    j >> ofile;
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
