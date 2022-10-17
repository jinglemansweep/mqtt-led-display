def flatten(l):
    return [item for sublist in l for item in sublist]


# r1, g1, b1, w = dark red, dark green, dark blue, dark white/grey
# r2, g2, b2 = medium
# r3, g3, b3 = bright

_u0 = 0x00
_u1 = 0x22
_u2 = 0x66
_u3 = 0xAA

__ = (_u0, _u0, _u0)

r1 = (_u1, _u0, _u0)
g1 = (_u0, _u1, _u0)
b1 = (_u0, _u0, _u1)
y1 = (_u1, _u1, _u0)
w1 = (_u1, _u1, _u1)

r2 = (_u2, _u0, _u0)
g2 = (_u0, _u2, _u0)
b2 = (_u0, _u0, _u2)
y2 = (_u2, _u2, _u0)
w2 = (_u2, _u2, _u2)

r3 = (_u3, _u0, _u0)
g3 = (_u0, _u3, _u0)
b3 = (_u0, _u0, _u3)
y3 = (_u3, _u3, _u0)
w3 = (_u3, _u3, _u3)

_snake = []
_snake += [__, __, __, g1, g1, g1, __, __]
_snake += [__, __, g1, w1, g1, w1, g1, __]
_snake += [__, __, __, g1, g1, g1, __, __]
_snake += [__, r1, r1, __, __, g1, __, __]
_snake += [__, __, __, __, g1, __, __, __]
_snake += [g1, g1, __, __, g1, g1, __, __]
_snake += [__, __, g1, g1, g1, __, g1, __]
_snake += [__, __, __, __, g1, g1, g1, __]

SNAKE = flatten(_snake)

_pokemon = []
_pokemon += [g1, __, __, g1, g1, g1, g1, __]
_pokemon += [g1, g1, y2, y1, g1, g1, g1, y1]
_pokemon += [g1, g1, g1, y2, y2, y2, y2, y1]
_pokemon += [y1, y1, g1, y2, __, y2, y2, __]
_pokemon += [y1, y1, g1, r1, y2, y2, y2, y1]
_pokemon += [g1, r1, g1, y2, y1, y1, y1, g1]
_pokemon += [g1, r1, y2, y1, y2, y1, y2, g1]
_pokemon += [g1, g1, y2, y1, r1, r1, y1, g1]

POKEMON = flatten(_pokemon)

# print(SNAKE)
