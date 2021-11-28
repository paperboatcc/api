using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace Fasmga;

public class User {
	[BsonId]
  [BsonRepresentation(BsonType.ObjectId)]
	private string? _id { get; set; }
	public string username { get; set; }
	public string? password { get; set; }
	[BsonElement("login_token")]
	public string? loginToken { get; set; }
	[BsonElement("api_token")]
	public string apiToken { get; set; }
	[BsonElement("is_banned")]
	public bool banned { get; set; }
	public string? totp { get; set; }
	[BsonElement("2fa_enabled")]
	public bool? twofactorauth { get; set; }
	[BsonElement("is_premium")]
	public bool premium { get; set; }
	[BsonElement("creation_date")]
	public int? creationdate { get; set; }

	public User(string username, string apiToken, bool banned, bool premium)
	{
		this.username = username;
		this.apiToken = apiToken;
		this.banned = banned;
		this.premium = premium;
	}
}
