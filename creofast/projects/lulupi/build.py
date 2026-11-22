#!/usr/bin/env python3
"""LULUPI KIDS креативтері — creofast стилі (қызыл хук, 2–3 сөздік субтитр, стикерлер), B-roll айтылған сөзге сай.
Дауыс: Piper TTS (kk_KZ-issai-high / ru_RU-irina-medium). Бастапқы видеолар: src/ (Drive-тан).
  python3 build.py ru 1 3          # бір креатив
  python3 build.py all             # 30 креатив
  python3 build.py ru 1 3 --test 1 5 12   # тек кадрлар
"""
import sys, os, json, re, wave, hashlib, subprocess, random, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

P = os.path.dirname(os.path.abspath(__file__)) + '/'
E = os.path.expanduser('~/creofast-kit/engine')
os.environ.setdefault('RAZBOR_WORK', P)
sys.path.insert(0, E); sys.path.insert(0, P)
import render as R
NB = '\u00a0'
def _wrap(txt, f, maxw):
    lines, cur = [], ''
    for w in txt.split(' '):
        c = (cur + ' ' + w).strip(' ')
        if f.getlength(c) > maxw and cur: lines.append(cur); cur = w
        else: cur = c
    return lines + [cur]
R.wrap = _wrap
import fx
from script import creative, SAY, KEYS, FACTS
from clips import CATS, START

FF = 'ffmpeg'
W, H, FPS = 1080, 1920, 30
OUT, TMP, TTS = P + 'out/', P + 'out/tmp/', P + 'audio/tts/'
READY = os.path.abspath(P + '../../ready') + '/'
for d in (OUT, TMP, TTS, P + 'test'): os.makedirs(d, exist_ok=True)
META = {i: (f, d) for i, f, d in json.load(open(P + 'meta.json'))}
HOOK_Y, SUB_Y, ST_Y = 380, 1400, 1150
VOICE = {'ru': ('ru_RU-irina-medium', None, 0.84), 'kk': ('kk_KZ-issai-high', 4, 0.87)}
_voices = {}

def run(cmd): subprocess.run(cmd, check=True)

# ---------- TTS ----------
def say_text(lang, txt):
    for a, b in SAY[lang]: txt = txt.replace(a, b)
    return txt.replace(' — ', ' ').replace('₸', 'тенге' if lang == 'ru' else 'теңге')

def tts(lang, txt):
    s = say_text(lang, txt)
    name, spk, ls = VOICE[lang]
    out = TTS + hashlib.md5(f'{name}|{spk}|{ls}|{s}'.encode()).hexdigest()[:16] + '.wav'
    if not os.path.exists(out):
        from piper import PiperVoice, SynthesisConfig
        if name not in _voices: _voices[name] = PiperVoice.load(os.path.expanduser(f'~/voices/{name}.onnx'))
        tmp = out + '.raw.wav'
        with wave.open(tmp, 'wb') as w:
            _voices[name].synthesize_wav(s, w, syn_config=SynthesisConfig(speaker_id=spk, length_scale=ls))
        # 48k стерео + басы/соңындағы тыныштықты қию
        run([FF, '-v', 'error', '-y', '-i', tmp, '-af',
             'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
             'atempo=1.07,highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80', '-ar', '48000', '-ac', '2', out])
        os.remove(tmp)
    with wave.open(out) as w: return out, w.getnframes() / w.getframerate()

# ---------- клип таңдау ----------
USE = {}   # бүкіл партия бойынша: клип -> қанша рет қолданылды
def pick(cat, used, rnd):
    pool = CATS[cat]
    cand = [c for c in pool if c not in used] or pool
    m = min(USE.get(c, 0) for c in cand)
    best = [c for c in cand if USE.get(c, 0) == m]
    c = rnd.choice(best); used.add(c); USE[c] = USE.get(c, 0) + 1
    return c

def offset(c, dur, k):
    if isinstance(c, str): return 0.0
    f, total = META[c]
    s0 = START.get(c, 0.4)
    span = max(0.0, total - s0 - dur - 0.3)
    return s0 + (span * ((k * 0.37) % 1.0) if span > 0 else 0.0)

# ---------- кесінділерді дайындау ----------
COVER = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1'
def piece(c, ss, n, out):
    """n кадр дәл (дрейф болмасын)."""
    if os.path.exists(out): return
    dur = n / FPS
    if isinstance(c, str):   # still:<name> — баяу жақындау
        img = P + 'stills/' + c.split(':')[1] + '.jpg'
        vf = (f'[0:v]scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,'
              f"zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n + 5}:s=1080x1920:fps={FPS},setsar=1[v]")
        run([FF, '-v', 'error', '-y', '-i', img, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
             '-filter_complex', vf, '-map', '[v]', '-map', '1:a', '-frames:v', str(n), '-t', f'{dur:.4f}',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', out + '.mov'])
    else:
        src = P + 'src/' + META[c][0]
        fc = f'[0:v]{COVER},fps={FPS},tpad=stop_mode=clone:stop_duration=2[v];[0:a]aresample=48000,apad[a]'
        run([FF, '-v', 'error', '-y', '-ss', f'{ss:.3f}', '-i', src, '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
             '-frames:v', str(n), '-t', f'{dur:.4f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p',
             '-c:a', 'pcm_s16le', '-ac', '2', out + '.mov'])
    os.rename(out + '.mov', out)

# ---------- графика ----------
RED = (227, 6, 19)
def price_img(lang):
    fb, fm, fs = R.font('ExtraBold', 116), R.font('Bold', 58), R.font('Bold', 42)
    old, new = '220 000 ₸', '140 000 ₸'
    small = 'с ваучером' if lang == 'ru' else 'ваучермен'
    top = 'в месяц' if lang == 'ru' else 'айына'
    d0 = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    W_ = int(max(700, d0.textlength(f'{old}  {top}', font=fm) + 110, d0.textlength(new, font=fb) + 110)); H_ = 360
    card = fx.rgba_card(W_, H_, (255, 255, 255, 255), 40); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, 18, H_ - 1), radius=9, fill=RED)
    d.text((W_ / 2 + 8, 62), f'{old}  {top}', font=fm, fill=(140, 140, 140), anchor='mm')
    tw = d.textlength(old, font=fm); x0 = W_ / 2 + 8 - d.textlength(f'{old}  {top}', font=fm) / 2
    d.line((x0 - 6, 64, x0 + tw + 6, 58), fill=RED, width=7)
    d.text((W_ / 2 + 8, 182), new, font=fb, fill=(17, 17, 17), anchor='mm')
    bw = d.textlength(small, font=fs) + 56
    d.rounded_rectangle((W_ / 2 + 8 - bw / 2, 262, W_ / 2 + 8 + bw / 2, 330), radius=34, fill=RED)
    d.text((W_ / 2 + 8, 296), small, font=fs, fill=(255, 255, 255), anchor='mm')
    return fx.shadowed(card, 40)

def stat_img(big, small):
    return fx.stat_img(big, small)

def end_overlay(lang, cta):
    """CTA соңғы кадры: төменгі қараңғы градиент + қызыл түйме + мекенжай."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g = np.zeros((H, W, 4), np.uint8)
    ys = np.arange(H)[:, None]
    a = np.clip((ys - 900) / 700, 0, 1) * 215
    g[..., 3] = a.astype(np.uint8).repeat(W, 1)
    im = Image.fromarray(g, 'RGBA')
    d = ImageDraw.Draw(im)
    btn = 'ЗАПИШИТЕСЬ НА ЭКСКУРСИЮ' if lang == 'ru' else 'ЭКСКУРСИЯҒА ЖАЗЫЛЫҢЫЗ'
    f1 = R.font('ExtraBold', 60)
    for s in range(60, 40, -2):
        f1 = R.font('ExtraBold', s)
        if d.textlength(btn, font=f1) < 860: break
    bw = d.textlength(btn, font=f1) + 90
    d.rounded_rectangle((W / 2 - bw / 2, 1180, W / 2 + bw / 2, 1300), radius=26, fill=RED + (255,))
    d.text((W / 2, 1240), btn, font=f1, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, 1090), 'LULUPI KIDS', font=R.font('ExtraBold', 92), fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, 1375), 'Premium Montessori', font=R.font('SemiBold', 44), fill=(255, 255, 255, 235), anchor='mm')
    d.text((W / 2, 1445), FACTS['addr_ru' if lang == 'ru' else 'addr_kk'], font=R.font('Bold', 46), fill=(255, 255, 255), anchor='mm')
    arr = np.asarray(im).astype(np.float32)
    return arr[..., :3], arr[..., 3:] / 255

def paste_rgba(fr, im, cx, cy, sc=1.0): fx.paste(fr, im, cx, cy, sc)

# ---------- бір креатив ----------
def build(lang, body, hook, test=None, plan_only=False):
    cid = f'{lang.upper()}{body}_H{hook}'
    phrases, seg = creative(lang, body, hook)
    rnd = random.Random(zlib.crc32(cid.encode()))
    # 1) дауыс
    t, auds = 0.25, []
    for i, ph in enumerate(phrases):
        wav, d = tts(lang, ph['text'])
        ph['t0'], ph['t1'] = t, t + d
        auds.append((wav, t))
        t += d + (0.25 if ph.get('hook') else 0.10)
    cta = phrases[-1]; cta['t1h'] = cta['t1'] + 1.6
    total = cta['t1h']
    # 2) B-roll жоспары
    used, segs, k = set(), [], 0
    for i, ph in enumerate(phrases):
        a = 0.0 if i == 0 else ph['t0'] - 0.05            # кесу сөз басталар сәтте
        b = total if ph.get('cta') else phrases[i + 1]['t0'] - 0.05
        d = b - a
        if ph.get('cta'):
            segs.append((a, b, rnd.choice(['still:logo_sign', 'still:building', 'still:entrance'])))
            continue
        cats = list(ph['cats'])
        mn = 0.9 if len(cats) >= 4 else 1.25
        n = max(1, min(len(cats), int(d / mn)))
        if n == 1 and d > 3.4: n, cats = 2, cats * 2
        cats = cats[:n]
        for j, c in enumerate(cats):
            x0, x1 = a + d * j / n, a + d * (j + 1) / n
            segs.append((x0, x1, pick(c, used, rnd)))
    # 3) кесінділер + негізгі видео
    if plan_only: return
    files = []
    for j, (a, b, c) in enumerate(segs):
        n = round(b * FPS) - round(a * FPS)
        ss = offset(c, n / FPS, zlib.crc32(f'{cid}{j}'.encode()) % 97)
        pth = TMP + f'{re.sub("[^a-zA-Z0-9_]", "_", str(c))}_{ss:.2f}_{n}.mov'
        piece(c, ss, n, pth)
        files.append(pth)
    lst = TMP + f'{cid}.txt'
    open(lst, 'w').write(''.join(f"file '{f}'\n" for f in files))
    base = TMP + f'{cid}_base.mov'
    run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-t', f'{total:.3f}', '-c', 'copy', base])
    # 4) аудио: дауыс + фон (кадрдағы табиғи дыбыс, тыныш)
    vo = TMP + f'{cid}_vo.wav'
    sr = 48000; buf = np.zeros((int((total + 1) * sr), 2), np.float32)
    for wav, t0 in auds:
        with wave.open(wav) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32)
        o = int(t0 * sr); buf[o:o + len(x)] += x
    buf = buf[:int(total * sr)]
    with wave.open(vo, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.clip(buf, -32768, 32767).astype(np.int16).tobytes())
    mix = TMP + f'{cid}_mix.wav'
    run([FF, '-v', 'error', '-y', '-i', vo, '-i', base, '-filter_complex',
         '[1:a]highpass=f=120,volume=0.16[bg];[0:a]volume=1.0[v];[v][bg]amix=inputs=2:duration=first:normalize=0,'
         'loudnorm=I=-14:TP=-1.5:LRA=9[a]', '-map', '[a]', '-ar', '48000', '-ac', '2', mix])
    # 5) субтитр карточкалары
    toks, brk, tt = [], [], []
    for ph in phrases:
        if ph.get('hook') or ph.get('cta'): continue
        ws = [w for w in re.sub(r'(\d) (\d)', r'\1' + NB + r'\2', ph['text']).replace(' ₸', NB + '₸').split(' ') if w]
        lens = np.array([len(w) + 1 for w in ws], float); cum = np.concatenate([[0], np.cumsum(lens)])
        for j, w in enumerate(ws):
            toks.append(w); brk.append(j == len(ws) - 1)
            tt.append(ph['t0'] + (ph['t1'] - ph['t0']) * cum[j] / cum[-1])
    cards = R.make_cards(toks, brk, tt, total, KEYS)
    cards = [(st, min(en, cta['t0'] - 0.05), w, kk) for st, en, w, kk in cards if st < cta['t0']]
    # кейінгі карта алдыңғы фразаның соңынан кейін бос тұрмасын
    hook_img = R.hook_img(re.sub(r'(\d) (\d)', r'\1' + NB + r'\2', phrases[0]['screen_hook']).replace(' ₸', NB + '₸'))
    hook_end = max(R.HOOK_T, phrases[0]['t1'] + 0.35)
    # стикерлер
    stick = []
    for ph in phrases:
        st = ph.get('st')
        if not st: continue
        if st[0] == 'stat': im = stat_img(st[1], st[2]).rotate(-3, resample=Image.BICUBIC, expand=True)
        elif st[0] == 'price': im = price_img(lang).rotate(2, resample=Image.BICUBIC, expand=True)
        elif st[0] == 'addr': im = stat_img('Мамыр-4, 156', 'г. Алматы' if lang == 'ru' else 'Алматы қ.').rotate(-3, resample=Image.BICUBIC, expand=True)
        stick.append((ph['t0'] + 0.15, ph['t1'] + 0.5, im))
    endo = end_overlay(lang, cta)
    # 6) кадр композициясы
    def comp(fr, t):
        fr = fr.copy()
        if t < hook_end: R.blend(fr, *hook_img, W / 2, HOOK_Y)
        for a, b, im in stick:
            if a <= t < b:
                u = min(1.0, (t - a) / 0.22); sc = fx.pop(u)
                if b - t < 0.15: sc *= max(0.0, (b - t) / 0.15)
                paste_rgba(fr, im, W / 2, ST_Y, sc)
        if t >= cta['t0'] - 0.05:
            rgb, al = endo; u = min(1.0, (t - cta['t0'] + 0.05) / 0.3)
            fr[:] = (fr * (1 - al * u) + rgb * al * u).astype(np.uint8)
        else:
            c = next((c for c in cards if c[0] <= t < c[1]), None)
            if c and t >= hook_end - 0.3: R.blend(fr, *R.sub_img(tuple(c[2]), False), W / 2, SUB_Y)
        return fr
    if test:
        for x in test:
            fr = np.frombuffer(subprocess.run([FF, '-v', 'error', '-ss', str(x), '-i', base, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                              capture_output=True).stdout, np.uint8).reshape(H, W, 3)
            Image.fromarray(comp(fr, x)).resize((540, 960)).save(P + f'test/{cid}_{x:05.1f}.jpg', quality=85)
        return
    out = OUT + f'LULUPI_{cid}.mp4'
    dec = subprocess.Popen([FF, '-v', 'error', '-i', base, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out],
                           stdin=subprocess.PIPE)
    fs = W * H * 3; fi = 0
    while True:
        b = dec.stdout.read(fs)
        if len(b) < fs: break
        enc.stdin.write(comp(np.frombuffer(b, np.uint8).reshape(H, W, 3), fi / FPS).tobytes()); fi += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    dst = READY + f'{lang.upper()}/{seg}/'; os.makedirs(dst, exist_ok=True)
    subprocess.run(['cp', out, dst])
    with open(OUT + 'plan.log', 'a') as fh:
        fh.write(f'{cid} {total:.1f}s ' + ' | '.join(f'{a:.1f}-{b:.1f}:{c}' for a, b, c in segs) + '\n')
    print(f'DONE {cid} {total:.1f}s -> {dst}', flush=True)

ALL = [(l, b, h) for l in ('ru', 'kk') for b in (1, 2, 3) for h in (1, 2, 3, 4, 5)]
if __name__ == '__main__':
    a = sys.argv[1:]
    test = [float(x) for x in a[a.index('--test') + 1:]] if '--test' in a else None
    if a[0] == 'all':
        part = int(a[1]) if len(a) > 2 else 0; nparts = int(a[2]) if len(a) > 2 else 1
        # USE есептегішін барлық бөлікте бірдей ету үшін жоспар ретпен жүреді, рендер тек өз бөлігі
        for i, (l, b, h) in enumerate(ALL):
            build(l, b, h, plan_only=(i % nparts != part))
    else:
        build(a[0], int(a[1]), int(a[2]), test)
