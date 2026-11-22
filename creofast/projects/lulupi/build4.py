#!/usr/bin/env python3
"""LULUPI KIDS v4 — спокойная версия по отзыву клиента:
- шрифт Nunito (мягкий, округлый), тексты меньше; без больших жёлтых слов на фоне;
- видео без фильтров/эффектов: без вспышек, размытия, зумов — чистые склейки;
- медленный мягкий бит (78 BPM), голос медленнее, клипы длиннее (≥2,3 с) — успеваешь читать и смотреть.
  python3 build4.py ru 2 1 [--test 1 5 9]     |   python3 build4.py pick5
"""
import sys, os, re, wave, math, random, zlib, subprocess, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import build as B
from build import R, fx, P, FF, W, H, FPS, TMP, OUT, READY, META, NB, run
from script import creative, KEYS, FACTS, HOOKS, EXTRAS, SAY
import music
import build2 as V2

# ---------- шрифт: Nunito вместо Montserrat везде ----------
NUN = P + 'fonts/Nunito.ttf'
WG = {'Black': 900, 'ExtraBold': 850, 'Bold': 750, 'SemiBold': 650, 'Medium': 550, 'Regular': 450}
_fc = {}
def font(w, s):
    k = (w, s)
    if k not in _fc:
        f = ImageFont.truetype(NUN, s); f.set_variation_by_axes([WG.get(w, 700)]); _fc[k] = f
    return _fc[k]
R.font = font

CORAL = (226, 58, 74); WHITE = (255, 255, 255); INK = (40, 40, 48); SOFTY = (255, 222, 110)
HOOK_Y, SUB_Y, ST_Y = 330, 1430, 1180
VOICE = {'ru': ('ru_RU-irina-medium', None, 0.97), 'kk': ('kk_KZ-issai-high', 4, 1.0)}

def ease(u): u = max(0.0, min(1.0, u)); return 1 - (1 - u) ** 3

# ---------- TTS (медленнее, без ускорения) ----------
def tts(lang, txt):
    s = B.say_text(lang, txt)
    name, spk, ls = VOICE[lang]
    out = B.TTS + 'v4_' + hashlib.md5(f'{name}|{spk}|{ls}|{s}'.encode()).hexdigest()[:16] + '.wav'
    if not os.path.exists(out):
        from piper import PiperVoice, SynthesisConfig
        if name not in B._voices: B._voices[name] = PiperVoice.load(os.path.expanduser(f'~/voices/{name}.onnx'))
        tmp = out + '.raw.wav'
        with wave.open(tmp, 'wb') as w:
            B._voices[name].synthesize_wav(s, w, syn_config=SynthesisConfig(speaker_id=spk, length_scale=ls))
        run([FF, '-v', 'error', '-y', '-i', tmp, '-af',
             'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
             'highpass=f=70,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=100', '-ar', '48000', '-ac', '2', out])
        os.remove(tmp)
    with wave.open(out) as w: return out, w.getnframes() / w.getframerate()

# ---------- графика ----------
def soft_shadow(im, r=10, op=150, dy=4):
    a = im.getchannel('A'); sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(min(255, v * op / 255 * 1.4))))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(sh, (0, dy)); out.alpha_composite(im); return out

_hk = {}
def hook_card(txt):
    if txt in _hk: return _hk[txt]
    t = txt[0] + txt[1:].lower() if txt.isupper() else txt
    t = re.sub(r'lulupi kids', 'LULUPI KIDS', t, flags=re.I).replace('montessori', 'Montessori').replace('мамыр', 'Мамыр')
    t = re.sub(r'([?!.]\s+)(\w)', lambda m: m.group(1) + m.group(2).upper(), t)
    t = re.sub(r'(\d) (\d)', r'\1' + NB + r'\2', t).replace(' ₸', NB + '₸')
    maxw = 820
    for size in range(62, 40, -2):
        f = font('ExtraBold', size); lines = R.wrap(t, f, maxw)
        if len(lines) <= 3: break
    lh = int(size * 1.28); tw = max(f.getlength(l) for l in lines)
    bw, bh = int(tw + 90), int(lh * len(lines) + 56)
    im = Image.new('RGBA', (bw + 60, bh + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((30, 30, 30 + bw, 30 + bh), radius=36, fill=(255, 255, 255, 245))
    for i, l in enumerate(lines):
        d.text((30 + bw / 2, 30 + 28 + i * lh + lh / 2), l, font=f, fill=CORAL, anchor='mm')
    _hk[txt] = soft_shadow(im, 14, 120, 6); return _hk[txt]

_sc = {}
def sub_card(words, active):
    key = (tuple(words), active)
    if key in _sc: return _sc[key]
    for size in range(58, 38, -2):
        f = font('ExtraBold', size); sp = f.getlength(' ')
        tw = sum(f.getlength(w) for w in words) + sp * (len(words) - 1)
        if tw <= 900: break
    im = Image.new('RGBA', (int(tw + 60), size + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 30
    for i, w in enumerate(words):
        d.text((x, 18), w, font=f, fill=SOFTY if i == active else WHITE, stroke_width=2, stroke_fill=(60, 50, 40))
        x += f.getlength(w) + sp
    _sc[key] = soft_shadow(im, 7, 190, 3); return _sc[key]

_st = {}
def stat_card(big, small):
    k = (big, small)
    if k in _st: return _st[k]
    fb, fs = font('Black', 72), font('Bold', 34)
    d0 = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    W_ = int(max(d0.textlength(big, font=fb), d0.textlength(small, font=fs)) + 90); H_ = 160
    im = Image.new('RGBA', (W_ + 40, H_ + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + W_, 20 + H_), radius=34, fill=(255, 255, 255, 245))
    d.text((20 + W_ / 2, 20 + 62), big, font=fb, fill=CORAL, anchor='mm')
    d.text((20 + W_ / 2, 20 + 122), small, font=fs, fill=(120, 120, 128), anchor='mm')
    _st[k] = soft_shadow(im, 12, 110, 5); return _st[k]

_pc = {}
def price_card(lang, val):
    k = (lang, val)
    if k in _pc: return _pc[k]
    old, top = '220 000 ₸', ('в месяц' if lang == 'ru' else 'айына')
    small = 'с ваучером' if lang == 'ru' else 'ваучермен'
    new = f'{val:,}'.replace(',', ' ') + ' ₸'
    fb, fm, fs = font('Black', 86), font('Bold', 40), font('Bold', 34)
    W_, H_ = 600, 270
    im = Image.new('RGBA', (W_ + 40, H_ + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + W_, 20 + H_), radius=38, fill=(255, 255, 255, 245))
    line = f'{old}  {top}'; lw = d.textlength(line, font=fm); x0 = 20 + W_ / 2 - lw / 2
    d.text((20 + W_ / 2, 20 + 50), line, font=fm, fill=(150, 150, 158), anchor='mm')
    ow = d.textlength(old, font=fm); d.line((x0 - 4, 20 + 52, x0 + ow + 4, 20 + 48), fill=CORAL, width=5)
    d.text((20 + W_ / 2, 20 + 135), new, font=fb, fill=CORAL, anchor='mm')
    bw = d.textlength(small, font=fs) + 50
    d.rounded_rectangle((20 + W_ / 2 - bw / 2, 20 + 195, 20 + W_ / 2 + bw / 2, 20 + 247), radius=26, fill=CORAL)
    d.text((20 + W_ / 2, 20 + 221), small, font=fs, fill=WHITE, anchor='mm')
    _pc[k] = soft_shadow(im, 12, 110, 5); return _pc[k]

def pill(txt):
    f = font('Bold', 32); d0 = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    w = int(d0.textlength(txt, font=f) + 50); h = 58
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=29, fill=(255, 255, 255, 215))
    d.text((w / 2, h / 2), txt, font=f, fill=CORAL, anchor='mm'); return im

def end_layers(lang):
    g = np.zeros((H, W, 4), np.uint8); ys = np.arange(H)[:, None]
    g[..., 3] = (np.clip((ys - 1000) / 600, 0, 1) * 170).astype(np.uint8).repeat(W, 1)
    grad = np.asarray(Image.fromarray(g, 'RGBA')).astype(np.float32)[..., 3:] / 255
    card = Image.new('RGBA', (900, 380), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, 899, 379), radius=44, fill=(255, 255, 255, 245))
    d.text((450, 70), 'LULUPI KIDS', font=font('Black', 72), fill=CORAL, anchor='mm')
    d.text((450, 128), 'Premium Montessori', font=font('SemiBold', 36), fill=(130, 130, 138), anchor='mm')
    bt = 'Запишитесь на экскурсию' if lang == 'ru' else 'Экскурсияға жазылыңыз'
    fb = font('ExtraBold', 46); bw = d.textlength(bt, font=fb) + 80
    d.rounded_rectangle((450 - bw / 2, 172, 450 + bw / 2, 262), radius=45, fill=CORAL)
    d.text((450, 217), bt, font=fb, fill=WHITE, anchor='mm')
    d.text((450, 322), FACTS['addr_ru' if lang == 'ru' else 'addr_kk'], font=font('Bold', 36), fill=INK, anchor='mm')
    return grad, soft_shadow(Image.fromarray(np.pad(np.asarray(card), ((30, 30), (30, 30), (0, 0)))), 16, 120, 6)

def paste(fr, im, cx, cy, sc=1.0, alpha=1.0):
    if alpha <= 0.01 or sc <= 0.02: return
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
    fx.paste(fr, im, cx, cy, sc)

def fade(t, a, b, fin=0.3, fout=0.25):
    if t < a or t >= b: return 0.0
    return min(1.0, (t - a) / fin, (b - t) / fout)

# ---------- один креатив ----------
def build(lang, body, hook, test=None):
    cid = f'{lang.upper()}{body}_H{hook}'
    phrases, seg = creative(lang, body, hook)
    hk = HOOKS[lang][hook]; EXTRAS_TXT = EXTRAS[lang][0]
    rnd = random.Random(zlib.crc32(('v4' + cid).encode()))
    t, auds = 0.4, []
    for ph in phrases:
        wav, d = tts(lang, ph['text'])
        ph['t0'], ph['t1'] = t, t + d; auds.append((wav, t))
        t += d + (0.45 if ph.get('hook') else 0.28)
    cta = phrases[-1]; total = cta['t1'] + 2.4
    # клипы: длинные, спокойные (≥2,3 с), склейка в начале фразы
    used, segs = set(), []
    for i, ph in enumerate(phrases):
        a = 0.0 if i == 0 else ph['t0'] - 0.1
        b = total if ph.get('cta') else phrases[i + 1]['t0'] - 0.1
        d = b - a
        if ph.get('cta'):
            segs.append((a, b, rnd.choice(['still:logo_sign', 'still:building', 'still:entrance']), None)); continue
        cats = list(hk['cats'][:2]) if ph.get('hook') else list(ph['cats'])
        n = max(1, min(len(cats), int(d / 2.3)))
        segs += [(a + d * j / n, a + d * (j + 1) / n, B.pick(cats[j], used, rnd), cats[j]) for j in range(n)]
    files = []
    for j, (a, b, c, cat) in enumerate(segs):
        n = round(b * FPS) - round(a * FPS)
        ss = B.offset(c, n / FPS, zlib.crc32(f'v4{cid}{j}'.encode()) % 97)
        pth = TMP + f'{re.sub("[^a-zA-Z0-9_]", "_", str(c))}_{ss:.2f}_{n}.mov'
        B.piece(c, ss, n, pth); files.append(pth)
    lst = TMP + f'v4_{cid}.txt'; open(lst, 'w').write(''.join(f"file '{f}'\n" for f in files))
    base = TMP + f'v4_{cid}_base.mov'
    run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-t', f'{total:.3f}', '-c', 'copy', base])
    # аудио
    sr = 48000; buf = np.zeros((int((total + 1) * sr), 2), np.float32)
    for wav, t0 in auds:
        with wave.open(wav) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32)
        o = int(t0 * sr); buf[o:o + len(x)] += x
    vo = TMP + f'v4_{cid}_vo.wav'
    with wave.open(vo, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.clip(buf[:int(total * sr)], -32768, 32767).astype(np.int16).tobytes())
    mu = TMP + f'v4_{cid}_music.wav'; music.make(total, mu, seed=zlib.crc32(cid.encode()), bpm=78, soft=True)
    mix = TMP + f'v4_{cid}_mix.wav'
    run([FF, '-v', 'error', '-y', '-i', vo, '-i', mu, '-i', base, '-filter_complex',
         '[0:a]asplit=2[v][key];[1:a]volume=0.5[m];[m][key]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=500[md];'
         '[2:a]highpass=f=150,volume=0.06[bg];[v][md][bg]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]',
         '-map', '[a]', '-ar', '48000', '-ac', '2', mix])
    # субтитры (обычный регистр, 2–3 слова)
    toks, brk, tt = [], [], []
    for ph in phrases:
        if ph.get('hook') or ph.get('cta'): continue
        ws = [w for w in re.sub(r'(\d) (\d)', r'\1' + NB + r'\2', ph['text']).replace(' ₸', NB + '₸').replace(' —', '').split(' ') if w]
        lens = np.array([len(w) + 1 for w in ws], float); cum = np.concatenate([[0], np.cumsum(lens)])
        for j, w in enumerate(ws):
            toks.append(w); brk.append(j == len(ws) - 1); tt.append(ph['t0'] + (ph['t1'] - ph['t0']) * cum[j] / cum[-1])
    cards, wi = [], 0
    for st, en, ws, _ in R.make_cards(toks, brk, tt, total, KEYS):
        idx = list(range(wi, wi + len(ws))); wi += len(ws)
        if st >= cta['t0'] - 0.1: continue
        cards.append((st, min(en + 0.15, cta['t0'] - 0.1), [w for w, _ in ws], [tt[i] for i in idx]))
    for k in range(len(cards) - 1):   # без мигания между карточками
        st, en, ws, wt = cards[k]
        if 0 < cards[k + 1][0] - en < 0.35: cards[k] = (st, cards[k + 1][0], ws, wt)
    hook_end = phrases[0]['t1'] + 0.6
    hookim = hook_card(hk['screen'])
    stick = []
    for ph in phrases:
        st = ph.get('st')
        if not st or ph.get('hook'): continue
        if st[0] == 'stat': stick.append(('stat', ph['t0'] + 0.1, ph['t1'] + 0.4, stat_card(st[1], st[2])))
        elif st[0] == 'addr': stick.append(('stat', ph['t0'] + 0.1, ph['t1'] + 0.4, stat_card('Мамыр-4, 156', 'г. Алматы' if lang == 'ru' else 'Алматы қ.')))
        elif st[0] == 'price': stick.append(('price', ph['t0'] + 0.1, ph['t1'] + 0.6, None))
    checks = []
    for ph in phrases:
        if ph['text'] == EXTRAS_TXT:
            keys = ['Англ', 'тхэкв', 'балет', 'танц', 'йога'] if lang == 'ru' else ['Ағылш', 'тхэкв', 'балет', 'би', 'йога']
            ws = ph['text'].split(); lens = np.cumsum([0] + [len(w) + 1 for w in ws])
            tms = []
            for kk in keys:
                j = next((j for j, w in enumerate(ws) if kk.lower() in w.lower()), 0)
                tms.append(ph['t0'] + (ph['t1'] - ph['t0']) * lens[j] / lens[-1])
            checks.append((ph['t0'] - 0.05, ph['t1'] + 0.6, V2.EXTRA_ITEMS[lang], tms))
    hdr = pill('LULUPI KIDS · Мамыр-4')
    grad, endcard = end_layers(lang)

    def comp(fr, t):
        fr = fr.copy()
        if t < cta['t0'] - 0.1: paste(fr, hdr, W / 2, 110, 1.0, 0.95 * min(1, t / 0.4))
        a = fade(t, 0.15, hook_end, 0.35, 0.3)
        if a: paste(fr, hookim, W / 2, HOOK_Y, 0.94 + 0.06 * ease((t - 0.15) / 0.35), a)
        for kind, s0, s1, im in stick:
            s1 = min(s1, cta['t0'] - 0.1); a = fade(t, s0, s1)
            if not a: continue
            if kind == 'stat': paste(fr, im, W / 2, ST_Y, 0.92 + 0.08 * ease((t - s0) / 0.3), a)
            else:
                u = ease((t - s0 - 0.3) / 1.3); val = int(round((220000 - 80000 * u) / 1000)) * 1000
                paste(fr, price_card(lang, val), W / 2, ST_Y - 40, 0.92 + 0.08 * ease((t - s0) / 0.3), a)
        for c0, c1, its, tms in checks:
            a = fade(t, c0, min(c1, cta['t0'] - 0.1))
            if a:
                non = sum(1 for x in tms if x <= t + 0.05)
                paste(fr, V2.checklist(lang, its, non), W / 2, 470, 0.82, a)
        if t >= cta['t0'] - 0.1:
            u = t - cta['t0'] + 0.1; k = min(1.0, u / 0.5)
            fr[:] = (fr * (1 - grad * k)).astype(np.uint8)
            paste(fr, endcard, W / 2, 1330 + 40 * (1 - ease(u / 0.6)), 1.0, min(1, u / 0.5))
        else:
            cd = next((c_ for c_ in cards if c_[0] <= t < c_[1]), None)
            if cd and t >= hook_end - 0.2:
                st, en, ws, wt = cd
                act = max([i for i, x in enumerate(wt) if x <= t + 0.03] or [0])
                paste(fr, sub_card(ws, act), W / 2, SUB_Y, 1.0, min(1, (t - st) / 0.12))
        return fr

    if test:
        for x in test:
            raw = subprocess.run([FF, '-v', 'error', '-ss', str(x), '-i', base, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
            Image.fromarray(comp(np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy(), x)).resize((540, 960)).save(P + f'test/v4_{cid}_{x:05.2f}.jpg', quality=85)
        return
    out = OUT + f'v4_LULUPI_{cid}.mp4'
    dec = subprocess.Popen([FF, '-v', 'error', '-i', base, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    fs = W * H * 3; fi = 0
    while True:
        bb = dec.stdout.read(fs)
        if len(bb) < fs: break
        enc.stdin.write(comp(np.frombuffer(bb, np.uint8).reshape(H, W, 3), fi / FPS).tobytes()); fi += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    dst = READY + 'v4_спокойные_5/'; os.makedirs(dst, exist_ok=True)
    subprocess.run(['cp', out, dst + f'LULUPI_{cid}.mp4'])
    print(f'DONE {cid} {total:.1f}s', flush=True)

PICK5 = [('ru', 2, 1), ('ru', 1, 2), ('ru', 3, 3), ('kk', 2, 1), ('kk', 1, 3)]
if __name__ == '__main__':
    a = sys.argv[1:]
    test = [float(x) for x in a[a.index('--test') + 1:]] if '--test' in a else None
    if a[0] == 'pick5':
        part = int(a[1]) if len(a) > 2 else 0; npart = int(a[2]) if len(a) > 2 else 1
        for i, x in enumerate(PICK5):
            if i % npart == part and not os.path.exists(OUT + f'v4_LULUPI_{x[0].upper()}{x[1]}_H{x[2]}.mp4'): build(*x)
    else:
        build(a[0], int(a[1]), int(a[2]), test)
