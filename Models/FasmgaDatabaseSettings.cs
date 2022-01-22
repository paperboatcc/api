namespace Fasmga.Models;

public class FasmgaDatabaseSettings : IFasmgaDatabaseSettings
{
    public string? DatabaseName { get; set; }
    public string? UrlsCollectionName { get; set; }
    public string? UsersCollectionName { get; set; }
}

public interface IFasmgaDatabaseSettings
{
    string? DatabaseName { get; set; }
    string? UrlsCollectionName { get; set; }
    string? UsersCollectionName { get; set; }
}
