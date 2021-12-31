namespace Fasmga.Schema;

public class FasmgaDatabaseSettings : IFasmgaDatabaseSettings
{
    public string? ConnectionString { get; set; }
    public string? DatabaseName { get; set; }
    public string? UrlsCollectionName { get; set; }
    public string? UsersCollectionName { get; set; }
}

public interface IFasmgaDatabaseSettings
{
    string? ConnectionString { get; set; }
    string? DatabaseName { get; set; }
    string? UrlsCollectionName { get; set; }
    string? UsersCollectionName { get; set; }
}
