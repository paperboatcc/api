using Microsoft.AspNetCore.Mvc;
using Fasmga.Services;
using Fasmga.Helpers;

namespace Fasmga.Controllers;

[ApiController]
[Route("/v1")]
public class ApiController : ControllerBase
{
	private ILogger<ApiController> _logger;
	private readonly UrlService _urlService;
	private readonly UserService _userService;
	private readonly Authorization _authorization;

	public ApiController(UrlService urlService, UserService userService, ILogger<ApiController> logger)
	{
		_urlService = urlService;
		_userService = userService;
		_authorization = new Authorization(_userService);
		_logger = logger;
	}

	// I can leave 404? yes. So why i put 204? because why not? 🙂
	[HttpGet]
	[ProducesResponseType(204)]
	public IActionResult Index() => NoContent();

	[HttpGet("urls")]
	public IActionResult GetUserUrls([FromHeader] string Authorization)
	{
		var AuthResult = _authorization.checkAuthorization(Authorization);

		if (!AuthResult.Allow || AuthResult.User is null)
		{
			return StatusCode(403, AuthResult.Message);
		}

		List<object> urls = new();
		_urlService.GetUserUrls(AuthResult.User).ForEach(u => {
			urls.Add(new { u.ID, u.owner, u.redirect, u.nsfw, u.captcha, u.unembedify, u.clicks, u.securitytype, u.creationdate });
		});

		return Ok(urls);
	}

	[HttpGet("urls/{id}")]
	public IActionResult GetUrlInfo([FromRoute] string id) {
		Url url = _urlService.Get(id);

		return Ok(new { url.ID, url.owner, url.redirect, url.nsfw, url.captcha, url.unembedify, url.clicks, url.securitytype, url.creationdate });
	}

	// [HttpGet("mongo")]
	// public IActionResult Mongo()
	// {
	// 	string? apiToken = Environment.GetEnvironmentVariable("TestingApiToken");

	// 	if (apiToken is null) {
	// 		return StatusCode(500, "Invalid apiToken"); // 500 because it's a env variable
	// 	}

	// 	User owner = _userService.Get(apiToken);

	// 	Url url = new(owner, "https://example.com", false);

	// 	for (int i = 0; i < 4; i++)
	// 	{
	// 		url.CheckUnique((UrlUniqueValues) i, _urlService);
	// 	}

	// 	_urlService.Create(url);

	// 	// return NoContent(); // approximately 137ms ( create )

	// 	Url find = _urlService.Get("nnTaX");

	// 	if (find is null) {
	// 		return NotFound("url ID invalid");
	// 	}

	// 	return Ok(find); // approximately 1620 ms ( find + create )
	// }
}

