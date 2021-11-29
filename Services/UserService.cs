using Fasmga.Schema;
using MongoDB.Driver;

namespace Fasmga.Services;

public class UserService
{
	private readonly IMongoCollection<User> _users;

	public UserService(IFasmgaDatabaseSettings settings)
	{
		string? connectionString = Environment.GetEnvironmentVariable("MongoDBConnectionString");

		if (connectionString is null) {
			throw new Exception("MongoDBConnectionString environment variable is not set.");
		}

		MongoClient client = new(connectionString);
		IMongoDatabase database = client.GetDatabase(settings.DatabaseName);

		_users = database.GetCollection<User>(settings.UsersCollectionName);
	}

	public List<User> Get() => _users.Find(User => true).ToList();

	public User Get(string apiToken) => _users.Find(User => User.ApiToken == apiToken).FirstOrDefault();
	public User Create(User User)
	{
		_users.InsertOne(User);
		return User;
	}

	public void Update(string apiToken, User UserIn) => _users.ReplaceOne(User => User.ApiToken == apiToken, UserIn);

	public void Remove(User UserIn) => _users.DeleteOne(User => User.ApiToken == User.ApiToken);

	public void Remove(string apiToken) => _users.DeleteOne(User => User.ApiToken == apiToken);
}
