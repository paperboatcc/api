using Fasmga.Models;

namespace Fasmga.Services;

public class Authentication
{
    private readonly UserService _userService;

    public Authentication(UserService UserService)
    {
        _userService = UserService;
    }

    /// <summary>
    /// Validate user based on his ApiToken
    /// </summary>
    public (bool, object) ValidateUser(string authorization, out User? user)
    {
        string[] authorizationArr = authorization.Split(" ");

        if (authorizationArr.Length != 2 || authorizationArr[0] != "Basic")
        {
            user = null;
            return (false, new { error = $"Authorization verb {authorizationArr[0]} invalid, use \"Basic <your token>\"" });
        }

        User? user1 = _userService.Get(authorizationArr[1]);
        user = user1;

        if (user1 is null)
        {
            return (false, new { error = "User with given token not found" });
        }

        return (true, new { message = "Valid user" });
    }
}
