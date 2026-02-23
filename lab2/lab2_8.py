a, b, c = map(int, input("Enter a b c: ").split())
print(1 if (a+b>c and b+c>a and c+a>b) else 0)
