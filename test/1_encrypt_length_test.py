import Joe
import utils
import time
import random
import string
import numpy as np
import Crypto.Util.number as getPrime

p = getPrime.getPrime(32)
g = 3
x = 2

data = []

print("Length\tAverage time (ms)")
for length in range(1, 101):
    times = []
    for _ in range(20):
        myJoeCypher = Joe.JoeCypher(p=p, g=g, x=x)
        original_text = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        start = time.time()
        encrypted_list = [myJoeCypher.cypher(ord(char)) for char in original_text]
        encoded_string = utils.Utils.encode_encrypted_floats(encrypted_list)
        end = time.time()
        times.append((end - start) * 1000)
    avg_time = sum(times) / len(times)
    data.append([length, avg_time])
    print(f"{length}\t\t{avg_time:.4f}")

data_np = np.array(data)
lengths = data_np[:, 0]
times = data_np[:, 1]

# 2nd degree polynomial fit
coeffs = np.polyfit(lengths, times, 2)
print(f"\nApproximated function: time(ms) = {coeffs[0]:.8f} * length^2 + {coeffs[1]:.8f} * length + {coeffs[2]:.8f}")

import matplotlib.pyplot as plt
plt.plot(lengths, times, label='Mean time (ms)')
plt.plot(lengths, np.polyval(coeffs, lengths), '--', label='Quadratic fit')
plt.xlabel('Text Length (characters)')
plt.ylabel('Time (ms)')
plt.title('Joe Cipher Encryption Time vs Text Length')
plt.legend()
plt.grid(True)
plt.show()
