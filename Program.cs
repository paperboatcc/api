using Fasmga;
using Fasmga.Schema;
using Fasmga.Services;
using Microsoft.Extensions.Options;

string cwd = Directory.GetCurrentDirectory();
string dotenvFile = Path.Combine(cwd, ".env");

DotEnv.Load(dotenvFile);

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.Configure<FasmgaDatabaseSettings>(builder.Configuration.GetSection(nameof(FasmgaDatabaseSettings)));
builder.Services.AddSingleton<IFasmgaDatabaseSettings>(sp => sp.GetRequiredService<IOptions<FasmgaDatabaseSettings>>().Value);

builder.Services.AddSingleton<UrlService>();
builder.Services.AddSingleton<UserService>();

WebApplication app = builder.Build();

if (app.Environment.IsDevelopment())
{
	app.UseDeveloperExceptionPage();
	app.UseSwagger();
	app.UseSwaggerUI();
}
else {
	app.UseHsts();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
