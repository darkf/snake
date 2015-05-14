def even(x):
	return not odd(x)

def odd(x):
	return x % 2 != 0

print("10 is even?", even(10))
print("11 is even?", even(11))
print("first 10 even?", list(map(even, range(10))))