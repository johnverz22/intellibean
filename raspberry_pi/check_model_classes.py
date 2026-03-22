#!/usr/bin/env python3
import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model('best_model.keras')
model.summary()

# Check what the model actually learned
# Test with pure colors
tests = {
    'all zeros (grey)': np.zeros((1,224,224,3), np.float32),
    'all white (+1.0)': np.ones((1,224,224,3), np.float32),
    'all black (-1.0)': np.full((1,224,224,3), -1.0, np.float32),
    'random noise':     np.random.uniform(-1,1,(1,224,224,3)).astype(np.float32),
    'random noise 2':   np.random.uniform(-1,1,(1,224,224,3)).astype(np.float32),
}
print("\nModel direct predictions (before TFLite):")
for name, arr in tests.items():
    p = model.predict(arr, verbose=0)[0]
    print(f"  {name}: bad={p[0]:.4f} good={p[1]:.4f} => {'GOOD' if np.argmax(p)==1 else 'BAD'}")

# Check final layer
print("\nFinal layer weights shape:", model.layers[-1].get_weights()[0].shape)
print("Final layer bias:", model.layers[-1].get_weights()[1])
