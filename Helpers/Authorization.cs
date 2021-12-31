using Fasmga.Services;

namespace Fasmga.Helpers;

class Authorization
{

    private readonly UserService _userService;

    public Authorization(UserService UserService)
    {
        _userService = UserService;
    }
    public AuthorizationResponse checkAuthorization(string Authorization, HttpRequest request)
    {
        string[] auth = Authorization.Split(" ");

        if (auth.Length != 2 || auth[0] != "Basic")
        {
            return new AuthorizationResponse(false, $"Authorization {auth[0]} is invalid or unknown, use Basic authorization", null, null);
        }

        if (string.IsNullOrEmpty(request.Headers["X-Real-IP"]))
        {
            return new AuthorizationResponse(false, "IP invalid, use a real one", null, null);
        }

        User? user = _userService.Get(auth[1]);

        if (user is null)
        {
            return new AuthorizationResponse(false, "Invalid Token", null, null);
        }

        return new AuthorizationResponse(true, $"Token {auth[1]} is valid", auth[1], user);
    }
}


class AuthorizationResponse
{
    public bool Allow { get; set; }
    public object Message { get; set; }
    public string? Token { get; set; }
    public User? User { get; set; }

    public AuthorizationResponse(bool allow, string message, string? token, User? user)
    {
        Allow = allow;
        Message = new { message };
        Token = token;
        User = user;
    }
}

