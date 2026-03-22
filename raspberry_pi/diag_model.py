#!/usr/bin/env python3
"""Quick model diagnostic — run on Pi to check predictions."""
import numpy as np
try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    from tflite_runtime.interpreter import Interpreter

interp = Interpreter(model_path='best_model_v2.tflite')
interp.allocate_tensors()
inp = interp.get_input_details()
out = interp.get_output_details()
print('Input shape:', inp[0]['shape'], 'dtype:', inp[0]['dtype'])
print('Output shape:', out[0]['shape'])

for name, val in [('zeros', 0.0), ('mid-grey (0.0 scaled)', 0.0), ('white (1.0 scaled)', 1.0), ('black (-1.0 scaled)', -1.0)]:
    arr = np.full(inp[0]['shape'], val, dtype=np.float32)
    interp.set_tensor(inp[0]['index'], arr)
    interp.invoke()
    preds = interp.get_tensor(out[0]['index'])[0]
    print(f'{name}: raw={preds}  -> class={np.argmax(preds)} (0=bad,1=good)  conf={np.max(preds)*100:.1f}%')
