def rfact(n):
	if n == 1 or n == 0:
		return 1
	return n * rfact(n - 1)

def fact(n):
	prod = 1
	
	while n > 1:
		prod *= n
		n -= 1

	return prod

print("10! is", fact(10))
print("10! recursively is", rfact(10))