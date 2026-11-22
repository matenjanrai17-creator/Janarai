#!/usr/bin/env python3
"""LULUPI KIDS v2 — «вау» нұсқа: хукта жылдам монтаж, битке кесу, punch/flash/whip ауысулар, Ken Burns,
караоке-субтитр, эмодзи-стикерлер, баға кері санау + конфетти, анимациялы соңғы кадр, музыка.
  python3 build2.py ru 1 3 [--test 1 5 9]
  python3 build2.py all [part nparts]
"""
import sys, os, re, wave, math, random, zlib, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

import build as B
from build import R, fx, P, FF, W, H, FPS, TMP, OUT, READY, META, NB, run
from script import creative, KEYS, FACTS, HOOKS
import music

EMO_FONT = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
EMOJI = {'montessori': '🧩', 'learn': '✏️', 'class': '📚', 'kazakh': '📚', 'teacher': '🤗', 'english': '🇬🇧', 'food': '🍎',
         'selfserve': '🙌', 'play': '🎈', 'outdoor': '☀️', 'ballet': '🩰', 'taekwondo': '🥋', 'dance': '💃', 'yoga': '🧘',
         'toddlers': '👶', 'seniors': '🎒', 'groups': '👫', 'happy': '😍', 'building': '🏡'}
YEL = (255, 214, 0); RED = (227, 6, 19); WHITE = (255, 255, 255)
HOOK_Y, SUB_Y, ST_Y, EMO_POS = 400, 1400, 1130, (905, 560)
BEAT = music.BEAT

def ease(u): u = max(0.0, min(1.0, u)); return 1 - (1 - u) ** 3
def back(u):  # асып барып оралу
    u = max(0.0, min(1.0, u)); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2

# ---------- графика ----------
_ec = {}
def emoji_img(e, size=150):
    k = (e, size)
    if k in _ec: return _ec[k]
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), e, font=EMO_FONT, embedded_color=True, anchor='mm')
    bb = im.getbbox() or (0, 0, 160, 160); im = im.crop(bb)
    s = size / max(im.size); im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    # ақ дөңгелек фон
    D = int(size * 1.45)
    out = Image.new('RGBA', (D + 40, D + 40), (0, 0, 0, 0))
    sh = Image.new('L', out.size, 0); ImageDraw.Draw(sh).ellipse((20, 30, 20 + D, 30 + D), fill=110)
    from PIL import ImageFilter
    out.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(out).ellipse((20, 20, 20 + D, 20 + D), fill=(255, 255, 255, 255))
    out.alpha_composite(im, (20 + (D - im.width) // 2, 20 + (D - im.height) // 2))
    _ec[k] = out; return out

def star(size, col=(255, 214, 0)):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = size / 2
    pts = []
    for i in range(8):
        r = c if i % 2 == 0 else c * 0.28; a = math.pi / 4 * i - math.pi / 2
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=col + (255,)); return im
STAR = star(70)

_hk = {}
def hook_frame(txt, k):
    """Қызыл қорап толық өлшемде, ішінде алғашқы k сөз ғана (сөзбе-сөз шығу)."""
    key = (txt, k)
    if key in _hk: return _hk[key]
    maxw = 820
    for size in range(78, 44, -2):
        f = R.font('ExtraBold', size); lines = R.wrap(txt, f, maxw)
        if len(lines) <= 3 and max(f.getlength(l) for l in lines) <= maxw: break
    lh = int(size * 1.2); tw = max(f.getlength(l) for l in lines)
    padx, pady = 40, 26
    bw, bh = int(tw + padx * 2), int(lh * len(lines) + pady * 2 - (lh - size) + 8)
    im = Image.new('RGBA', (bw + 24, bh + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 18, bw + 12, bh + 18), radius=24, fill=(120, 0, 8, 160))
    d.rounded_rectangle((12, 12, bw + 12, bh + 12), radius=24, fill=RED + (255,))
    n = 0
    for i, l in enumerate(lines):
        ws = l.split(' '); x = 12 + bw / 2 - f.getlength(l) / 2
        for w in ws:
            if n < k:
                col = YEL if re.search(r'\d|₸|MONTESSORI|LULUPI|БЕЗ|ҚОСЫМША|140', w) else WHITE
                d.text((x, 12 + pady + i * lh), w, font=f, fill=col)
            x += f.getlength(w + ' '); n += 1
    _hk[key] = im; return im

_sc = {}
def sub_card(words, active):
    """Караоке субтитр: БАС ӘРІП, қара жиек, айтылып жатқан сөз сары."""
    key = (tuple(words), active)
    if key in _sc: return _sc[key]
    size = 66
    for size in range(66, 40, -2):
        f = R.font('ExtraBold', size); sp = f.getlength(' ')
        tw = sum(f.getlength(w) for w in words) + sp * (len(words) - 1)
        if tw <= 920: break
    im = Image.new('RGBA', (int(tw + 60), size + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 30
    for i, w in enumerate(words):
        col = YEL if i == active else WHITE
        d.text((x, 24), w, font=f, fill=col, stroke_width=7, stroke_fill=(0, 0, 0))
        x += f.getlength(w) + sp
    _sc[key] = im; return im

_pc = {}
def price_card(lang, val, strike):
    key = (lang, val, round(strike, 2))
    if key in _pc: return _pc[key]
    fb, fm, fs = R.font('ExtraBold', 120), R.font('Bold', 58), R.font('Bold', 44)
    old, top = '220 000 ₸', ('в месяц' if lang == 'ru' else 'айына')
    small = 'с ваучером' if lang == 'ru' else 'ваучермен'
    new = f'{val:,}'.replace(',', ' ') + ' ₸'
    d0 = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    W_ = int(max(720, d0.textlength(f'{old}  {top}', font=fm) + 120, d0.textlength('220 000 ₸', font=fb) + 110)); H_ = 370
    card = fx.rgba_card(W_, H_, (255, 255, 255, 255), 40); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, 18, H_ - 1), radius=9, fill=RED)
    line = f'{old}  {top}'; x0 = W_ / 2 + 8 - d.textlength(line, font=fm) / 2
    d.text((W_ / 2 + 8, 62), line, font=fm, fill=(140, 140, 140), anchor='mm')
    tw = d.textlength(old, font=fm)
    if strike > 0: d.line((x0 - 6, 66, x0 - 6 + (tw + 12) * strike, 58), fill=RED, width=8)
    d.text((W_ / 2 + 8, 186), new, font=fb, fill=(17, 17, 17) if val > 140000 else RED, anchor='mm')
    bw = d.textlength(small, font=fs) + 60
    d.rounded_rectangle((W_ / 2 + 8 - bw / 2, 268, W_ / 2 + 8 + bw / 2, 340), radius=36, fill=RED)
    d.text((W_ / 2 + 8, 304), small, font=fs, fill=WHITE, anchor='mm')
    _pc[key] = fx.shadowed(card, 40); return _pc[key]

def end_layers(lang):
    g = np.zeros((H, W, 4), np.uint8); ys = np.arange(H)[:, None]
    g[..., 3] = (np.clip((ys - 850) / 650, 0, 1) * 225).astype(np.uint8).repeat(W, 1)
    grad = Image.fromarray(g, 'RGBA')
    title = Image.new('RGBA', (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(title)
    d.text((W / 2, 80), 'LULUPI KIDS', font=R.font('ExtraBold', 104), fill=WHITE, anchor='mm', stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((W / 2, 175), 'Premium Montessori', font=R.font('SemiBold', 46), fill=WHITE, anchor='mm')
    btn_t = 'ЗАПИШИТЕСЬ НА ЭКСКУРСИЮ' if lang == 'ru' else 'ЭКСКУРСИЯҒА ЖАЗЫЛЫҢЫЗ'
    f1 = R.font('ExtraBold', 60)
    for s in range(60, 40, -2):
        f1 = R.font('ExtraBold', s)
        if d.textlength(btn_t, font=f1) < 840: break
    bw = int(d.textlength(btn_t, font=f1) + 100)
    btn = Image.new('RGBA', (bw, 130), (0, 0, 0, 0)); db = ImageDraw.Draw(btn)
    db.rounded_rectangle((0, 0, bw - 1, 129), radius=30, fill=RED + (255,))
    db.text((bw / 2, 65), btn_t, font=f1, fill=WHITE, anchor='mm')
    addr = Image.new('RGBA', (W, 90), (0, 0, 0, 0)); da = ImageDraw.Draw(addr)
    txt = FACTS['addr_ru' if lang == 'ru' else 'addr_kk']
    fa = R.font('Bold', 48); tw = da.textlength(txt, font=fa)
    pin = emoji_img('📍', 46).resize((60, 60))
    addr.alpha_composite(pin, (int(W / 2 - tw / 2 - 70), 12))
    da.text((W / 2 + 4, 45), txt, font=fa, fill=WHITE, anchor='mm')
    return grad, title, btn, addr

def paste(fr, im, cx, cy, sc=1.0, rot=0.0, alpha=1.0):
    if sc <= 0.02 or alpha <= 0.01: return
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1: a = im.getchannel('A').point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    fx.paste(fr, im, cx, cy, sc)

def zoom(fr, s, cx=0.5, cy=0.5, dx=0, rot=0.0):
    if abs(s - 1) < 1e-3 and not dx and not rot: return fr
    M = cv2.getRotationMatrix2D((W * cx, H * cy), rot, s); M[0, 2] += dx
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

TRANS = ['punch', 'whip', 'flash', 'spin', 'punch', 'whip']

# ---------- бір креатив ----------
def build(lang, body, hook, test=None, plan_only=False):
    cid = f'{lang.upper()}{body}_H{hook}'
    phrases, seg = creative(lang, body, hook)
    hk = HOOKS[lang][hook]
    rnd = random.Random(zlib.crc32(('v2' + cid).encode()))
    t, auds = 0.15, []
    for ph in phrases:
        wav, d = B.tts(lang, ph['text'])
        ph['t0'], ph['t1'] = t, t + d; auds.append((wav, t))
        t += d + (0.25 if ph.get('hook') else 0.10)
    cta = phrases[-1]; total = cta['t1'] + 2.0
    snap = lambda x: round(x / BEAT) * BEAT if abs(x - round(x / BEAT) * BEAT) < 0.2 else x
    # B-roll: хук — жылдам монтаж (~0,5–0,75 с), қалғаны — сөзге сай, кесу битке
    used, segs = set(), []
    for i, ph in enumerate(phrases):
        a = 0.0 if i == 0 else snap(ph['t0'] - 0.05)
        b = total if ph.get('cta') else snap(phrases[i + 1]['t0'] - 0.05)
        d = b - a
        if ph.get('cta'):
            segs.append((a, b, rnd.choice(['still:logo_sign', 'still:building', 'still:entrance']), None)); continue
        if ph.get('hook'):
            n = max(3, int(d / 0.6)); cats = (hk['cats'] * 3)[:n]
        else:
            cats = list(ph['cats']); mn = 0.9 if len(cats) >= 4 else 1.2
            n = max(1, min(len(cats), int(d / mn)))
            if n == 1 and d > 3.0: n, cats = 2, cats * 2
            cats = cats[:n]
        for j, c in enumerate(cats):
            x0, x1 = a + d * j / n, a + d * (j + 1) / n
            if j: x0 = snap(x0)
            if j < n - 1: x1 = snap(x1)
            segs.append((x0, x1, B.pick(c, used, rnd), c))
    if plan_only: return
    files = []
    for j, (a, b, c, cat) in enumerate(segs):
        n = round(b * FPS) - round(a * FPS)
        ss = B.offset(c, n / FPS, zlib.crc32(f'{cid}{j}'.encode()) % 97)
        pth = TMP + f'{re.sub("[^a-zA-Z0-9_]", "_", str(c))}_{ss:.2f}_{n}.mov'
        B.piece(c, ss, n, pth); files.append(pth)
    lst = TMP + f'v2_{cid}.txt'; open(lst, 'w').write(''.join(f"file '{f}'\n" for f in files))
    base = TMP + f'v2_{cid}_base.mov'
    run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-t', f'{total:.3f}', '-c', 'copy', base])
    # аудио: дауыс + музыка (дауыс кезінде басылады) + табиғи дыбыс
    sr = 48000; buf = np.zeros((int((total + 1) * sr), 2), np.float32)
    for wav, t0 in auds:
        with wave.open(wav) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32)
        o = int(t0 * sr); buf[o:o + len(x)] += x
    vo = TMP + f'v2_{cid}_vo.wav'
    with wave.open(vo, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.clip(buf[:int(total * sr)], -32768, 32767).astype(np.int16).tobytes())
    mu = TMP + f'v2_{cid}_music.wav'; music.make(total, mu, seed=zlib.crc32(cid.encode()))
    whoosh = []  # ауысу сәттері (музыкалық акцент үшін)
    mix = TMP + f'v2_{cid}_mix.wav'
    run([FF, '-v', 'error', '-y', '-i', vo, '-i', mu, '-i', base, '-filter_complex',
         '[0:a]asplit=2[v][key];[1:a]volume=0.55[m];[m][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=300[md];'
         '[2:a]highpass=f=150,volume=0.08[bg];[v][md][bg]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]',
         '-map', '[a]', '-ar', '48000', '-ac', '2', mix])
    # субтитр сөздері
    toks, brk, tt = [], [], []
    for ph in phrases:
        if ph.get('hook') or ph.get('cta'): continue
        ws = [w for w in re.sub(r'(\d) (\d)', r'\1' + NB + r'\2', ph['text']).replace(' ₸', NB + '₸').replace(' —', '').split(' ') if w]
        lens = np.array([len(w) + 1 for w in ws], float); cum = np.concatenate([[0], np.cumsum(lens)])
        for j, w in enumerate(ws):
            toks.append(w); brk.append(j == len(ws) - 1); tt.append(ph['t0'] + (ph['t1'] - ph['t0']) * cum[j] / cum[-1])
    cards_raw = R.make_cards(toks, brk, tt, total, KEYS)
    cards, wi = [], 0
    for st, en, ws, _ in cards_raw:
        idx = list(range(wi, wi + len(ws))); wi += len(ws)
        if st >= cta['t0'] - 0.05: continue
        cards.append((st, min(en, cta['t0'] - 0.05), [w.upper() for w, _ in ws], [tt[i] for i in idx]))
    hook_words = hk['screen'].replace('₸', '₸').split(' ')
    hook_txt = re.sub(r'(\d) (\d)', r'\1' + NB + r'\2', hk['screen']).replace(' ₸', NB + '₸')
    nhw = len(hook_txt.split(' '))
    hook_end = max(R.HOOK_T, phrases[0]['t1'] + 0.4)
    hook_dur_words = max(0.6, phrases[0]['t1'] - phrases[0]['t0'])
    # стикерлер
    stick = []
    for ph in phrases:
        st = ph.get('st')
        if not st: continue
        if st[0] == 'stat': stick.append(('stat', ph['t0'] + 0.1, ph['t1'] + 0.5, fx.stat_img(st[1], st[2])))
        elif st[0] == 'addr': stick.append(('stat', ph['t0'] + 0.1, ph['t1'] + 0.5, fx.stat_img('Мамыр-4, 156', 'г. Алматы' if lang == 'ru' else 'Алматы қ.')))
        elif st[0] == 'price': stick.append(('price', ph['t0'] + 0.05, ph['t1'] + 0.6, None))
    # эмодзи: әр жаңа санат сегментінде (хуктан кейін, CTA дейін)
    emos, last = [], None
    for a, b, c, cat in segs:
        if cat and a >= hook_end - 0.1 and a < cta['t0'] - 0.2 and cat in EMOJI and EMOJI[cat] != last:
            emos.append((a, b, emoji_img(EMOJI[cat]))); last = EMOJI[cat]
    hook_emo = emoji_img(hk.get('emoji', '👀'), 120)
    grad, title, btn, addr = end_layers(lang)
    confetti = [(rnd.uniform(80, 1000), rnd.uniform(-300, 0), rnd.uniform(-160, 160), rnd.uniform(500, 1100),
                 rnd.choice([RED, YEL, (0, 170, 255), (60, 200, 90), (255, 120, 200)]), rnd.uniform(0, 6.28)) for _ in range(70)]
    bounds = [a for a, b, c, cat in segs][1:]
    seg_of = lambda t: next((k for k, (a, b, c, cat) in enumerate(segs) if a <= t < b), len(segs) - 1)

    def comp(fr, t):
        k = seg_of(t); a, b, c, cat = segs[k]; lt = t - a
        # Ken Burns + ауысу
        s = 1.0 + 0.07 * lt / max(0.5, b - a); dx = 0; rot = 0.0
        cy = 0.42 if k % 2 else 0.5
        if k > 0 and lt < 0.2 and not str(c).startswith('still'):
            u = lt / 0.2; tr = TRANS[k % len(TRANS)]
            if tr == 'punch': s *= 1 + 0.22 * (1 - ease(u))
            elif tr == 'whip': dx = (1 if k % 4 == 1 else -1) * W * 0.35 * (1 - ease(u))
            elif tr == 'spin': rot = 7 * (1 - ease(u)); s *= 1 + 0.12 * (1 - ease(u))
        if t < 0.35: s *= 1 + 0.25 * (1 - ease(t / 0.35))       # бірінші кадр — серпін
        fr = zoom(fr, s, 0.5, cy, dx, rot)
        if dx: fr = cv2.blur(fr, (int(10 + abs(dx) / 6), 1))
        fr = np.ascontiguousarray(fr)
        if k > 0 and lt < 0.12 and TRANS[k % len(TRANS)] == 'flash':
            al = 0.85 * (1 - lt / 0.12); fr[:] = (fr * (1 - al) + 255 * al).astype(np.uint8)
        # прогресс жолағы
        fr[0:10, :int(W * t / total)] = RED
        if t < hook_end:
            kw = nhw if t > phrases[0]['t1'] else max(1, min(nhw, int(1 + (t - phrases[0]['t0']) / hook_dur_words * nhw * 1.15)))
            im = hook_frame(hook_txt, kw)
            sc = back(t / 0.3) if t < 0.3 else 1.0
            if t > hook_end - 0.15: sc *= max(0, (hook_end - t) / 0.15)
            shake = 6 * math.sin(t * 40) * max(0, 1 - t / 0.4)
            paste(fr, im, W / 2 + shake, HOOK_Y, sc)
            eu = (t - 0.25) / 0.3
            if eu > 0: paste(fr, hook_emo, W / 2 + im.width / 2 - 30, HOOK_Y - im.height / 2 - 10, back(eu), rot=12 * math.sin(t * 5))
        for e0, e1, im in emos:
            if e0 <= t < e1 and t < cta['t0'] - 0.1:
                u = (t - e0) / 0.25; sc = back(u) * 0.75
                if e1 - t < 0.12: sc *= (e1 - t) / 0.12
                paste(fr, im, EMO_POS[0], EMO_POS[1] + 10 * math.sin(t * 4), sc, rot=8 * math.sin(t * 3))
        for kind, s0, s1, im in stick:
            s1 = min(s1, cta['t0'] - 0.05)
            if not (s0 <= t < s1): continue
            u = t - s0; out = max(0.0, min(1.0, (s1 - t) / 0.15))
            if kind == 'stat':
                paste(fr, im, W / 2, ST_Y, back(u / 0.3) * out, rot=-3 + 2.5 * math.sin(u * 5))
                for j, (ox, oy, ph0) in enumerate([(-300, -90, 0), (310, -70, 1.7), (-260, 110, 3.1), (290, 120, 4.4)]):
                    tw_ = 0.5 + 0.5 * math.sin(u * 7 + ph0)
                    if u > 0.2: paste(fr, STAR, W / 2 + ox, ST_Y + oy, (0.4 + 0.5 * tw_) * out)
            else:
                cnt = ease((u - 0.25) / 0.8); val = int(round((220000 - 80000 * cnt) / 1000)) * 1000
                im2 = price_card(lang, val, ease((u - 1.0) / 0.25))
                paste(fr, im2, W / 2, ST_Y - 30, back(u / 0.3) * out, rot=2 * math.sin(u * 4))
                cu = u - 1.05
                if 0 < cu < 1.6:
                    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
                    for x, y, vx, vy, col, r0 in confetti:
                        px = x + vx * cu; py = ST_Y - 250 + y + vy * cu * 0.6 + 600 * cu * cu
                        r = r0 + cu * 8; w_ = 14 * abs(math.cos(r)) + 3
                        dd.rectangle((px - w_, py - 7, px + w_, py + 7), fill=col + (255,))
                    fx.paste(fr, lay, W / 2, H / 2)
        if t >= cta['t0'] - 0.05:
            u = t - cta['t0'] + 0.05
            ga = np.asarray(grad).astype(np.float32); al = ga[..., 3:] / 255 * min(1, u / 0.3)
            fr[:] = (fr * (1 - al)).astype(np.uint8)
            if 'logo_sign' not in str(segs[-1][2]): paste(fr, title, W / 2, 1030 + 140 * (1 - ease(u / 0.45)), 1.0, alpha=min(1, u / 0.3))
            if u > 0.25:
                pul = 1 + 0.045 * math.sin((u - 0.25) * 2 * math.pi * 1.6)
                paste(fr, btn, W / 2, 1255, back((u - 0.25) / 0.35) * pul)
            if u > 0.55: paste(fr, addr, W / 2, 1400 + 60 * (1 - ease((u - 0.55) / 0.4)), 1.0, alpha=min(1, (u - 0.55) / 0.3))
            if u > 0.8:
                pt = emoji_img('👆', 70)
                paste(fr, pt, W / 2 + btn.width / 2 - 20, 1330 + 18 * abs(math.sin(u * 5)), back((u - 0.8) / 0.3) * 0.8)
        else:
            cd = next((c_ for c_ in cards if c_[0] <= t < c_[1]), None)
            if cd and t >= hook_end - 0.2:
                st, en, ws, wt = cd
                act = max([i for i, x in enumerate(wt) if x <= t + 0.03] or [0])
                im = sub_card(ws, act)
                paste(fr, im, W / 2, SUB_Y, 0.82 + 0.18 * back((t - st) / 0.16) if t - st < 0.16 else 1.0)
        return fr

    if test:
        for x in test:
            raw = subprocess.run([FF, '-v', 'error', '-ss', str(x), '-i', base, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
            Image.fromarray(comp(np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy(), x)).resize((540, 960)).save(P + f'test/v2_{cid}_{x:05.2f}.jpg', quality=85)
        return
    out = OUT + f'LULUPI_{cid}.mp4'
    dec = subprocess.Popen([FF, '-v', 'error', '-i', base, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    fs = W * H * 3; fi = 0
    while True:
        bb = dec.stdout.read(fs)
        if len(bb) < fs: break
        enc.stdin.write(comp(np.frombuffer(bb, np.uint8).reshape(H, W, 3).copy(), fi / FPS).tobytes()); fi += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    dst = READY + f'{lang.upper()}/{seg}/'; os.makedirs(dst, exist_ok=True)
    subprocess.run(['cp', out, dst])
    print(f'DONE {cid} {total:.1f}s -> {dst}', flush=True)

ALL = [(l, b, h) for l in ('ru', 'kk') for b in (1, 2, 3) for h in (1, 2, 3, 4, 5)]
if __name__ == '__main__':
    a = sys.argv[1:]
    test = [float(x) for x in a[a.index('--test') + 1:]] if '--test' in a else None
    if a[0] == 'all':
        part = int(a[1]) if len(a) > 2 else 0; nparts = int(a[2]) if len(a) > 2 else 1
        for i, (l, b, h) in enumerate(ALL): build(l, b, h, plan_only=(i % nparts != part))
    else:
        build(a[0], int(a[1]), int(a[2]), test)
