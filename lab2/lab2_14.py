n = int(input("enter a number: "))
choice=int(input("1.Binary 2.Octal 3.Hex: "))
match choice:
    case 1: print(bin(n)[2:])
    case 2: print(oct(n)[2:])
    case 3: print(hex(n)[2:].upper())
    case _: print("invalid")