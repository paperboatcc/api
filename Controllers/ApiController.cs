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

	// Here is the explanation for the code above:
	// 1. First we check if the user has authorization to use the endpoint.
	// 2. Get the URLs by User Authorization
	// 3. Respond with the list of Url 
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
			urls.Add(u.ToObject());
		});

		return Ok(urls);
	}

	// The code above does the following:
	// 1. Get the URL by ID
	// 2. Respond with that
	[HttpGet("urls/{id}")]
	public IActionResult GetUrlInfo([FromRoute] string id)
	{
		Url url = _urlService.Get(id);

		if (url is null)
		{
			return NotFound();
		}

		return Ok(url.ToObject());
	}

	// Here is the explanation for the code above:
	// 1. First we check if the user has authorization to use the endpoint.
	// 2. Creates a new Url instance from the request body
	// 3. Save to database
	// 4. Respond with the Url
	[HttpPost("create")]
	public async Task<IActionResult> CreateUrl([FromHeader] string Authorization, [FromBody] UrlRequest urlRequest)
	{
		var AuthResult = _authorization.checkAuthorization(Authorization);

		if (!AuthResult.Allow || AuthResult.User is null)
		{
			return StatusCode(403, AuthResult.Message);
		}

		Url? url = await urlRequest.ToUrl(AuthResult.User, _urlService);

		if (url is null)
		{
			return BadRequest(new { message = "Url id is already used!" });
		}

		_urlService.Create(url);

		return Created("/v1/urls", url);
	}
}
