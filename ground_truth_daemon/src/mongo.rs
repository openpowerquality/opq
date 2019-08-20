use crate::scraper::DataPoint;
use bson::Document;
use mongodb::coll::Collection;

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
