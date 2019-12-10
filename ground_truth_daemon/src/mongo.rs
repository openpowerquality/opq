use crate::conf::GroundTruthDaemonConfig;
use crate::scraper::DataPoint;


pub fn init(
    config: &GroundTruthDaemonConfig,
) -> Result<(mongodb::Client, mongodb::coll::Collection), String> {
    let mongo_client: mongodb::Client =
        mongodb::Client::connect(&config.mongo_host, config.mongo_port)
            .map_err(|e| format!("Error getting Mongo client: {:?}", e))?;
    let ground_truth_coll = mongo_client.db("opq2").collection("ground_truth");

    Ok((mongo_client, ground_truth_coll))
}

pub fn store_data_points(coll: &Collection, data_points: &Vec<DataPoint>) -> Result<(), String> {
    let mut documents: Vec<Document> = Vec::new();

    for data_point in data_points {
        let doc = bson::to_bson(data_point)
            .map_err(|e| format!("Error converting data point into BSON: {:?}", e))?;

        if let bson::Bson::Document(document) = doc {
            documents.push(document);
        } else {
            return Err("Error converting the BSON object into a MongoDB document".to_string());
        }
    }

    match coll.insert_many(documents, None) {
        Ok(res) => match res.bulk_write_exception {
            None => Ok(()),
            Some(ex) => Err(format!("Error storing documents to DB: {}", ex.message)),
        },
        Err(err) => Err(format!("Error storing documents to DB: {:?}", err)),
    }
}
