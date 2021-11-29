using Fasmga.Schema;
using MongoDB.Driver;

namespace Fasmga.Services;

public class UrlService
{
	private readonly IMongoCollection<Url> _urls;

	public UrlService(IFasmgaDatabaseSettings settings)
	{
		string? connectionString = Environment.GetEnvironmentVariable("MongoDBConnectionString");

		if (connectionString is null) {
			throw new Exception("MongoDBConnectionString environment variable is not set.");
		}

		MongoClient client = new(connectionString);
		IMongoDatabase database = client.GetDatabase(settings.DatabaseName);

		_urls = database.GetCollection<Url>(settings.UrlsCollectionName);
	}

	public List<Url> Get() => _urls.Find(Url => true).ToList();

	public dynamic Get(string id) => _urls.Find(Url => Url.ID == id).FirstOrDefault();

	public List<Url> GetUserUrls(User user) => Get().Where(u => u.Owner == user.Username).ToList();
	public Url Create(Url Url)
	{
		_urls.InsertOne(Url);
		return Url;
	}

	public void Update(string id, Url UrlIn) => _urls.ReplaceOne(Url => Url.ID == id, UrlIn);

	public void Remove(Url UrlIn) => _urls.DeleteOne(Url => Url.ID == UrlIn.ID);

	public void Remove(string id) => _urls.DeleteOne(Url => Url.ID == id);
}
