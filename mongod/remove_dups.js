// Credit to https://stackoverflow.com/a/39013357

var conn = new Mongo();
var db = conn.getDB("opq");
var duplicates = [];

db.runCommand(
    {aggregate: "events",
        pipeline: [
            { $group: { _id: { event_id: "$event_id"}, dups: { "$addToSet": "$_id" }, count: { "$sum": 1 } }},
            { $match: { count: { "$gt": 1 }}}
        ],
        allowDiskUse: true }
)
    .result
    .forEach(function(doc) {
        doc.dups.shift();
        doc.dups.forEach(function(dupId){ duplicates.push(dupId); })
    })
printjson(duplicates); //optional print the list of duplicates to be removed

db.events.remove({_id:{$in:duplicates}});