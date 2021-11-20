using Microsoft.AspNetCore.Mvc;
using System.Text.Json;
using MongoDB.Driver;
using MongoDB.Bson;
using fasmga.Services;
namespace fasmga.Controllers;

[ApiController]
[Route("/v1")]
public class ApiController : ControllerBase
{
	private ILogger<ApiController> Logger;
	private MongoClient Database;

	public ApiController(Database database, ILogger<ApiController> logger) {
		Database = database.Client;
		Logger = logger;
	}

	[HttpGet()]
	public IActionResult Get()
	{
		return Ok("Hello world!");
	}

	[HttpGet("test")]
	public IActionResult Test() {
		Url url = new(ID: "testu", redirect: "https://example.com", nsfw: false, owner: new User("mona", "apitoken", false));

		Logger.LogInformation(JsonSerializer.Serialize<Url>(url));

		return Ok(JsonSerializer.Serialize<Url>(url));
	}

	[HttpGet("header")]
	[ProducesResponseType(200)]
	[ProducesResponseType(400)]
	public IActionResult Header([FromHeader] string Authentication) {
		Logger.LogInformation($"Auth healder: {Authentication}");

		if (!Authentication.StartsWith("Basic ")) {
			return BadRequest("Invalid token type. Use a Basic token!");
		}

		string token = Authentication.Split("Basic ")[1];

		Logger.LogInformation($"Token: {token}");

		return Ok($"Here your token {token}");
	}

	[HttpGet("mongo")]
	public IActionResult Mongo() {
    IMongoDatabase database = Database.GetDatabase("testing");
    IMongoCollection<BsonDocument> collection = database.GetCollection<BsonDocument>("url");

		BsonDocument document = new Url($"test-{(int) (DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalSeconds}", new User("sciopone", "tokenone", false), "https://mio", false).ToBsonDocument();

		collection.InsertOne(document);

		FilterDefinition<BsonDocument> filter = Builders<BsonDocument>.Filter.Eq("ID", "wlhywgnx");

		IFindFluent<BsonDocument, BsonDocument> query = collection.Find(filter);

		if (query.CountDocuments() == 0) {
			return NotFound("No document found");
		}

		BsonDocument result = query.FirstOrDefault();
		result.Remove("_id");

		return Ok(result.ToJson());
	}
}
