#!/usr/bin/env python3
import os, sys, time
from base64 import b85encode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

def run_and_measure(name, fn, pt_bytes):
    t0 = time.perf_counter()
    out = fn(pt_bytes)
    t1 = time.perf_counter()
    out["name"] = name
    out["time_ms"] = (t1 - t0) * 1000.0
    out["pt_len"] = len(pt_bytes)
    out["expansion"] = out["tx_bytes"] / max(1, len(pt_bytes))
    return out

def fmt_bytes(n):
    for u in ("B","KB","MB","GB"):
        if n < 1024 or u == "GB":
            return f"{n:.0f} {u}"
        n /= 1024

def line(r):
    base85 = f" | Base85={fmt_bytes(r['base85_bytes'])}" if r.get("base85_bytes") is not None else ""
    return (f"{r['name']}: tiempo={r['time_ms']:.3f} ms | "
            f"PT={r['pt_len']} B -> TX={fmt_bytes(r['tx_bytes'])} "
            f"(x{r['expansion']:.2f}){base85}")

def aes_gcm_encrypt(pt_bytes):
    key = os.urandom(16)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, pt_bytes, None)
    tx = len(nonce) + len(ct)
    return {
        "tx_bytes": tx,
        "base85_bytes": len(b85encode(nonce + ct)),
    }

def chacha_encrypt(pt_bytes):
    key = os.urandom(32)
    ch = ChaCha20Poly1305(key)
    nonce = os.urandom(12)
    ct = ch.encrypt(nonce, pt_bytes, None)
    tx = len(nonce) + len(ct)
    return {
        "tx_bytes": tx,
        "base85_bytes": len(b85encode(nonce + ct)),
    }

def joe_encrypt_factory(p=99999999991, g=3, x=30):
    try:
        import Joe
        import utils
    except Exception as e:
        def _missing(_pt_bytes):
            raise RuntimeError("") from e
        return _missing

    def _joe_encrypt(pt_bytes):
        pt_str = pt_bytes.decode("utf-8")
        myJoe = Joe.JoeCypher(p=p, g=g, x=x)
        enc_list = [myJoe.cypher(ord(ch)) for ch in pt_str]
        encoded_string = utils.Utils.encode_encrypted_floats(enc_list)
        tx = len(encoded_string.encode("ascii", errors="strict"))
        return {
            "tx_bytes": tx,
            "base85_bytes": None,
        }
    return _joe_encrypt

def main():
    phrase = "This is a test for symmetric algorithms" if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    pt = phrase.encode("utf-8")

    joe_fn = joe_encrypt_factory(p=99999999991, g=3, x=30)

    results = []
    results.append(run_and_measure("AES-GCM", aes_gcm_encrypt, pt))
    results.append(run_and_measure("ChaCha20-Poly1305", chacha_encrypt, pt))
    try:
        results.append(run_and_measure("JoeCipher", joe_fn, pt))
    except Exception as e:
        print(f"Somehting went wrong: {e}")

    print(f"Frase: {phrase!r}\n")
    for r in results:
        print(line(r))

if __name__ == "__main__":
    main()