def f(x):
	print("f:", x)
	x = 10

def g(x):
	print("g1:", x)
	f(20)
	print("g2:", x)

x = 30
print("global1:", x)

g(5)
print("global2:", x)
