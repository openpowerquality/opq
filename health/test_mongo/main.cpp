#include <cstdint>
#include <iostream>
#include <vector>
#include <bsoncxx/json.hpp>
#include <bsoncxx/builder/stream/document.hpp>
#include <mongocxx/client.hpp>
#include <mongocxx/stdx.hpp>
#include <mongocxx/uri.hpp>
#include <mongocxx/instance.hpp>

using bsoncxx::builder::stream::close_array;
using bsoncxx::builder::stream::close_document;
using bsoncxx::builder::stream::document;
using bsoncxx::builder::stream::finalize;
using bsoncxx::builder::stream::open_array;
using bsoncxx::builder::stream::open_document;

int main() {
    mongocxx::instance instance{};
    // Defaults to mongodb://localhost:27017
    mongocxx::client client{mongocxx::uri{}};
    mongocxx::database db = client["opq"];
    mongocxx::collection coll = db["measurements"];

    bsoncxx::stdx::optional<bsoncxx::document::value> maybe_result = 
        coll.find_one(document{} << finalize);

    if (maybe_result) {
        std::cout << bsoncxx::to_json(*maybe_result) << std::endl;
    } else {
        std::cout << "bruh" << std::endl;
    }

    return 0;
}





