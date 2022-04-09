using Fasmga.Services;
using Fasmga.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace Fasmga.Controllers;

[ApiController]
[Route("/v1")]
public class ApiController : ControllerBase
{
    private readonly UrlService _urlService;
    private readonly UserService _userService;

    public ApiController(UrlService urlService, UserService userService)
    {
        _urlService = urlService;
        _userService = userService;
    }

    /// <summary>
    /// Validate user and retrive all url(s) from user
    /// </summary>
    [HttpGet("urls")]
    [Authorize(AuthenticationSchemes = "Authentication")]
    public IActionResult GetUserUrls()
    {
        List<object> urls = new();
        _urlService.GetUserUrls(HttpContext.User).ForEach(u =>
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
    [Authorize(AuthenticationSchemes = "Authentication")]
    public IActionResult CreateUrl([FromBody] UrlRequest urlRequest)
    {
        var url = urlRequest.ToUrl(HttpContext.User, _urlService);

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
    public IActionResult DeleteUrl([FromQuery] string id)
    {
        Url? url = _urlService.Get(id);

        if (url is null)
        {
            return NotFound();
        }

        if (url.Owner != ((User)HttpContext.User).Username)
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
        Url? url = _urlService.Get(id);

        if (url is null)
        {
            return NotFound();
        }

        if (url.Owner != ((User)HttpContext.User).Username)
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
