
from itertools import product


def obj1(data, x):
    return sum([x[i, k] for i, k in product(range(data['n']), range(data['r']))])


def obj2(data, y):
    d = { abs(sum(data['h'][l] * (y[i, l] - y[j, l]) for l in range(data['p']))) for i in range(data['n']) for j in data['conflicts'][i]}
    return sum(min(d[i, j] for j in data['conflicts'][i]) for i in range(data['n']))
