using AspNetCoreRateLimit;
using Fasmga;
using Fasmga.Schema;
using Fasmga.Services;
using Microsoft.Extensions.Options;

string cwd = Directory.GetCurrentDirectory();
string dotenvFile = Path.Combine(cwd, ".env");

DotEnv.Load(dotenvFile);

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers().AddNewtonsoftJson(options => options.UseMemberCasing()); ;

builder.Services.AddMvc(options => options.EnableEndpointRouting = false);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddCors(options => 
{
  options.AddDefaultPolicy(builder => builder.AllowAnyMethod().AllowAnyHeader().AllowCredentials().SetIsOriginAllowed((hosts) => true));
});

builder.Services.AddOptions();

builder.Services.Configure<FasmgaDatabaseSettings>(builder.Configuration.GetSection(nameof(FasmgaDatabaseSettings)));
builder.Services.AddSingleton<IFasmgaDatabaseSettings>(sp => sp.GetRequiredService<IOptions<FasmgaDatabaseSettings>>().Value);

builder.Services.AddSingleton<UrlService>();
builder.Services.AddSingleton<UserService>();
builder.Services.AddSingleton<Authorization>();

builder.Services.AddMemoryCache();
builder.Services.Configure<IpRateLimitOptions>(builder.Configuration.GetSection("IpRateLimiting"));
builder.Services.Configure<IpRateLimitPolicies>(builder.Configuration.GetSection("IpRateLimitPolicies"));

builder.Services.AddInMemoryRateLimiting();
builder.Services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();


WebApplication app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseIpRateLimiting();

app.UseMvc();

app.UseCors();

app.MapControllers();

app.Run();
