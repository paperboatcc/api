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
		var AuthResult = _authorization.checkAuthorization(Authorization, Request);

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
		var AuthResult = _authorization.checkAuthorization(Authorization, Request);

		if (!AuthResult.Allow || AuthResult.User is null)
		{
			return StatusCode(403, AuthResult.Message);
		}

		Url? url = await urlRequest.ToUrl(AuthResult.User, _urlService);

		if (url is null)
		{
			return BadRequest(new { message = "Url id is already used!" });
		}

		try {
			_urlService.Create(url);
			return Created("/v1/urls", url);
		}
		catch {
			return StatusCode(500, new { message = "failed to create url" });
		}
	}

	// Here is the explanation for the code above:
	// 1. First we check if the user has authorization to use the endpoint.
	// 2. Creates a new Url instance from the request body
	// 3. Check if user can delete that url
	// 4. Delete the url
	// 5. Respond to user
	[HttpDelete("delete")]
	public IActionResult DeleteUrl([FromHeader] string Authorization, [FromQuery] string id)
	{
		var AuthResult = _authorization.checkAuthorization(Authorization, Request);

		if (!AuthResult.Allow || AuthResult.User is null)
		{
			return StatusCode(403, AuthResult.Message);
		}

		Url? url = _urlService.Get(id);

		if (url is null)
		{
			return NotFound();
		}

		if (url.Owner != AuthResult.User.Username)
		{
			return StatusCode(401, new { error = "You cant delete url that aren't your" });
		}

		try
		{
			_urlService.Remove(url);
			return Ok(new { message = $"Deleted url with id {id}" });
		} catch {
			return StatusCode(500, new { error = "Cannot delete url" });
		}
	}

	[HttpPatch("edit")]
	public IActionResult EditUrl([FromHeader] string Authorization, [FromQuery] string id, [FromBody] UrlEditRequest body)
    {
		var AuthResult = _authorization.checkAuthorization(Authorization, Request);

		if (!AuthResult.Allow || AuthResult.User is null)
		{
			return StatusCode(403, AuthResult.Message);
		}

		Url? url = _urlService.Get(id);

		if (url is null)
		{
			return NotFound();
		}

		if (url.Owner != AuthResult.User.Username)
		{
			return StatusCode(401, new { error = "You cant edit url that aren't your" });
		}

		try
		{
			Url editedUrl = body.ToUrl(url);
			_urlService.Update(id, editedUrl);
			return Ok(editedUrl);
		} catch {
			return StatusCode(500, new { error = "Cannot edit url" });
		}
	}
}
