def root_finder():
    print("Hello, and welcome to Root Finder, which finds the roots of a polynomial structured as ax^2 + bx + c, where a, b, and c are the constants of the expression.")
    a = float(input("a = "))
    b = float(input("b = "))
    c = float(input("c = "))
    if a == 0:
        
        if b != 0:
            
            answer1 = (-c/b)
            print("This linear function has one real root:")
            print(answer1)
            
        elif b == 0:
            
            print("This function is a constant. Roots are indeterminable.")
            
    elif 4*a*c > b**2:
        
        print("This quadratic has no real roots.")
        
    elif 4*a*c == b**2 and a != 0:
        
        answer1 = (-b + (b**2 - 4*a*c)**(1/2))/(2*a)
        print("This quadratic has one real root:")
        print(str(answer1))
        
    elif 4*a*c < b**2 and a != 0:
        
        root1 = (-b + (b**2 - 4*a*c)**(1/2))/(2*a)
        root2 = (-b - (b**2 - 4*a*c)**(1/2))/(2*a)
        
        answer1 = str(root1)
        answer2 = str(root2)
        
        print("This quadratic has two real roots: ")
        print(answer1)
        print(answer2)

root_finder()
escape = input("To exit the program, enter 'e'.")
while escape != "e":
    root_finder()
    escape = input("To exit the program, enter 'e'.")
    print(escape)