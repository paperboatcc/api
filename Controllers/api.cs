using Microsoft.AspNetCore.Mvc;

namespace fasmga.Controllers;

[ApiController]
[Route("/v1")]
public class Api : ControllerBase
{
	[HttpGet()]
	public IActionResult Get()
	{
		return Ok("Hello world!");
	}

	[HttpGet("test")]
	public IActionResult Test() {
		Url url = new("testu", new User("mona", "apitoken", false), "https://example.com", false);

		return Ok(System.Text.Json.JsonSerializer.Serialize(url));
	}
}