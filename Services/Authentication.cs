using System.Security.Claims;
using Fasmga.Models;
using Microsoft.AspNetCore.Authentication;
using Microsoft.Extensions.Primitives;

namespace Fasmga.Services;

public class Auth : IAuthenticationHandler
{
    private readonly UserService _userService;

    private string? _token { get; set; }
    private User? _user { get; set; }

    private HttpContext _context { get; set; } = null!;

    public Auth(UserService UserService)
    {
        _userService = UserService;
    }

    public Task InitializeAsync(AuthenticationScheme _, HttpContext context)
    {
        Console.WriteLine("Hello world! INIT");
        _context = context;
        var header = context.Request.Headers.TryGetValue("Authentication", out StringValues authentication);

        if (!header || authentication[0] is null)
        {
            SendResponse(StatusCodes.Status400BadRequest, new { error = "No authorization header" });
            return Task.CompletedTask;
        }

        var auth = authentication[0].Split(" ");

        if (auth.Length != 2 || auth[0] != "Basic")
        {
            SendResponse(StatusCodes.Status400BadRequest, new { error = $"Authorization verb {auth[0]} invalid, use 'Basic <your token>'" });
            return Task.CompletedTask;
        }

        _token = auth[1];

        return Task.CompletedTask;
    }

    public async Task<AuthenticateResult> AuthenticateAsync()
    {
        await ChallengeAsync(null);

        if (_user is null)
        {
            return AuthenticateResult.Fail(new Exception("User doesn't exist"));
        }

        _user.Authenticate();

        var userClaimPrincipal = new ClaimsPrincipal(_user);
        var authTicket = new AuthenticationTicket(userClaimPrincipal, "Authentication");

        return AuthenticateResult.Success(authTicket);
    }

    public Task ChallengeAsync(AuthenticationProperties? _)
    {
        if (_token is null)
        {
            SendResponse(StatusCodes.Status400BadRequest, new { error = "No token provided" });
            return Task.CompletedTask;
        }

        _user = _userService.Get(_token);

        return Task.CompletedTask;
    }

    public Task ForbidAsync(AuthenticationProperties? _)
    {
        SendResponse(StatusCodes.Status401Unauthorized, new { error = "You aren't authorized!" });

        return Task.CompletedTask;
    }

    private void SendResponse(int statusCode, object message)
    {
        _context.Response.StatusCode = statusCode;
        _context.Response.ContentType = "application/json";
        _context.Response.WriteAsJsonAsync(message);

        _context.Response.StartAsync();
        _context.Response.CompleteAsync();
    }
}
