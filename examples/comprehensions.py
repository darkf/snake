# list comprehensions
print([x*2 for x in range(10)])
print([x for x in range(20) if x%2 != 0])

# dict comprehensions
print({k: v for k,v in [(1, 2), (3, 4)]})
