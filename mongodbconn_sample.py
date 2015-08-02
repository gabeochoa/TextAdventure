import pymongo

def mongoconn():
	MONGO_URL = "mongodb://username:password@host:port/database"
	connection = pymongo.Connection(MONGO_URL)
	db = connection.get_default_database()
	print db.collection_names()
	return db['collection']