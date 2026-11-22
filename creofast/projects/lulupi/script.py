# LULUPI KIDS — 30 креатив: 6 body (RU1-3, KZ1-3) × 5 хук.
# Әр фраза: (экрандағы мәтін, B-roll санаттары, стикер|None)
# Стикер: ('stat', үлкен, кіші) | ('price',) | ('addr',)

FACTS = dict(addr_ru='г. Алматы, мкр. Мамыр-4, 156', addr_kk='Алматы қ., Мамыр-4 ш/а, 156')

HOOKS = {
 'ru': {
  1: dict(screen='ВОТ ЧЕМ ЗАНЯТ РЕБЁНОК, ПОКА ВЫ НА РАБОТЕ', say='Вот чем занят ребёнок, пока вы на работе.', cats=['montessori', 'ballet', 'taekwondo', 'dance', 'food', 'outdoor'], emoji='👀', seg='01_пока_вы_на_работе'),
  2: dict(screen='ПОЧЕМУ МАМЫ МАМЫР-4 ВЫБИРАЮТ ЭТОТ САД?', say='Почему мамы Мамыр-4 выбирают этот сад?', cats=['happy', 'building', 'happy', 'ballet', 'play'], emoji='🤔', seg='02_почему_выбирают'),
  3: dict(screen='ПРЕМИУМ-САД ЗА 140 000 ₸? ДА, С ВАУЧЕРОМ', say='Премиум-сад за 140 000 ₸? Да, с ваучером!', cats=['happy', 'ballet', 'montessori', 'taekwondo', 'happy'], emoji='😱', seg='03_цена_ваучер'),
  4: dict(screen='БАЛЕТ, ТХЭКВОНДО И АНГЛИЙСКИЙ — БЕЗ ДОПЛАТ', say='Балет, тхэквондо и английский — без доплат!', cats=['ballet', 'taekwondo', 'english', 'ballet', 'taekwondo'], emoji='🔥', seg='04_без_доплат'),
  5: dict(screen='ОДИН ДЕНЬ ИЗ ЖИЗНИ LULUPI KIDS', say='Один день из жизни LULUPI KIDS. Смотрите до конца!', cats=['happy', 'food', 'montessori', 'dance', 'outdoor', 'ballet'], emoji='☀️', seg='05_один_день'),
 },
 'kk': {
  1: dict(screen='СІЗ ЖҰМЫСТА ЖҮРГЕНДЕ БАЛАҢЫЗ НЕ ІСТЕЙДІ?', say='Сіз жұмыста жүргенде балаңыз не істейді?', cats=['montessori', 'ballet', 'taekwondo', 'dance', 'food', 'outdoor'], emoji='👀', seg='01_сіз_жұмыстасыз'),
  2: dict(screen='МАМЫР-4 АНАЛАРЫ НЕГЕ ОСЫ БАЛАБАҚШАНЫ ТАҢДАЙДЫ?', say='Мамыр-4 аналары неге осы балабақшаны таңдайды?', cats=['happy', 'building', 'happy', 'ballet', 'play'], emoji='🤔', seg='02_неге_таңдайды'),
  3: dict(screen='ПРЕМИУМ БАЛАБАҚША 140 000 ₸? ИӘ, ВАУЧЕРМЕН', say='Премиум балабақша 140 000 ₸? Иә, ваучермен!', cats=['happy', 'ballet', 'montessori', 'taekwondo', 'happy'], emoji='😱', seg='03_баға_ваучер'),
  4: dict(screen='БАЛЕТ, ТХЭКВОНДО, АҒЫЛШЫН — ҚОСЫМША ТӨЛЕМСІЗ', say='Балет, тхэквондо және ағылшын тілі — қосымша төлемсіз!', cats=['ballet', 'taekwondo', 'english', 'ballet', 'taekwondo'], emoji='🔥', seg='04_қосымша_төлемсіз'),
  5: dict(screen='LULUPI KIDS-ТЕГІ БІР КҮН', say='LULUPI KIDS-тегі бір күн. Соңына дейін көріңіз!', cats=['happy', 'food', 'montessori', 'dance', 'outdoor', 'ballet'], emoji='☀️', seg='05_бір_күн'),
 },
}

BODY = {
 ('ru', 1): [
  ('В LULUPI KIDS сочетаются Montessori и традиционные занятия.', ['montessori', 'class'], None),
  ('Дети учатся, играют и постепенно становятся самостоятельнее.', ['learn', 'play', 'selfserve'], None),
  ('Есть группы QADAM, JUNIOR и SENIOR,', ['toddlers', 'groups', 'seniors'], None),
  ('обучение — на русском или казахском.', ['class', 'kazakh'], ('stat', 'RU / KZ', 'язык обучения')),
  ('Детей ждёт пятиразовое питание', ['food', 'food'], ('stat', '5 раз', 'питание в день')),
  ('и насыщенный день с 8:00 до 18:00.', ['dance', 'outdoor', 'taekwondo'], ('stat', '8:00–18:00', 'насыщенный день')),
 ],
 ('ru', 2): [
  ('Здесь каждый день наполнен понятными детям занятиями,', ['montessori', 'learn'], None),
  ('свободной игрой', ['play'], None),
  ('и общением с педагогами.', ['teacher'], None),
  ('Пятиразовое питание,', ['food'], ('stat', '5 раз', 'питание в день')),
  ('русский или казахский язык', ['class'], ('stat', 'RU / KZ', 'язык обучения')),
  ('и группы по возрасту —', ['groups'], None),
  ('в LULUPI KIDS в микрорайоне Мамыр-4.', ['building'], ('addr',)),
 ],
 ('ru', 3): [
  ('От QADAM для малышей до SENIOR перед школой —', ['toddlers', 'seniors'], None),
  ('подбираем группу по возрасту ребёнка.', ['groups'], None),
  ('Montessori-подход сочетается с традиционными занятиями,', ['montessori', 'class'], None),
  ('а день включает питание, игру,', ['food', 'play'], None),
  ('прогулки и занятия с педагогами.', ['outdoor', 'teacher'], None),
 ],
 ('kk', 1): [
  ('LULUPI KIDS-те Montessori мен дәстүрлі сабақтар үйлеседі.', ['montessori', 'class'], None),
  ('Балалар ойнап, білім алып,', ['play', 'learn'], None),
  ('біртіндеп өз бетінше әрекет етуге үйренеді.', ['selfserve', 'montessori'], None),
  ('QADAM, JUNIOR және SENIOR топтары бар,', ['toddlers', 'groups', 'seniors'], None),
  ('оқу орыс және қазақ тілдерінде жүргізіледі.', ['kazakh', 'class'], ('stat', 'KZ / RU', 'оқу тілі')),
  ('Балалар күніне бес рет тамақтанады,', ['food', 'food'], ('stat', '5 рет', 'күніне тамақ')),
  ('балабақша 8:00-ден 18:00-ге дейін жұмыс істейді.', ['dance', 'outdoor', 'taekwondo'], ('stat', '8:00–18:00', 'жұмыс уақыты')),
 ],
 ('kk', 2): [
  ('Мұнда күн сайын балаларға арналған сабақтар,', ['montessori', 'learn'], None),
  ('еркін ойын', ['play'], None),
  ('және педагогтермен қарым-қатынас бар.', ['teacher'], None),
  ('Күніне бес рет тамақтану,', ['food'], ('stat', '5 рет', 'күніне тамақ')),
  ('қазақ немесе орыс тілі,', ['kazakh'], ('stat', 'KZ / RU', 'оқу тілі')),
  ('жас ерекшелігіне сай топтар —', ['groups'], None),
  ('бәрі Мамыр-4 шағынауданындағы LULUPI KIDS-те.', ['building'], ('addr',)),
 ],
 ('kk', 3): [
  ('Кішкентайларға арналған QADAM тобынан', ['toddlers'], None),
  ('мектепалды SENIOR тобына дейін —', ['seniors'], None),
  ('баланың жасына сай топ бар.', ['groups'], None),
  ('Montessori тәсілі дәстүрлі сабақтармен ұштасады,', ['montessori', 'class'], None),
  ('ал күн тәртібінде тамақтану, ойын,', ['food', 'play'], None),
  ('серуен және педагогтермен сабақтар бар.', ['outdoor', 'teacher'], None),
 ],
}

EXTRAS = {
 'ru': ('Английский, тхэквондо, балет, танцы и йога — уже в стоимости.', ['english', 'taekwondo', 'ballet', 'dance', 'yoga'], None),
 'kk': ('Ағылшын тілі, тхэквондо, балет, би және йога бағасына кіреді.', ['english', 'taekwondo', 'ballet', 'dance', 'yoga'], None),
}
PRICE = {
 'ru': ('220 000 ₸ в месяц, а с ваучером — 140 000 ₸.', ['happy', 'ballet'], ('price',)),
 'kk': ('Айына 220 000 ₸, ваучермен — 140 000 ₸.', ['happy', 'ballet'], ('price',)),
}
CTA = {
 'ru': ('Запишитесь на экскурсию в LULUPI KIDS!', ['endcard'], None),
 'kk': ('LULUPI KIDS-ке экскурсияға жазылыңыз!', ['endcard'], None),
}

# TTS айтылуы (экрандағы мәтін өзгермейді)
SAY = {
 'ru': [('LULUPI KIDS', 'Лулупи Кидс'), ('Montessori-подход', 'Монтессори-подход'), ('Montessori', 'Монтессори'),
        ('QADAM', 'Кадам'), ('JUNIOR', 'Джуниор'), ('SENIOR', 'Сеньор'), ('с 8:00 до 18:00', 'с восьми утра до шести вечера'),
        ('Мамыр-4', 'Мамыр-четыре'), ('220 000 ₸', 'двести двадцать тысяч тенге'), ('140 000 ₸', 'сто сорок тысяч тенге'),
        ('тхэквондо', 'таэквондо')],
 'kk': [('LULUPI KIDS-тегі', 'Лулупи Кидстегі'), ('LULUPI KIDS-те', 'Лулупи Кидсте'), ('LULUPI KIDS-ке', 'Лулупи Кидске'), ('LULUPI KIDS', 'Лулупи Кидс'),
        ('Montessori', 'Монтессори'), ('QADAM', 'Қадам'), ('JUNIOR', 'Джуниор'), ('SENIOR', 'Сениор'),
        ('8:00-ден 18:00-ге', 'таңғы сегізден кешкі алтыға'), ('Мамыр-4-тен', 'Мамыр-төрттен'), ('Мамыр-4', 'Мамыр-төрт'),
        ('220 000 ₸', 'екі жүз жиырма мың теңге'), ('140 000 ₸', 'жүз қырық мың теңге'), ('тхэквондо', 'таэквондо'), ('бес рет', 'бес рет')],
}

KEYS = ['LULUPI', 'Montessori', 'QADAM', 'JUNIOR', 'SENIOR', 'пятиразовое', 'бес', '8:00', '220', '140', 'ваучер',
        'Мамыр-4', 'английский', 'ағылшын', 'тхэквондо', 'балет', 'экскурси', 'самостоятель', 'бетінше', 'игр', 'ойын', 'педагог']

def creative(lang, body, hook):
    """Толық фразалар тізімі: хук + body + (доп.сабақтар) + баға + CTA."""
    h = HOOKS[lang][hook]
    ph = [dict(text=h['say'], screen_hook=h['screen'], cats=h['cats'], st=None, hook=True)]
    for t, c, s in BODY[(lang, body)]: ph.append(dict(text=t, cats=c, st=s))
    if hook != 4:
        t, c, s = EXTRAS[lang]; ph.append(dict(text=t, cats=c, st=s))
    t, c, s = PRICE[lang]; ph.append(dict(text=t, cats=c, st=s))
    t, c, s = CTA[lang]; ph.append(dict(text=t, cats=c, st=s, cta=True))
    return ph, h['seg']
