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
