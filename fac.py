
"""
def fact(n):
	if n == 1 or n == 0:
		return 0
	return n * fact(n - 1)
"""

def fact(n):
	prod = 1
	
	while n > 1:
		prod *= n
		n -= 1

	return prod

print("10! is", fact(10))