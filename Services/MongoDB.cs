using MongoDB.Driver;

namespace fasmga.Services;

public class Database {

	public MongoClient Client { get; set; }

	public Database() {
		Client = new MongoClient("mongodb://localhost:27017");
	}
}
