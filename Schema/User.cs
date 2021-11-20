namespace fasmga;

public class User {
	public string username { get; }
	public string apiToken { get; }
	public bool banned { get; set; }
	public bool premium { get; }

	public User(string username, string apiToken, bool banned) {
		this.username = username;
		this.apiToken = apiToken;
		this.banned = banned;
	}
}