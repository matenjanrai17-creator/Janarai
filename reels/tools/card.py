from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
S=sys.argv[1]; F="/usr/share/fonts/opentype/inter/"
W,H=1080,1920; BURG=(122,30,43)
def font(n,s): return ImageFont.truetype(F+n,s)
bg=Image.open(f"{S}/img/C0C949C1.jpg").convert("RGB")
r=max(W/bg.width,H/bg.height); bg=bg.resize((int(bg.width*r)+1,int(bg.height*r)+1))
bg=bg.crop(((bg.width-W)//2,(bg.height-H)//2,(bg.width-W)//2+W,(bg.height-H)//2+H)).filter(ImageFilter.GaussianBlur(18))
ov=Image.new("RGB",(W,H),BURG); base=Image.blend(bg,ov,0.86)
TXT={
 "ru":dict(cta="Запишитесь на экскурсию",wa="WhatsApp",city="г. Алматы",addr="мкр. Мамыр-4, дом 156",hours="08:00–18:00 · Montessori + традиционные занятия"),
 "kz":dict(cta="Экскурсияға жазылыңыз",wa="WhatsApp",city="Алматы қ.",addr="Мамыр-4 ш/а, 156 үй",hours="08:00–18:00 · Montessori + дәстүрлі сабақтар"),
}
for lang,t in TXT.items():
    im=base.copy(); d=ImageDraw.Draw(im)
    def ctext(y,s,f,fill=(255,255,255)):
        w=d.textlength(s,font=f); d.text(((W-w)/2,y),s,font=f,fill=fill)
    ctext(470,"LULUPI KIDS",font("InterDisplay-Bold.otf",118))
    ctext(612,"PREMIUM MONTESSORI",font("Inter-Medium.otf",40),(236,214,218))
    d.line([(W/2-90,700),(W/2+90,700)],fill=(255,255,255),width=3)
    ctext(760,t["cta"],font("Inter-SemiBold.otf",58))
    # WhatsApp pill
    pf=font("InterDisplay-Bold.otf",76); num="+7 706 504 4885"
    nw=d.textlength(num,font=pf); px=(W-nw)/2-50; py=870
    d.rounded_rectangle([px,py,px+nw+100,py+190],radius=40,fill=(255,255,255))
    lf=font("Inter-Medium.otf",36); lw=d.textlength(t["wa"],font=lf)
    d.text(((W-lw)/2,py+22),t["wa"],font=lf,fill=(90,90,90))
    d.text(((W-nw)/2,py+72),num,font=pf,fill=BURG)
    ctext(1120,t["city"],font("Inter-Medium.otf",44),(236,214,218))
    ctext(1180,t["addr"],font("Inter-SemiBold.otf",56))
    ctext(1290,t["hours"],font("Inter-Regular.otf",32),(226,200,205))
    im.save(f"{S}/build/card_{lang}.png")
