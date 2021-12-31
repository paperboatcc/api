using Fasmga.Helpers;
using Fasmga.Services;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using Newtonsoft.Json;
using OtpNet;
using System.Security.Cryptography;
using System.Text;

namespace Fasmga;

public enum UrlUniqueValues
{
    ID,
    qruuid1,
    qruuid2,
    securitytotp,
}

public class Url
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    private string? _id { get; set; }
    public string ID { get; set; }
    [BsonElement("redirect_url")]
    [JsonProperty("redirect_url")]
    public string Redirect { get; set; }
    [BsonElement("owner")]
    [JsonProperty("owner")]
    public string Owner { get; set; }
    [BsonElement("password")]
    [JsonProperty("password")]
    public string? Password { get; set; }
    [BsonElement("nsfw")]
    [JsonProperty("nsfw")]
    public bool Nsfw { get; set; }
    [BsonElement("captcha")]
    [JsonProperty("captcha")]
    public bool Captcha { get; set; }
    [BsonElement("unembedify")]
    [JsonProperty("unembedify")]
    public bool Unembedify { get; set; }
    [BsonElement("clicks")]
    [JsonProperty("clicks")]
    public int Clicks { get; set; }
    [BsonElement("deletedate")]
    [JsonProperty("deletedate")]
    public int Deletedate { get; set; }
    [BsonElement("editinfo")]
    [JsonProperty("editinfo")]
    public object Editinfo { get; set; }
    [BsonElement("qruuid1")]
    [JsonProperty("qruuid1")]
    public string Qruuid1 { get; set; }
    [BsonElement("qruuid2")]
    [JsonProperty("qruuid2")]
    public string Qruuid2 { get; set; }
    [BsonElement("securitytype")]
    [JsonProperty("securitytype")]
    public string Securitytype { get; set; }
    [BsonElement("securitytotp")]
    [JsonProperty("securitytotp")]
    public string Securitytotp { get; set; }
    [BsonElement("creationdate")]
    [JsonProperty("creationdate")]
    public int Creationdate { get; set; }
    private UrlOptions IdOptions { get; set; }

    public Url(User owner, string redirect, bool nsfw, UrlOptions? idOptions = null, string password = "", bool captcha = false, bool unembedify = false)
    {
        Redirect = redirect;
        Owner = owner.Username;
        Nsfw = nsfw;
        Captcha = captcha;
        Unembedify = unembedify;
        Password = string.IsNullOrEmpty(password) ? "" : Convert.ToHexString(SHA512.Create().ComputeHash(Encoding.UTF8.GetBytes(password)));
        IdOptions = idOptions ?? new();

        ID = GenerateID();
        Securitytype = Password is null || string.IsNullOrEmpty(Password) ? "none" : "password";
        Creationdate = (int)(DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalSeconds;
        Clicks = 0;
        Deletedate = 0;
        Securitytotp = GenerateTotp();
        Editinfo = new object();
        Qruuid1 = GenerateUuid1();
        Qruuid2 = GenerateUuid2();
    }

    public string GenerateUuid1()
    {
        string newUuid1 = Guid.NewGuid().ToString();

        Qruuid1 = newUuid1;
        return newUuid1;
    }

    public string GenerateUuid2()
    {
        string newUuid2 = Guid.NewGuid().ToString();

        Qruuid2 = newUuid2;
        return newUuid2;
    }

    public string GenerateTotp()
    {
        byte[] key = KeyGeneration.GenerateRandomKey(20);
        string base32String = Base32Encoding.ToString(key);

        Securitytotp = base32String;
        return base32String;
    }

    public string GenerateID()
    {
        if (IdOptions.StaticID is not null)
        {
            return IdOptions.StaticID;
        }

        return UrlIDGenerator.Generate(IdOptions.IDType ?? "lowercase", IdOptions.Length == 0 ? 8 : IdOptions.Length);
    }

    public bool CheckUnique(UrlUniqueValues value, UrlService service)
    {
        switch (value)
        {
            case UrlUniqueValues.ID:
                while (service.Get().Any(u => u.ID == ID))
                {
                    string oldID = ID;
                    ID = GenerateID();
                    if (ID == oldID) return false;
                }
                break;
            case UrlUniqueValues.qruuid1:
                while (service.Get().Any(u => u.Qruuid1 == Qruuid1))
                {
                    Qruuid1 = GenerateUuid1();
                }
                break;
            case UrlUniqueValues.qruuid2:
                while (service.Get().Any(u => u.Qruuid2 == Qruuid2))
                {
                    Qruuid2 = GenerateUuid2();
                }
                break;
            case UrlUniqueValues.securitytotp:
                while (service.Get().Any(u => u.Securitytotp == Securitytotp))
                {
                    Securitytotp = GenerateTotp();
                }
                break;
            default:
                while (service.Get().Any(u => u.ID == ID))
                {
                    ID = GenerateID();
                }
                break;
        }

        return true;
    }

    public override string ToString()
    {
        return JsonConvert.SerializeObject(this);
    }

    public object ToObject()
    {
        return new { ID, owner = Owner, redirect = Redirect, nsfw = Nsfw, captcha = Captcha, unembedify = Unembedify, clicks = Clicks, securitytype = Securitytype, creationdate = Creationdate };
    }
}

public class UrlOptions
{
    public string? StaticID { get; set; }
    public string? IDType { get; set; }
    public int Length { get; set; }

    public UrlOptions()
    {
        StaticID = null;
        IDType = "lowercase";
        Length = 8;
    }

    public UrlOptions(string ID)
    {
        StaticID = ID;
        IDType = null;
        Length = 0;
    }

    public UrlOptions(string genIDType, int length = 8)
    {
        StaticID = null;


        if (genIDType is null || !(genIDType.Contains("lowercase") || genIDType.Contains("uppercase") || genIDType.Contains("numbers")))
        {
            genIDType = "lowercase";
        }
        else
        {
            IDType = genIDType;
        }

        Length = length;
    }

    public override string ToString()
    {
        return JsonConvert.SerializeObject(this);
    }
}

public class UrlRequest
{
    public string Redirect { get; set; }
    public string? Password { get; set; }
    public bool Nsfw { get; set; }
    public bool Captcha { get; set; }
    public bool Unembedify { get; set; }
    public string? Type { get; set; }
    public int Length { get; set; }
    public string? Id { get; set; }
    public UrlOptions? Options { get; set; }

    public UrlRequest(string redirect, bool nsfw = false, string password = "", bool captcha = false, bool unembedify = false, string type = "lowercase", int length = 8, string? id = null)
    {
        Redirect = redirect;
        Nsfw = nsfw;
        Password = password;
        Captcha = captcha;
        Unembedify = unembedify;

        Type = type;
        Length = length == 0 ? 8 : length < 128 ? length : 128;
        Id = id;
        Options = Id is null ? new(Type, Length) : new(Id);
    }

    public override string ToString()
    {
        return JsonConvert.SerializeObject(this);
    }

    public async Task<Url?> ToUrl(User owner, UrlService urlService)
    {
        Url url = new(owner, Redirect, Nsfw, Options, Password is null ? "" : Password, Captcha, Unembedify);

        bool IDUnique = await Task.Run(() => url.CheckUnique(UrlUniqueValues.ID, urlService));
        await Task.Run(() => url.CheckUnique(UrlUniqueValues.qruuid1, urlService));
        await Task.Run(() => url.CheckUnique(UrlUniqueValues.qruuid2, urlService));
        await Task.Run(() => url.CheckUnique(UrlUniqueValues.securitytotp, urlService));

        if (!IDUnique) return null;

        return url;
    }
}

public class UrlEditRequest
{
    public string? Redirect { get; set; }
    public string? Password { get; set; }
    public bool? Nsfw { get; set; }
    public bool? Captcha { get; set; }
    public bool? Unembedify { get; set; }
    public int DeleteDate { get; set; } // wip
    public UrlEditRequest? EditInfo { get; set; } // wip

    public UrlEditRequest(
        string? redirect = null,
        string? password = null,
        bool? nsfw = null,
        bool? captcha = null,
        bool? unembedify = null,
        int deletedate = 0,
        UrlEditRequest? editinfo = null
    )
    {
        Redirect = redirect;
        Password = password;
        Nsfw = nsfw;
        Captcha = captcha;
        Unembedify = unembedify;
        DeleteDate = deletedate;
        EditInfo = editinfo;
    }

    public override string ToString()
    {
        return JsonConvert.SerializeObject(this);
    }

    public Url ToUrl(Url url)
    {
        url.Redirect = Redirect is null ? url.Redirect : Redirect;
        url.Password = Password is null ? url.Password : Convert.ToHexString(SHA512.Create().ComputeHash(Encoding.UTF8.GetBytes(Password)));
        url.Securitytype = Password is null ? url.Securitytype : Password is null || string.IsNullOrEmpty(Password) ? "none" : "password";
        url.Nsfw = (bool)(Nsfw is null ? url.Nsfw : Nsfw);
        url.Captcha = (bool)(Captcha is null ? url.Captcha : Captcha);
        url.Unembedify = (bool)(Unembedify is null ? url.Unembedify : Unembedify);
        url.Deletedate = DeleteDate == 0 ? url.Deletedate : DeleteDate;
        url.Editinfo = EditInfo is null ? url.Editinfo : EditInfo;

        return url;
    }
}
