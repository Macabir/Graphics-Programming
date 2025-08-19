// The 'using' directive imports a namespace, giving us access to its classes.
using System;

public class Program
{

    public static void Main(string[] args)
    {
        // Display a message to the user.
        Console.WriteLine("This is a simple addition program.");
        Console.WriteLine("Please enter the first number:");

        // Read the user's input from the console and store it in a string variable.
        string firstNumberAsString = Console.ReadLine() ?? string.Empty;

        bool isFirstNumberValueValid = int.TryParse(firstNumberAsString, out int firstNumber);

        if (!isFirstNumberValueValid)
        {
            Console.WriteLine("Invalid input. Please enter a valid number.");
            return;
        }

        // Convert the string input to a number (integer).
        // This is necessary because Console.ReadLine() always returns a string.33

        // Repeat the process for the second number.
        
        Console.WriteLine("Please enter the second number:");

        string secondNumberAsString = Console.ReadLine() ?? string.Empty;

        bool isSecondNumberValueValid = int.TryParse(secondNumberAsString, out int secondNumber);

        if (!isFirstNumberValueValid)
        {
            Console.WriteLine("Invalid input. Please enter a valid number.");
            return;
        }

        // Perform the addition.
        int sum = firstNumber + secondNumber;

        // Display the result to the user using string interpolation.
        Console.WriteLine($"The sum is: {sum}");
    }
}