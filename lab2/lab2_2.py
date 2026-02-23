num = int(input("Enter 3-digit number: "))
rev = (num%10)*100 + ((num//10)%10)*10 + (num//100)
print("Reverse =", rev)
