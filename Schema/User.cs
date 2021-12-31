using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using Newtonsoft.Json;

namespace Fasmga;

public class User
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    private string? _id { get; set; }
    [BsonElement("username")]
    [JsonProperty("username")]
    public string Username { get; set; }
    [BsonElement("password")]
    [JsonProperty("password")]
    public string? Password { get; set; }
    [BsonElement("login_token")]
    [JsonProperty("login_token")]
    public string? LoginToken { get; set; }
    [BsonElement("api_token")]
    [JsonProperty("api_token")]
    public string ApiToken { get; set; }
    [BsonElement("is_banned")]
    [JsonProperty("is_banned")]
    public bool Banned { get; set; }
    [BsonElement("totp")]
    [JsonProperty("totp")]
    public string? Totp { get; set; }
    [BsonElement("2fa_enabled")]
    [JsonProperty("2fa_enabled")]
    public bool? Twofactorauth { get; set; }
    [BsonElement("is_premium")]
    [JsonProperty("is_premium")]
    public bool Premium { get; set; }
    [BsonElement("creation_date")]
    [JsonProperty("creation_date")]
    public int? Creationdate { get; set; }

    public User(string username, string apiToken, bool banned, bool premium)
    {
        Username = username;
        ApiToken = apiToken;
        Banned = banned;
        Premium = premium;
    }

    public override string ToString()
    {
        return JsonConvert.SerializeObject(this);
    }
}
