using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace fasmga.Controllers;

[ApiController]
[Route("/v1")]
public class ApiController : ControllerBase
{
	private ILogger<ApiController> Logger;

	public ApiController(ILogger<ApiController> logger) {
		Logger = logger;
	}

	[HttpGet()]
	public IActionResult Get()
	{
		return Ok("Hello world!");
	}

	[HttpGet("test")]
	public IActionResult Test() {
		Url url = new(id: "testu", redirect: "https://example.com", nsfw: false, owner: new User("mona", "apitoken", false));

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
}