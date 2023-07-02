def test_mongo(app, mongo_db):
    _, mongo = mongo_db
    name = app.config["MONGO_COLLECTION_NAME"]
    collection = mongo[name]

    query = collection.insert_one({"test": "xxxx"})
    assert query.acknowledged
    query2 = collection.find_one({"test": "xxxx"})
    assert query2["test"] == "xxxx"


def test_more_mongo(app, mongo_db):
    _, mongo = mongo_db
    name = app.config["MONGO_COLLECTION_NAME"]
    collection = mongo[name]

    query_big = collection.insert_many([{"test": "first test"}, {"test": "second test"}])
    assert query_big.acknowledged
    query2 = collection.find()
    query2 = list(query2)
    assert len(query2) == 2
