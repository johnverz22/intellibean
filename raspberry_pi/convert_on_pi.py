#!/usr/bin/env python3
"""
Convert best_model.keras -> best_model_v3.tflite using ai_edge_litert on Pi.
ai_edge_litert bundles its own TFLite converter that works without full TF.
"""
import numpy as np

# ai_edge_litert ships with a converter module
try:
    import ai_edge_litert.converter as converter_module
    print("Using ai_edge_litert converter")
    HAS_CONVERTER = True
except ImportError:
    HAS_CONVERTER = False
    print("No converter in ai_edge_litert, trying tensorflow-lite-support...")

if not HAS_CONVERTER:
    # Try tflite_model_maker or tensorflow
    try:
        import tensorflow as tf
        HAS_TF = True
    except ImportError:
        HAS_TF = False

    if not HAS_TF:
        print("ERROR: No TF or converter available.")
        print("Install with: pip install tensorflow-cpu")
        exit(1)

# ── If we have full TF ────────────────────────────────────────────────────────
if not HAS_CONVERTER:
    print(f"TF {tf.__version__}")
    model = tf.keras.models.load_model('best_model.keras')
    print("Last layer:", model.layers[-1].name, model.layers[-1].output_shape)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_bytes = converter.convert()
    out = 'best_model_v3.tflite'
    with open(out, 'wb') as f:
        f.write(tflite_bytes)
    print(f"Saved {out} ({len(tflite_bytes)//1024} KB)")

    from ai_edge_litert.interpreter import Interpreter
    interp = Interpreter(model_path=out)
    interp.allocate_tensors()
    inp_d = interp.get_input_details()
    out_d = interp.get_output_details()
    for tag, data in [("zeros", np.zeros(inp_d[0]['shape'], np.float32)),
                      ("rand ", np.random.uniform(-1,1,inp_d[0]['shape']).astype(np.float32))]:
        interp.set_tensor(inp_d[0]['index'], data)
        interp.invoke()
        p = interp.get_tensor(out_d[0]['index'])[0]
        print(f"{tag} -> bad={p[0]:.4f} good={p[1]:.4f} => {'GOOD' if np.argmax(p)==1 else 'BAD'}")
    print("Sanity check done.")
