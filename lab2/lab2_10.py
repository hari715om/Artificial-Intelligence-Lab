n = int(input("Enter 3-digit number: "))
rev = (n%10)*100 + ((n//10)%10)*10 + (n//100)
print("Palindrome" if n==rev else "Not Palindrome")
