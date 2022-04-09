using AspNetCoreRateLimit;
using Fasmga.Models;
using Fasmga.Helpers;
using Fasmga.Services;
using Microsoft.Extensions.Options;

namespace Fasmga;

public class Startup
{
    public IConfigurationRoot Configuration { get; }

    public Startup(IConfigurationRoot configuration)
    {
        var cwd = Directory.GetCurrentDirectory();
        var dotenvFile = Path.Combine(cwd, ".env");

        DotEnv.Load(dotenvFile);

        Configuration = configuration;
    }


    public IServiceCollection ConfigureServices(IServiceCollection services)
    {
        services.AddControllers().AddNewtonsoftJson(options => options.UseMemberCasing()); ;

        services.AddMvc(options => options.EnableEndpointRouting = false);

        services.AddEndpointsApiExplorer();
        services.AddSwaggerGen();

        services.AddCors(options =>
        {
            options.AddDefaultPolicy(builder => builder.AllowAnyMethod().AllowAnyHeader().AllowCredentials().SetIsOriginAllowed((hosts) => true));
        });

        services.AddOptions();

        services.Configure<FasmgaDatabaseSettings>(Configuration.GetSection(nameof(FasmgaDatabaseSettings)));
        services.AddSingleton<IFasmgaDatabaseSettings>(sp => sp.GetRequiredService<IOptions<FasmgaDatabaseSettings>>().Value);

        services.AddSingleton<UrlService>();
        services.AddSingleton<UserService>();

        services.AddAuthentication(options =>
        {
            options.AddScheme<Auth>("Authentication", "Authentication");

            options.DefaultScheme = "Authentication";
        });

        services.AddMemoryCache();
        services.Configure<IpRateLimitOptions>(Configuration.GetSection("IpRateLimiting"));
        services.Configure<IpRateLimitPolicies>(Configuration.GetSection("IpRateLimitPolicies"));

        services.AddInMemoryRateLimiting();
        services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();

        return services;
    }

    public WebApplication Configure(WebApplication app)
    {
        if (app.Environment.IsDevelopment())
        {
            app.UseDeveloperExceptionPage();
            app.UseSwagger();
            app.UseSwaggerUI();
        }

        app.UseIpRateLimiting();

        app.UseMvc();

        app.UseCors();
        app.UseAuthentication();

        app.MapControllers();

        return app;
    }
}
