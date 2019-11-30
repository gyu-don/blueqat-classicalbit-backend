import random
from blueqat import Circuit, BlueqatGlobalSetting
import blueqat_classicalbit_backend

def set_(c, val, pos):
    def g(val):
        i = 0
        while val:
            if val & 1:
                yield pos + i
            i += 1
            val >>= 1
    return c.x[tuple(g(val))]

BlueqatGlobalSetting.register_macro('set', set_)


def sum_(c, ci, ai, bi):
    return c.cx[ai, bi].cx[ci, bi]


def carry(c, ci, ai, bi, cj):
    return c.ccx[ai, bi, cj].cx[ai, bi].ccx[ci, bi, cj]


def uncarry(c, ci, ai, bi, cj):
    return c.ccx[ci, bi, cj].cx[ai, bi].ccx[ai, bi, cj]


BlueqatGlobalSetting.register_macro('sum', sum_)
BlueqatGlobalSetting.register_macro('carry', carry)
BlueqatGlobalSetting.register_macro('uncarry', uncarry)


def adder(c, a0, b0, c0, sign, n_bits):
    for i in range(n_bits - 1):
        c.carry(c0 + i, a0 + i, b0 + i, c0 + i + 1)
    c.carry(c0 + n_bits - 1, a0 + n_bits - 1, b0 + n_bits - 1, sign)
    c.cx[a0 + n_bits - 1, b0 + n_bits - 1].sum(c0 + n_bits - 1, a0 + n_bits - 1, b0 + n_bits - 1)
    for i in reversed(range(n_bits - 1)):
        c.uncarry(c0 + i, a0 + i, b0 + i, c0 + i + 1).sum(c0 + i, a0 + i, b0 + i)
    return c


BlueqatGlobalSetting.register_macro('adder', adder)

a = random.randrange(0, 1 << 127)
b = random.randrange(0, 1 << 127)
c = Circuit().set(a, 0).set(b, 128).adder(0, 128, 256, 257, 128)
result = int(c.m[:].run_with_classical().most_common()[0][0][128:][::-1], base=2)
assert a + b == result
print(f'{a} + {b} = {result}')
