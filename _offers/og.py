"""Генератор обложек для превью ссылок (og:image), 1200×630.

Зачем: при пересылке ссылки в Telegram подтягивалось фото из hero — это личное фото,
а нужна фирменная карточка с названием услуги. Запуск: python3 _offers/og.py
(нужен Chrome; карточки кладутся в img/og-<slug>.png).
"""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build import OFFERS, ROOT  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP = Path("/tmp/og-cards")

# что писать на карточке: крупная строка + строка-результат
CARDS = {
    "audit": ("AI-оптимизация процессов", "заявки, отчёты, ответы клиентам — без ручной работы", "аудит от 9 900 ₽"),
    "session": ("Сессия по вайбкодингу", "за 1,5 часа собираем твой рабочий AI-инструмент", "6 000 ₽"),
    "bot": ("Бот-курс для преподавателя", "задания ученикам каждый день и статистика для вас", "от 50 000 ₽"),
    "workshop": ("Воркшоп Claude Code", "за день команда собирает 4 инструмента на своих задачах", "от 25 000 ₽"),
    "content": ("Контент-конвейер", "из одного эфира — 7 публикаций в вашем голосе", "от 12 000 ₽"),
    "digest": ("AI-дайджест", "агент читает рынок за вас и присылает 5–10 событий", "от 10 000 ₽"),
    "ainative": ("Команда и процессы", "6 недель: команда переходит на AI и не откатывается", "от 49 900 ₽"),
}

TPL = """<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@700;900&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{width:1200px;height:630px;background:{accent};color:#f4f1e8;font-family:Inter,sans-serif;
       display:flex;flex-direction:column;justify-content:space-between;padding:72px 80px;overflow:hidden;position:relative}}
  .grid{{position:absolute;inset:0;opacity:.14;
        background-image:repeating-linear-gradient(90deg,rgba(0,0,0,.5) 0 2px,transparent 2px 6px),
                         repeating-linear-gradient(0deg,rgba(0,0,0,.5) 0 2px,transparent 2px 6px)}}
  .row{{position:relative;display:flex;justify-content:space-between;align-items:flex-start;
       font-family:Inter,sans-serif;font-weight:600;font-size:22px;letter-spacing:.18em;text-transform:uppercase}}
  h1{{position:relative;font-family:Unbounded,sans-serif;font-weight:900;font-size:{size}px;line-height:1.05;
     text-transform:lowercase;letter-spacing:-.02em;max-width:1040px}}
  p{{position:relative;font-size:32px;line-height:1.35;max-width:900px;margin-top:26px}}
  .foot{{position:relative;display:flex;justify-content:space-between;align-items:center;font-size:24px}}
  .price{{background:#f4f1e8;color:{accent};font-family:Unbounded,sans-serif;font-weight:700;
         font-size:26px;padding:12px 22px;text-transform:lowercase}}
</style></head><body>
<div class="grid"></div>
<div class="row"><span>Ника Штефан</span><span>{corner}</span></div>
<div><h1>{title}</h1><p>{sub}</p></div>
<div class="foot"><span>ex-Head of Product Discovery · Т-Банк · 9 лет в продукте</span><span class="price">{price}</span></div>
</body></html>"""


def main():
    TMP.mkdir(exist_ok=True)
    for slug, offer in OFFERS.items():
        title, sub, price = CARDS[slug]
        size = 84 if len(title) <= 24 else 68
        html = TPL.format(accent=offer["accent"], title=title, sub=sub, price=price,
                          corner=offer["corners"][2], size=size)
        src = TMP / f"{slug}.html"
        src.write_text(html, encoding="utf-8")
        out = ROOT / "img" / f"og-{slug}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--window-size=1200,630", "--virtual-time-budget=4000",
                        f"--screenshot={out}", f"file://{src}"],
                       check=True, capture_output=True)
        print("готово:", out.name)


if __name__ == "__main__":
    main()
