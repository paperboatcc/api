using OtpNet;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using Fasmga.Services;
using Fasmga.Helpers;

namespace Fasmga;

public enum UrlUniqueValues
{
	ID,
	qruuid1,
	qruuid2,
	securitytotp,
}

public class Url {
  [BsonId]
  [BsonRepresentation(BsonType.ObjectId)]
	private string? _id { get; set; }
	public string ID { get; set; }
	[BsonElement("redirect_url")]
	public string redirect { get; set; }
	public string owner { get; set; }
	public string password { get; set; }
	public bool nsfw { get; set; }
	public bool captcha { get; set; }
	public bool unembedify { get; set; }
	public int clicks { get; set; }
	public int deletedate { get; set; }
	public object editinfo { get; set; }
	public string qruuid1 { get; set; }
	public string qruuid2 { get; set; }
	public string securitytype { get; set; }
	public string securitytotp { get; set; }
	public int creationdate { get; set; }

	public Url(User owner, string redirect, bool nsfw, UrlOptions? idOptions = null, string password = "", bool captcha = false, bool unembedify = false)
	{
		this.redirect = redirect;
		this.owner = owner.username;
		this.nsfw = nsfw;
		this.captcha = captcha;
		this.unembedify = unembedify;
		this.password = password;

		ID = GenerateID(idOptions);
		securitytype = password is null || password == string.Empty ? "none" : "password";
		creationdate = (int) (DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalSeconds;
		clicks = 0;
		deletedate = 0;
		securitytotp = GenerateTotp();
		editinfo = new Object();
		qruuid1 = GenerateUuid1();
		qruuid2 = GenerateUuid2();
	}

	public string GenerateUuid1()
	{
		string newUuid1 = Guid.NewGuid().ToString();

		this.qruuid1 = newUuid1;
		return newUuid1;
	}

	public string GenerateUuid2()
	{
		string newUuid2 = Guid.NewGuid().ToString();

		this.qruuid2 = newUuid2;
		return newUuid2;
	}

	public string GenerateTotp()
	{
		byte[] key = KeyGeneration.GenerateRandomKey(20);
		string base32String = Base32Encoding.ToString(key);

		this.securitytotp = base32String;
		return base32String;
	}

	public string GenerateID(UrlOptions? options = null) {
		if (options is null) {
			options = new UrlOptions();
		}
		
		if (options.staticID is not null)
		{
			return options.staticID;
		}

		return UrlIDGenerator.Generate(options.genIDType ?? "lowercase", options.length ?? 8);
	}

	public int CheckUnique(UrlUniqueValues value, UrlService service)
	{
		int attempt = 0;

		switch (value)
		{
			case UrlUniqueValues.ID:
				while (service.Get().Where(u => u.ID == ID).Count() > 0 && attempt < 100) {
					ID = GenerateID();
					attempt++;
				}
				break;
			case UrlUniqueValues.qruuid1:
				while (service.Get().Where(u => u.qruuid1 == qruuid1).Count() > 0 && attempt < 100) {
					qruuid1 = GenerateUuid1();
					attempt++;
				}
				break;
			case UrlUniqueValues.qruuid2:
				while (service.Get().Where(u => u.qruuid2 == qruuid2).Count() > 0 && attempt < 100) {
					qruuid2 = GenerateUuid2();
					attempt++;
				}
				break;
			case UrlUniqueValues.securitytotp:
				while (service.Get().Where(u => u.securitytotp == securitytotp).Count() > 0 && attempt < 100) {
					securitytotp = GenerateTotp();
					attempt++;
				}
				break;
			default:
				while (service.Get().Where(u => u.ID == ID).Count() > 0 && attempt < 100) {
					ID = GenerateID();
					attempt++;
				}
				break;
		}

		return attempt;
	}
}

public class UrlOptions {
	public string? staticID { get; set; }
	public string? genIDType { get; set; }
	public int? length { get; set; }

	public UrlOptions()
	{
		staticID = null;
		genIDType = "lowercase";
		length = 8;
	}

	public UrlOptions(string ID)
	{
		staticID = ID;
		genIDType = null;
		length = null;
	}

	public UrlOptions(string genIDType, int length = 8)
	{
		staticID = null;
		this.genIDType = genIDType;
		this.length = length;
	}
}
