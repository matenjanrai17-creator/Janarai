"""Жеңіл позитив бит (120 BPM) — numpy синтез, авторлық құқықсыз. make(total, path, seed)."""
import numpy as np, wave

SR = 48000
BPM = 120
BEAT = 60 / BPM
NOTES = {'C': 261.63, 'D': 293.66, 'E': 329.63, 'F': 349.23, 'G': 392.0, 'A': 440.0, 'B': 493.88}
PROGS = [
    [('C', 'E', 'G'), ('G', 'B', 'D'), ('A', 'C', 'E'), ('F', 'A', 'C')],
    [('F', 'A', 'C'), ('G', 'B', 'D'), ('E', 'G', 'B'), ('A', 'C', 'E')],
    [('C', 'E', 'G'), ('A', 'C', 'E'), ('F', 'A', 'C'), ('G', 'B', 'D')],
]

def env(n, a=0.003, d=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / d)
    return e

def kick(n=int(0.3 * SR)):
    t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.12)

def noise(n, rng): return rng.uniform(-1, 1, n)

def hp(x, k=0.92):
    y = np.zeros_like(x); p = 0.0; px = 0.0
    for i in range(len(x)):
        p = k * (p + x[i] - px); px = x[i]; y[i] = p
    return y

def pluck(f, n, d=0.25):
    t = np.arange(n) / SR
    s = 0.6 * np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return s * env(n, 0.004, d)

def make(total, path, seed=0):
    rng = np.random.default_rng(seed)
    prog = PROGS[seed % len(PROGS)]
    N = int(total * SR) + SR
    mix = np.zeros(N)
    K = kick()
    clap_src = hp(noise(int(0.18 * SR), rng), 0.85) * env(int(0.18 * SR), 0.002, 0.05)
    hat = hp(noise(int(0.05 * SR), rng), 0.6) * env(int(0.05 * SR), 0.001, 0.015)
    nb = int(total / BEAT) + 2
    for b in range(nb):
        o = int(b * BEAT * SR)
        if o >= N: break
        def add(x, at, g):
            e = min(N, at + len(x)); mix[at:e] += g * x[:e - at]
        add(K, o, 0.9)
        if b % 2 == 1: add(clap_src, o, 0.35)
        add(hat, o + int(BEAT / 2 * SR), 0.18)
        if b % 4 == 3: add(hat, o + int(BEAT * 0.75 * SR), 0.12)
        ch = prog[(b // 4) % 4]
        root = NOTES[ch[0]] / 2
        add(pluck(root, int(BEAT * SR), 0.18), o, 0.35)                     # бас
        for k in range(2):                                                     # арпеджио 8-лер
            f = NOTES[ch[(b * 2 + k) % 3]] * 2
            add(pluck(f, int(BEAT / 2 * SR), 0.12), o + int(k * BEAT / 2 * SR), 0.16)
    mix = mix[:int(total * SR)]
    # соңында 1 с fade out
    fo = int(1.0 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
    mix /= max(1e-6, np.abs(mix).max()) / 0.8
    st = np.stack([mix, mix], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
