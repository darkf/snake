def fizzy():
	s = ""

	for num in range(1, 101):
		if num % 3 == 0 and num % 5 == 0:
			s += "FizzBuzz "
		elif num % 3 == 0:
			s += "Fizz "
		elif num % 5 == 0:
			s += "Buzz "
		else:
			s += str(num)
			s += " "

	return s

print(fizzy())