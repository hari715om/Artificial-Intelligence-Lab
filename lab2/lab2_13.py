num = int(input("Enter number: "))
i = 2
factors = []
while i*i <= num:
    if num % i == 0:
        factors.append(i)
        while num % i == 0:
            num //= i
    i += 1
if num > 1:
    factors.append(num)
print("Distinct prime factors:", factors)
