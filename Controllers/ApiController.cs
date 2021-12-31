using Fasmga.Services;
using Microsoft.AspNetCore.Mvc;

namespace Fasmga.Controllers;

[ApiController]
[Route("/v1")]
public class ApiController : ControllerBase
{
    private readonly ILogger<ApiController> _logger;
    private readonly UrlService _urlService;
    private readonly UserService _userService;
    private readonly Authorization _authorization;

    public ApiController(UrlService urlService, UserService userService, Authorization authorization, ILogger<ApiController> logger)
    {
        _urlService = urlService;
        _userService = userService;
        _authorization = authorization;
        _logger = logger;
    }

    /// <summary>
    /// Validate user and retrive all url(s) from user
    /// </summary>
    [HttpGet("urls")]
    public IActionResult GetUserUrls([FromHeader] string authorization)
    {
        (bool allow, object message) = _authorization.ValidateUser(authorization, out User? user);

        if (!allow || user is null)
        {
            return StatusCode(403, message);
        }

        List<object> urls = new();
        _urlService.GetUserUrls(user).ForEach(u =>
        {
            urls.Add(u.ToObject());
        });

        return Ok(urls);
    }

    /// <summary>
    /// Give back information about the url from the id
    /// </summary>
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

    /// <summary>
    /// Validate user with healder and then generate the url
    /// </summary>
    [HttpPost("create")]
    public async Task<IActionResult> CreateUrl([FromHeader] string authorization, [FromBody] UrlRequest urlRequest)
    {
        (bool allow, object message) = _authorization.ValidateUser(authorization, out User? user);

        if (!allow || user is null)
        {
            return StatusCode(403, message);
        }

        Url? url = await urlRequest.ToUrl(user, _urlService);

        if (url is null)
        {
            return BadRequest(new { message = "Url id is already used!" });
        }

        try
        {
            _urlService.Create(url);
            return Created("/v1/urls", url);
        }
        catch
        {
            return StatusCode(500, new { message = "failed to create url" });
        }
    }

    /// <summary>
    /// Validate user that make the request and then delete url
    /// </summary>
    [HttpDelete("delete")]
    public IActionResult DeleteUrl([FromHeader] string authorization, [FromQuery] string id)
    {
        (bool allow, object message) = _authorization.ValidateUser(authorization, out User? user);

        if (!allow || user is null)
        {
            return StatusCode(403, message);
        }

        Url? url = _urlService.Get(id);

        if (url is null)
        {
            return NotFound();
        }

        if (url.Owner != user.Username)
        {
            return StatusCode(401, new { error = "You cant delete url that aren't your" });
        }

        try
        {
            _urlService.Remove(url);
            return Ok(new { message = $"Deleted url with id {id}" });
        }
        catch
        {
            return StatusCode(500, new { error = "Cannot delete url" });
        }
    }

    /// <summary>
    /// Validate user with healder and then edit url
    /// </summary>
    [HttpPatch("edit")]
    public IActionResult EditUrl([FromHeader] string authorization, [FromQuery] string id, [FromBody] UrlEditRequest body)
    {
        (bool allow, object message) = _authorization.ValidateUser(authorization, out User? user);

        if (!allow || user is null)
        {
            return StatusCode(403, message);
        }

        Url? url = _urlService.Get(id);

        if (url is null)
        {
            return NotFound();
        }

        if (url.Owner != user.Username)
        {
            return StatusCode(401, new { error = "You cant edit url that aren't your" });
        }

        try
        {
            Url editedUrl = body.ToUrl(url);
            _urlService.Update(id, editedUrl);
            return Ok(editedUrl);
        }
        catch
        {
            return StatusCode(500, new { error = "Cannot edit url" });
        }
    }
}
