#include <iostream>
#include <cstdlib>
#include <ctime>

int main() {
    // Seed the random number generator
    srand(time(0));

    const int SIZE = 10;
    int numbers[SIZE];
    int sum = 0;

    // Fill the array with random numbers and calculate the sum
    std::cout << "The random array elements are: " << std::endl;
    for (int i = 0; i < SIZE; ++i) {
        numbers[i] = rand() % 100 + 1; // Generates numbers between 1 and 100
        std::cout << numbers[i] << " ";
        sum += numbers[i];
    }
    std::cout << std::endl;


    std::cout << "The sum of the array elements is: " << sum << std::endl;
    
    return 0;
}