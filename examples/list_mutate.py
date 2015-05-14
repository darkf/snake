xs = [1, 2, 3, 4, 5]
xs.append(6)

print(xs)
assert xs == [1, 2, 3, 4, 5, 6]

xs[0] = 10

print(xs)
assert xs == [10, 2, 3, 4, 5, 6]

xs[1:3] = [100, 200]

print(xs)
assert xs == [10, 100, 200, 4, 5, 6]