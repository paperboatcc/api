namespace Fasmga.Helpers; 

public static class UrlIDGenerator {

	private static Random _random = new();
	private static string lowercaseAlphabet = "abcdefghijklmnopqrstuvwxyz";
	private static string uppercaseAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
	private static string numbers = "0123456789";

	public static string Generate(string type = "lowercase", int length = 8)
	{
		string alphabet = "";

		foreach (string t in type.Split('-')) ToAlphabet(t, ref alphabet);

    return new string(Enumerable.Repeat(alphabet, length).Select(s => s[_random.Next(s.Length)]).ToArray());
	}

	private static string ToAlphabet(string type, ref string chars) => type switch
	{
		"lowercase" => chars += lowercaseAlphabet,
		"uppercase" => chars += uppercaseAlphabet,
		"numbers" => chars += numbers,
		_ => chars += lowercaseAlphabet
	};
}
