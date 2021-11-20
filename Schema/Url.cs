using MongoDB.Bson;
using OtpNet;

namespace fasmga;

public class Url {
	public string ID { get; }
	public string redirect_url { get; }
	public string owner { get; }
	public string password { get; set; }
	public bool nsfw { get; set; }
	public bool captcha { get; set; }
	public int clicks { get; set; }
	public bool unembedify { get; set; }
	public int deletedate { get; set; }
	public object editinfo { get; set; }
	public string qruuid1 { get; set; }
	public string qruuid2 { get; set; }
	public string securitytype { get; set; }
	public string securitytotp { get; set; }
	public int creationdate { get; }

	public Url(string ID, User owner, string redirect, bool nsfw, string password = "", bool captcha = false, bool unembedify = false) {
		byte[] key = KeyGeneration.GenerateRandomKey(20);
		string base32String = Base32Encoding.ToString(key);

		this.ID = ID;
		this.redirect_url = redirect;
		this.owner = owner.username;
		this.nsfw = nsfw;
		this.captcha = captcha;
		this.unembedify = unembedify;
		this.password = password;

		securitytype = password is null || password == string.Empty ? "none" : "password";
		creationdate = (int) (DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalSeconds;
		clicks = 0;
		deletedate = 0;
		securitytotp = GenerateTotp();
		editinfo = new Object();
		qruuid1 = GenerateUuid1();
		qruuid2 = GenerateUuid2();
	}

	public string GenerateUuid1() {
		string newUuid1 = Guid.NewGuid().ToString();

		this.qruuid1 = newUuid1;
		return newUuid1;
	}

	public string GenerateUuid2() {
		string newUuid2 = Guid.NewGuid().ToString();

		this.qruuid2 = newUuid2;
		return newUuid2;
	}

	public string GenerateTotp() {
		byte[] key = KeyGeneration.GenerateRandomKey(20);
		string base32String = Base32Encoding.ToString(key);

		this.securitytotp = base32String;
		return base32String;
	}

	public BsonDocument ToBsonDocument() {
		return new BsonDocument()
		{
			{ "ID", ID },
			{ "redirect_url", redirect_url },
			{ "owner", owner },
			{ "password", password },
			{ "nsfw", nsfw },
			{ "captcha", captcha },
			{ "unembedify", unembedify },
			{ "qruuid1", qruuid1 },
			{ "qruuid2", qruuid2 },
			{ "editinfo", editinfo.ToBsonDocument() },
			{ "clicks", clicks },
			{ "securitytype", securitytype },
			{ "securitytotp", securitytotp },
			{ "creationdate", creationdate },
			{ "deletedate", deletedate },
		};
	}
}
