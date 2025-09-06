"""
Cálculo de entropía de Shannon para Joe Cipher:
- Entropía sobre el texto Base-85 (tope teórico ≈ log2(85) ≈ 6.41 bits/símbolo)

Nota: Para evitar sesgos por muestras pequeñas, se recomienda usar un corpus >= ~100 KB.
Puedes aumentar REPEAT para replicar el texto de prueba y obtener una estimación más estable.
"""

from base64 import b85decode
from collections import Counter
import math

import Joe
import utils

p = 99999999991
g = 3
x = 30

ORIGINAL_TEXT = "test message"
REPEAT = 10000

def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    total = len(data)
    counts = Counter(data)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())

def log2_base85() -> float:
    return math.log2(85)

myJoeCypher = Joe.JoeCypher(p=p, g=g, x=x)

plain = (ORIGINAL_TEXT * REPEAT) if REPEAT > 1 else ORIGINAL_TEXT

encrypted_list = [myJoeCypher.cypher(ord(ch)) for ch in plain]

encoded_string = utils.Utils.encode_encrypted_floats(encrypted_list)

ciphertext_b85_bytes = encoded_string.encode("ascii")
H_b85 = shannon_entropy(ciphertext_b85_bytes)

decoded_bytes = b85decode(ciphertext_b85_bytes)

print(f"Longitud del texto Base-85: {len(ciphertext_b85_bytes)} bytes")
print(f"Longitud de los bytes decodificados: {len(decoded_bytes)} bytes\n")

print(f"Entropía (texto Base-85): {H_b85:.4f} bits/símbolo   (máx teórico ≈ log2(85) = {log2_base85():.2f})")
