"""Blueqat backend for classical bit simulation

    This module provides Blueqat backend for X, CX, CCX gates and measurement.
    "classical" backend is faster and less memory than general quantum computer simulator.
    However, available gates are not enough to make quantum algorithm.
"""

from dataclasses import dataclass
from typing import List
from collections import Counter
import numpy as np
from blueqat import BlueqatGlobalSetting
from blueqat.backends.backendbase import Backend

@dataclass
class _ClassicalBitBackendContext:
    shots: int
    bits: List[bool]
    measured: List[bool]

class ClassicalBitBackend(Backend):
    """Backend for classical bit simulation.

    This backend supports only X, CX, CCX gates and measurement.
    """
    def _preprocess_run(self, gates, n_qubits, args, kwargs):
        shots = kwargs.get('shots', 100)
        return gates, _ClassicalBitBackendContext(shots, [False] * n_qubits, [False] * n_qubits)

    def _postprocess_run(self, ctx):
        return Counter({
            ''.join('1' if b else '0' for b in ctx.bits): ctx.shots
        })

    def gate_x(self, gate, ctx):
        bits = ctx.bits
        for idx in gate.target_iter(len(bits)):
            bits[idx] = not bits[idx]
        return ctx

    def gate_cx(self, gate, ctx):
        bits = ctx.bits
        for (c, t) in gate.control_target_iter(len(bits)):
            if bits[c]:
                bits[t] = not bits[t]
        return ctx

    def gate_ccx(self, gate, ctx):
        bits = ctx.bits
        c0, c1, t = gate.targets
        if bits[c0] and bits[c1]:
            bits[t] = not bits[t]
        return ctx

    def gate_measure(self, gate, ctx):
        bits = ctx.bits
        meas = ctx.measured
        for idx in gate.target_iter(len(bits)):
            meas[idx] = bits[idx]
        return ctx


BlueqatGlobalSetting.register_backend('classical', ClassicalBitBackend)

if __name__ == '__main__':
    import random
    from blueqat import Circuit
    c = Circuit().x[0].cx[0, 10].x[11].ccx[0, 6, 5].ccx[0, 11, 9].x[0].m[:]
    assert c.run(shots=50) == c.run_with_classical(shots=50)


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
    c = Circuit().set(a, 0).set(b, 128).adder(0, 128, 255, 256, 128)
    result = int(c.m[:].run_with_classical().most_common()[0][0][128:][::-1], base=2)
    assert a + b == result
    print(f'{a} + {b} = {result}')
