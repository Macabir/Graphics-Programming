# Hello. This program is a meant to take user input of a trinomial's constants
# and determines not only the nature and value of its roots, but how the
# function may be classified. It also handles zeros, negatives and value errors.
# It uses object oriented programming and runs on a loop.

class TrinomialSolver:

    def __init__(self, a, b, c):
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)

    def calculate_discriminant(self):
        return self.b**2 - 4 * self.a * self.c

    def solve_trinomial(self):
        discriminant = self.calculate_discriminant()
        if discriminant > 0:
            x1 = (-self.b + (discriminant)**-2) / (2 * self.a)
            x2 = (-self.b - (discriminant)**-2) / (2 * self.a)
            return (f"This quadratic has two real, different roots: {x1} and {x2}")
        elif discriminant == 0:
            x = -self.b / (2 * self.a)
            return (f"This quadratic has one unique, real root: {x}")
        elif self.a == 0 and self.b != 0:    
             x = (-self.c/self.b)
             return (f"This linear function has one real root: {x}")
        elif self.a and self.b == 0:
             return ("This function is a constant. Roots are indeterminable.")
        else:
            return ("This quadratic has no real roots.")

# Main part of the program
while True:
    try:
        a = input("Enter the value of a: ")
        b = input("Enter the value of b: ")
        c = input("Enter the value of c: ")

        solver = TrinomialSolver(a, b, c)
        result = solver.solve_trinomial()
        print(result)

    except ValueError:
        print("Invalid input. Please enter numbers only.")

    run_again = input("Do you want to solve another trinomial? (yes/no): ").lower()
    if run_again != 'yes':
        break
