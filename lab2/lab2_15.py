import random
num = random.randint(1, 50)

while True:
    guess = int(input("Guess number: "))
    if guess==num:
        print("correct number")
        break
    if guess <num:
        print("Too low")
    else:
        print("too high")