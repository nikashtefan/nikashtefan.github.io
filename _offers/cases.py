# -*- coding: utf-8 -*-
"""ainative.html: один блок «кейсы» сразу после первого экрана + поправка прокрутки по меню.

Что делает (запуск повторяемый: python3 _offers/cases.py):
1. Из скринов в case_src/ собирает обложки img/cover-*.jpg одного формата: 4:3, один фон,
   скрин в окне браузера. Разные по размеру скрины так выглядят одной серией.
2. Заменяет старые блоки «примеры» (#examples), «кейсы клиентов» (#clients) и «что я уже собрала» (#works)
   одним блоком #examples: клиенты под NDA + мои проекты в одной ленте.
3. Меню: прокрутка к заголовку блока под шапкой, а не к верху секции (у секций 150px отступа и волна).

Почему не через build.py: ainative.html правили руками (цены «по запросу», трекинг), полная
пересборка их откатит (см. CLAUDE.md).
Скрины клиентов обезличены: КП — выдуманная шапка, оборудование кодами (A1, B1…), цены •••;
отчёт по рекламе настоящий, бренд и суммы заменены на •••.
"""
import pathlib, re
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(__file__).resolve().parent / "case_src"
PAGE = ROOT / "ainative.html"

BG = (240, 227, 231)        # светлый тон акцента страницы #8a0f3c
W, H = 1200, 900
WIN_X, WIN_Y, WIN_W = 90, 90, 1020
BAR = 46

# id, файл, кроп исходника (None = целиком), фон под скрином внутри окна
COVERS = [
    ("kp", "kp.png", (40, 40, 1150, 1060), (255, 255, 255)),
    ("ads", "report.png", None, (243, 244, 249)),
    ("contracts", "contracts.png", (50, 180, 725, 530), (243, 235, 227)),
    ("litbot", "litbot-admin.png", None, (255, 255, 255)),
    ("content", "content-factory.png", (380, 0, 1290, 700), (255, 255, 255)),
    ("models", "models-hub.png", None, (255, 255, 255)),
]

# телефон поверх окна: второй экран того же кейса (файл, кроп исходника)
PHONES = {"ads": ("report-bot.png", (0, 10, 754, 1190)),
          "kp": ("kp-chat.png", (0, 120, 752, 1240)),
          "contracts": ("contracts-chat.png", (0, 100, 770, 1480)),
          "litbot": ("litbot-chat.jpg", (0, 90, 780, 1480))}
PH_W, PH_X, PH_Y = 330, 800, 250


def phone(canvas, fname, crop, w=PH_W, x=PH_X, y=PH_Y):
    PH_W, PH_X, PH_Y = w, x, y
    shot = Image.open(SRC / fname).convert("RGB").crop(crop)
    shot = shot.resize((PH_W, round(shot.height * PH_W / shot.width)), Image.LANCZOS)
    b = 12                                       # рамка телефона
    pw, ph = PH_W + 2 * b, min(shot.height, H - PH_Y + 40) + 2 * b
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle((PH_X, PH_Y + 16, PH_X + pw, PH_Y + ph), 40, fill=110)
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    canvas.paste(Image.new("RGB", (W, H), (60, 15, 35)), (0, 0), shadow)
    body = Image.new("RGB", (pw, ph), (24, 26, 32))
    inner = Image.new("L", shot.size, 0)
    ImageDraw.Draw(inner).rounded_rectangle((0, 0, shot.width, shot.height), 28, fill=255)
    body.paste(shot.crop((0, 0, PH_W, ph - 2 * b)), (b, b), inner.crop((0, 0, PH_W, ph - 2 * b)))
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw, ph), 40, fill=255)
    canvas.paste(body, (PH_X, PH_Y), mask)


# обложка только из телефонов (кейсы, где весь продукт живёт в Telegram)
DUOS = {"assistant": [("assistant-1.png", (0, 190, 662, 1432), 420, 140, 60),
                      ("assistant-2.png", (0, 660, 736, 1470), 440, 610, 300)],
        "english": [("english.jpg", (0, 100, 786, 1470), 470, 365, 60)]}


def duo(name):
    canvas = Image.new("RGB", (W, H), BG)
    for args in DUOS[name]:
        phone(canvas, *args)
    canvas.save(ROOT / "img" / f"cover-{name}.jpg", quality=86, optimize=True, progressive=True)


def cover(name, fname, crop, inner_bg):
    shot = Image.open(SRC / fname).convert("RGB")
    if crop:
        shot = shot.crop(crop)
    shot = shot.resize((WIN_W, round(shot.height * WIN_W / shot.width)), Image.LANCZOS)
    win_h = H - WIN_Y + 40                       # окно уходит за нижний край: так обложки выглядят как серия
    canvas = Image.new("RGB", (W, H), BG)
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle((WIN_X, WIN_Y + 14, WIN_X + WIN_W, WIN_Y + win_h), 22, fill=70)
    shadow = shadow.filter(ImageFilter.GaussianBlur(26))
    canvas.paste(Image.new("RGB", (W, H), (90, 20, 45)), (0, 0), shadow)
    win = Image.new("RGB", (WIN_W, win_h), inner_bg)
    d = ImageDraw.Draw(win)
    d.rectangle((0, 0, WIN_W, BAR), fill=(255, 255, 255))
    for i, c in enumerate([(236, 106, 94), (244, 191, 79), (97, 197, 84)]):
        d.ellipse((20 + i * 24, 16, 34 + i * 24, 30), fill=c)
    d.line((0, BAR, WIN_W, BAR), fill=(228, 220, 222), width=2)
    win.paste(shot.crop((0, 0, WIN_W, min(shot.height, win_h - BAR))), (0, BAR + 1))
    mask = Image.new("L", (WIN_W, win_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, WIN_W, win_h), 22, fill=255)
    canvas.paste(win, (WIN_X, WIN_Y), mask)
    if name in PHONES:
        phone(canvas, *PHONES[name])
    out = ROOT / "img" / f"cover-{name}.jpg"
    canvas.save(out, quality=86, optimize=True, progressive=True)


CASES = [  # (обложка, кто, тег, продукт, проблема, что сделала, было, стало, ссылка)
    ("kp", "клиент · nda", "кп и расчёты", "AI-ассистент для КП и смет",
     "Каждый объект считает владелец, поэтому проект готов только на следующий день. Взять больше объектов компания не может.",
     "Владелец надиктовывает объект, а ассистент присылает КП и спецификацию.",
     "1–2 дня, и всё через владельца", "2 минуты, владелец только проверяет", ""),
    ("ads", "клиент · nda", "реклама", "AI-автоотчёт по рекламным кампаниям",
     "На рекламу уходит почти 1 млн ₽ в месяц, а какие деньги сгорают, никто не знает.",
     "Отчёт сам собирается из Директа и ВК, показывает утечки, а агент предлагает решения.",
     "мусор ловили руками в Метрике", "нашли 900 тыс. ₽: ВК покупал клики вместо охвата", ""),
    ("contracts", "клиент · nda", "документы", "AI-ассистент для договоров с самозанятыми",
     "На каждого исполнителя HR руками переносит паспорт и реквизиты, договор ждут 3–4 часа.",
     "Исполнитель присылает фото документов, а AI сам проверяет данные и собирает договор.",
     "3–4 часа на договор", "10 минут, остаётся нажать «на подпись»", ""),
    ("assistant", "мой проект", "ai-ассистент", "Личный AI-ассистент",
     "Договорённости с клиентами раскиданы по чатам и созвонам, и что кому обещала, приходится держать в голове.",
     "Ассистент сам читает переписку и встречи, ведёт карточки клиентов и пишет в Telegram: кто что обещал и кто молчит.",
     "обещания и встречи в голове", "сводка 4 раза в день, новый человек сразу в базе", ""),
    ("english", "мой проект", "обучение", "AI-тренер английского",
     "После урока новые слова и правила забываются, а повторять самой некогда.",
     "Кидаешь скрин урока, бот за минуту разбирает правило и кладёт новые слова в колоду. Несколько раз в день присылает мини-упражнения на слабые места.",
     "конспект урока руками", "разбор за минуту, повтор сам по расписанию", ""),
    ("litbot", "мой проект", "обучение", "Бот-ассистент учителя",
     "Учитель сам рассылает задания и считает, кто что сделал.",
     "Бот каждый день присылает задания и сам ведёт статистику, программу учитель меняет в админке.",
     "рассылка и учёт руками", "учитель только смотрит итоги", ""),
    ("content", "мой проект", "контент", "Контент-фабрика",
     "На посты по одному выпуску подкаста уходил целый день.",
     "Из одного выпуска получаются превью, главы и 7 постов в голосе автора.",
     "1 день на выпуск", "30 минут, 7 публикаций", "content.html"),
    ("models", "мой проект", "расчёты", "Хаб расчётных моделей",
     "Каждое «а если поднять цену» приходилось пересчитывать в таблице заново.",
     "9 моделей: юнит-экономика, окупаемость, воронки. Меняешь цифру и сразу видишь результат.",
     "пересчёт на каждый вопрос", "цену выбираешь по цифрам", "models-hub/"),
]

SQUIGGLE = '<svg class="squiggle" viewBox="0 0 300 18" preserveAspectRatio="none" aria-hidden="true"><path d="M3 11 C40 4 70 16 105 9 C140 2 175 15 210 8 C240 3 270 13 297 7"/></svg>'
TG = "https://t.me/kvazarchIk?text=%D0%9F%D1%80%D0%B8%D0%B2%D0%B5%D1%82%21%20%D0%A5%D0%BE%D1%87%D1%83%20%D0%BF%D0%BE%D1%81%D0%BC%D0%BE%D1%82%D1%80%D0%B5%D1%82%D1%8C%20%D0%BA%D0%B5%D0%B9%D1%81%D1%8B"  # «Привет! Хочу посмотреть кейсы»

CSS = """<style>
.kc{flex:0 0 min(360px,84vw);scroll-snap-align:start;border:2px solid var(--ink);background:var(--paper);display:flex;flex-direction:column}
.kc img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;border-bottom:2px solid var(--ink)}
.kc-b{padding:18px 20px 20px;display:flex;flex-direction:column;gap:10px;flex:1}
.kc-t{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.kc-who{font-family:"Oswald",sans-serif;font-weight:600;font-size:11px;letter-spacing:.12em;text-transform:uppercase;padding:3px 8px;background:var(--ink);color:#fff}
.kc-who.own{background:transparent;color:var(--ink);box-shadow:inset 0 0 0 1.5px var(--ink)}
.kc h3{font-family:"Unbounded",sans-serif;font-weight:700;font-size:18px;line-height:1.22;text-transform:lowercase;margin:2px 0 0;min-height:3.66em}
.kc .kc-pr{font-weight:600;min-height:5.8em}
.kc-go{font-family:"Oswald",sans-serif;font-weight:600;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--red);text-decoration:none}
.kc p{margin:0;font-size:14.5px;line-height:1.45}
.kc-ba{margin-top:auto;padding-top:12px;border-top:1.5px solid var(--line);display:grid;gap:6px;font-size:14px;line-height:1.35}
.kc-ba span{font-family:"Oswald",sans-serif;font-weight:600;font-size:11px;letter-spacing:.12em;text-transform:uppercase;margin-right:6px}
.kc-ba .was{opacity:.65}
.kc-ba .now{color:var(--red);font-weight:600}
.kc-cta{margin-top:26px;display:flex;flex-wrap:wrap;align-items:center;gap:16px}
.kc-cta p{margin:0;font-size:16px;opacity:.8}
</style>"""


def ver(c):
    # GitHub Pages кэширует картинки на 10 минут: без версии в ссылке браузер показывает старую обложку
    import hashlib
    return hashlib.md5((ROOT / "img" / f"cover-{c}.jpg").read_bytes()).hexdigest()[:8]


def section():
    cards = "".join(
        f'<article class="kc cs"><img src="img/cover-{c}.jpg?v={ver(c)}" alt="" loading="lazy" width="1200" height="900">'
        f'<div class="kc-b"><div class="kc-t"><span class="kc-who{"" if who.startswith("клиент") else " own"}">{who}</span><span class="term">{tag}</span></div>'
        f'<h3>{prod}</h3><p class="kc-pr">{prob}</p><p>{what}</p>'
        + (f'<a class="kc-go" href="{link}" target="_blank" rel="noopener">посмотреть вживую →</a>' if link else "") +
        f'<div class="kc-ba"><div class="was"><span>было</span>{was}</div><div class="now"><span>стало</span>{now}</div></div></div></article>'
        for c, who, tag, prod, prob, what, was, now, link in CASES
    )
    return f"""<section id="examples">
  <div class="wrap">
    <div class="corners"><span class="mark">кейсы</span><span class="mid mark">проблема → решение → результат</span><span class="mark right">CASES</span></div>
    <h2 class="section-h reveal" style="margin-bottom:58px">узнаёте свою задачу?{SQUIGGLE}</h2>
    <p class="works-note reveal">Первые три — мои клиенты, названия под NDA, суммы на скринах скрыты. Дальше мои собственные проекты. Каждый кейс показываю вживую на созвоне.</p>
    {CSS}
    <div class="cs-wrap reveal"><div class="cs-row">{cards}</div><div class="cs-nav"><button type="button" class="cs-btn" data-d="-1" aria-label="Назад">←</button><span class="mark">листай вбок</span><button type="button" class="cs-btn" data-d="1" aria-label="Вперёд">→</button></div></div>
    <div class="kc-cta reveal"><p>Похожая задача у вас?</p><a class="btn" href="{TG}" target="_blank" rel="noopener">покажу кейсы на созвоне</a></div>
  </div>
</section>
"""


# Меню: прокручиваем так, чтобы заголовок блока (.corners) встал под шапку, и подсветку считаем по нему же
NAV_JS = """<script>/* nav-scroll-fix */
(function(){
  var nav=document.querySelector('nav');
  function head(s){return s.querySelector('.corners')||s;}
  function go(id,smooth){var s=document.getElementById(id);if(!s)return;
    var y=head(s).getBoundingClientRect().top+window.scrollY-(nav?nav.offsetHeight:0)-28;
    window.scrollTo({top:Math.max(0,y),behavior:smooth?'smooth':'auto'});}
  document.querySelectorAll('a[href^="#"]').forEach(function(a){a.addEventListener('click',function(e){
    var id=a.getAttribute('href').slice(1);if(!id||!document.getElementById(id))return;
    e.preventDefault();history.replaceState(null,'','#'+id);go(id,true);});});
  if(location.hash)window.addEventListener('load',function(){go(location.hash.slice(1),false);});
})();
</script>"""


def section_bounds(html, sid):
    a = html.find(f'<section id="{sid}"')
    if a < 0:
        return None
    b = html.find("</section>", a) + len("</section>")
    return a, b


for args in COVERS:
    cover(*args)
for name in DUOS:
    duo(name)

html = PAGE.read_text(encoding="utf-8")
# старые блоки: прошлая версия кейсов (между маркерами), #works и #examples
html = re.sub(r"<!-- client-cases:start -->.*?<!-- client-cases:end -->\n?", "", html, flags=re.S)
for sid in ("works", "clients"):
    bnd = section_bounds(html, sid)
    if bnd:
        html = html[:bnd[0]] + html[bnd[1]:].lstrip("\n")
a, b = section_bounds(html, "examples")
html = html[:a] + section().rstrip("\n") + html[b:]
# пункты меню: один «кейсы» вместо «примеры» + «кейсы»
html = html.replace('<a href="#examples">примеры</a>', '<a href="#examples">кейсы</a>', 1)
html = html.replace('<a href="#works">кейсы</a>', "", 1)
# старая подсветка мерила верх секции — меряем заголовок
html = html.replace("var t = p[1].getBoundingClientRect().top;",
                    "var t = (p[1].querySelector('.corners')||p[1]).getBoundingClientRect().top;", 1)
html = html.replace("var line = 140,", "var line = (document.querySelector('nav')||{offsetHeight:90}).offsetHeight + 60,", 1)
if "nav-scroll-fix" not in html:
    html = html.replace("</body>", NAV_JS + "\n</body>", 1)
PAGE.write_text(html, encoding="utf-8")
print("ok")
