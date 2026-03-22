#!/usr/bin/env python3
"""Diagnose the saved keras model weights directly."""
import os, numpy as np
from tensorflow import keras

BASE  = os.path.expanduser('~/bean_sorter')
KERAS = os.path.join(BASE, 'best_model_new.keras')

print(f"Loading {KERAS}...")
model = keras.models.load_model(KERAS)
print("Loaded OK")

for tag, x in [
    ('zeros', np.zeros((1,224,224,3), dtype='float32')),
    ('ones ', np.ones((1,224,224,3), dtype='float32')),
    ('rand1', np.random.uniform(-1,1,(1,224,224,3)).astype('float32')),
    ('rand2', np.random.uniform(-1,1,(1,224,224,3)).astype('float32')),
]:
    p = model.predict(x, verbose=0)[0]
    label = 'GOOD' if p[1] > p[0] else 'BAD'
    print(f"  {tag}: bad={p[0]:.4f}  good={p[1]:.4f}  => {label}")
