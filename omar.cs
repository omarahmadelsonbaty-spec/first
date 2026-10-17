using System;
class Program
{
    static void Main()
    {
		Console.WriteLine("Press W to say Hello, S to say Goodbye, Press B to exit, A or D for other messages. Press any other key for invalid input.");
        while (true)
        {
			ConsoleKey input = Console.ReadKey(true).Key;

            if (input == ConsoleKey.W)
            {
                Console.WriteLine("Hello, World!");
            }
            else if (input == ConsoleKey.S)
            {
                Console.WriteLine("Goodbye, World!");
            }
            else if (input == ConsoleKey.A)
            {
                Console.WriteLine("You pressed A.");
            }
            else if (input == ConsoleKey.D)
            {
                Console.WriteLine("You pressed D.");
            }
            else if (input == ConsoleKey.B)
			{
				Console.WriteLine("Exiting the program.");
				break;
			}
			else
            {
                Console.WriteLine("Invalid input.");
            }
        }
    }
}
