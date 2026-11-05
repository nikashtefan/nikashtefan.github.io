# -*- coding: utf-8 -*-
"""Блок «кейсы клиентов» на ainative.html: проблема → решение → было/стало + скрин работы.

Вставляется в готовый html между маркерами, а не через build.py: ainative.html правили руками
(цены «по запросу», трекинг), и полная пересборка их откатит (см. CLAUDE.md). Запуск повторяемый:
python3 _offers/client_cases.py
Имена клиентов под NDA. Скрины обезличены: КП с выдуманной шапкой и размытыми ценами,
отчёт по рекламе — настоящий, бренд и суммы заменены на •••.
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "ainative.html"
START, END = "<!-- client-cases:start -->", "<!-- client-cases:end -->"
SQUIGGLE = '<svg class="squiggle" viewBox="0 0 300 18" preserveAspectRatio="none" aria-hidden="true"><path d="M3 11 C40 4 70 16 105 9 C140 2 175 15 210 8 C240 3 270 13 297 7"/></svg>'
TG = "https://t.me/kvazarchIk?text=%D0%9F%D1%80%D0%B8%D0%B2%D0%B5%D1%82%21%20%D0%A5%D0%BE%D1%87%D1%83%20%D0%BF%D0%BE%D1%81%D0%BC%D0%BE%D1%82%D1%80%D0%B5%D1%82%D1%8C%20%D0%BA%D0%B5%D0%B9%D1%81%D1%8B"  # «Привет! Хочу посмотреть кейсы»

CASES = [
    {
        "tag": "монтаж систем связи · КП и расчёты",
        "h": "каждый объект считает только владелец",
        "problem": "Компания проектирует и монтирует усиление сотовой связи в зданиях. Клиент присылает план, владелец сам прикидывает в голове антенны и оборудование, рисует от руки и отдаёт проектировщику. КП, договоры и расчёты тоже на нём. Пока он один, рост упирается в его часы.",
        "solution": "AI-ассистент в Telegram. Владелец надиктовывает объект голосом, ассистент подбирает оборудование по его правилам комплектации, досчитывает кабель, разъёмы и делители, добавляет работы и присылает КП в PDF и спецификацию в Excel. Цены и оборудование правят прямо в ассистенте.",
        "was": "расчёт и КП живут у владельца в голове",
        "now": "КП приходит в чат готовым, владелец только проверяет",
        "img": "img/case-kp.png", "alt": "КП, которое собрал ассистент (данные компании скрыты)",
        "cap": "КП, которое собрал ассистент. Шапка и цены скрыты",
    },
    {
        "tag": "рекламное агентство · отчёты",
        "h": "почти 1 млн ₽ в месяц на рекламу, и непонятно, что работает",
        "problem": "У клиента агентства реклама в Директе и ВК. Мусорные площадки ловили руками через сессии в Метрике, ловилось плохо. Где бюджет работает, а где уходит в никуда, по кабинетам видно не было.",
        "solution": "Подключила Директ и ВК по API и разобрала трафик вместе с Метрикой. Отчёт за месяц собирается из кабинетов: где теряются деньги и что поменять, с цифрами.",
        "was": "мусор искали руками, по ощущениям",
        "now": "РСЯ оказалась чистой, на мусор 0,7%. А ВК был настроен на дешёвые клики вместо охвата: 900 тыс. ₽ за 7 месяцев, тысяча показов в 4,5 раза дороже, чем в РСЯ",
        "img": "img/case-ads.png", "alt": "Отчёт клиенту за октябрь (бренд и суммы скрыты)",
        "cap": "Настоящий отчёт клиенту за октябрь. Бренд и суммы скрыты",
    },
    {
        "tag": "оформление исполнителей · документы",
        "h": "договор с самозанятым ждут по 3–4 часа",
        "problem": "Компания оформляет самозанятых и ИП для брендов на маркетплейсах. На каждый договор HR-партнёр запрашивает паспорт, СНИЛС, ИНН и реквизиты, вписывает всё в шаблон, руководитель проверяет. Договор ждут 3–4 часа.",
        "solution": "Бот в Telegram. Руководитель создаёт договор, исполнитель по ссылке присылает фото документов. AI их читает, формулы проверяют ИНН, СНИЛС и счёт, недостающее бот просит сам. Готовый договор приходит в шаблоне компании.",
        "was": "3–4 часа ожидания HR на каждый договор",
        "now": "договор собирается, пока исполнитель присылает фото. Остаётся одна кнопка «на подпись»",
        "img": "img/case-contracts.png", "alt": "Схема, как идёт договор в боте",
        "cap": "Как идёт договор: кто что делает",
    },
]

CSS = """<style>
.cc{display:grid;gap:28px}
.cc-case{border:2px solid var(--ink);background:var(--paper);display:grid;grid-template-columns:1.05fr .95fr}
.cc-text{padding:30px 30px 32px;display:flex;flex-direction:column;gap:14px}
.cc-text h3{font-family:"Unbounded",sans-serif;font-weight:700;font-size:22px;line-height:1.2;text-transform:lowercase;margin:0}
.cc-l{font-family:"Oswald",sans-serif;font-weight:600;font-size:12px;letter-spacing:.14em;text-transform:uppercase;opacity:.6;margin-bottom:4px}
.cc-text p{margin:0;font-size:16px;line-height:1.5}
.cc-ba{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:4px}
.cc-ba>div{padding:14px 16px;border:1.5px solid var(--ink)}
.cc-ba>.now{background:var(--red);color:#fff;border-color:var(--red)}
.cc-ba .now .cc-l{opacity:.85}
.cc-shot{border-left:2px solid var(--ink);background:#fff;display:flex;flex-direction:column;justify-content:space-between;margin:0}
.cc-shot img{width:100%;height:auto;display:block}
.cc-shot figcaption{font-size:13px;opacity:.65;padding:10px 14px;border-top:1px solid rgba(0,0,0,.12)}
.cc-cta{margin-top:30px;display:flex;flex-wrap:wrap;align-items:center;gap:18px}
.cc-cta p{margin:0;font-size:17px}
@media(max-width:820px){.cc-case{grid-template-columns:1fr}.cc-shot{border-left:none;border-top:2px solid var(--ink)}.cc-ba{grid-template-columns:1fr}.cc-text{padding:22px 18px}}
</style>"""


def section():
    cards = "".join(
        f'<article class="cc-case reveal"><div class="cc-text"><span class="term">{c["tag"]}</span><h3>{c["h"]}</h3>'
        f'<div><div class="cc-l">проблема</div><p>{c["problem"]}</p></div>'
        f'<div><div class="cc-l">что сделала</div><p>{c["solution"]}</p></div>'
        f'<div class="cc-ba"><div><div class="cc-l">было</div><p>{c["was"]}</p></div>'
        f'<div class="now"><div class="cc-l">стало</div><p>{c["now"]}</p></div></div></div>'
        f'<figure class="cc-shot"><img src="{c["img"]}" alt="{c["alt"]}" loading="lazy"><figcaption>{c["cap"]}</figcaption></figure></article>'
        for c in CASES
    )
    return f"""{START}
{CSS}
<section id="clients">
  <div class="wrap">
    <div class="corners"><span class="mark">кейсы клиентов</span><span class="mid mark">проблема → решение → результат</span><span class="mark right">CASES</span></div>
    <h2 class="section-h reveal" style="margin-bottom:58px">узнаёте свою задачу?{SQUIGGLE}</h2>
    <p class="works-note reveal">Это мои клиенты. Названия компаний под NDA, суммы на скринах скрыты. Каждый кейс подробно, с живой работой, показываю на созвоне.</p>
    <div class="cc">{cards}</div>
    <div class="cc-cta reveal"><p>Хотите посмотреть вживую или похожая задача у вас?</p><a class="btn" href="{TG}" target="_blank" rel="noopener">покажу на созвоне</a></div>
  </div>
</section>
{END}
"""


html = PAGE.read_text(encoding="utf-8")
html = re.sub(re.escape(START) + ".*?" + re.escape(END) + "\n?", "", html, flags=re.S)
anchor = '<section id="works">'
assert anchor in html, "не нашёл блок works"
PAGE.write_text(html.replace(anchor, section() + anchor, 1), encoding="utf-8")
print("ok", PAGE)
