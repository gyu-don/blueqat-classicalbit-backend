# blueqat-classicalbit-backend
Blueqat backend for classical bit (Only X gate, CX gate, CCX gate and measurement are available)

## Usage

```py
from blueqat import Circuit
import blueqat_classicalbit_backend

print(Circuit().x[0].cx[0, 1].ccx[0, 1, 2].m[:].run_with_classical())
```
