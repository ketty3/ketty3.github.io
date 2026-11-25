# -*- coding: utf-8 -*-
"""Создаёт внутренние страницы-проигрыватели презентаций.

Запуск: python generate_player.py
Результат: lectures/lecture-01.html ... lecture-16.html
"""
from __future__ import annotations

import html
from pathlib import Path

from generate_presentations import AUTHOR, COURSE, build_slides, parse_source
from generate_site import ACCENTS

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "lectures"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def render_slide(item: dict, index: int) -> str:
    lead_text = item.get("lead", "")
    lead = f'\n        <p class="slide-lead">{esc(lead_text)}</p>' if lead_text else ""

    if item["kind"] == "cover":
        content = f"""        <div class="big-number">{esc(item['sub'].split(' · ')[0].replace('Лекция ', '').strip())}</div>
        <h2>{esc(item['title'])}</h2>
        <p class="slide-lead">{esc(item['sub'])}</p>
        <p class="cover-author">{esc(AUTHOR)}</p>"""
    elif item["kind"] == "note":
        content = f"""        <h2>{esc(item['title'])}</h2>
        <p class="slide-lead">{esc(item['lead'])}</p>"""
    elif item["kind"] == "chips":
        chips = "".join(f'<span class="chip">{esc(t)}</span>' for t in item["items"])
        content = f"""        <h2>{esc(item['title'])}</h2>{lead}
        <div class="slide-bottom"><div class="chips">{chips}</div></div>"""
    elif item["kind"] == "question":
        refs = "".join(
            f'<li><span class="li-num">•</span><span class="li-text">{esc(t)}</span></li>'
            for t in item["items"]
        )
        content = f"""        <h2>{esc(item['title'])}</h2>
        <div class="question"><b>Для обсуждения</b><p>{esc(item['lead'])}</p></div>
        <ul class="slide-list">{refs}</ul>"""
    else:
        marker = lambda i: f"{i + 1:02d}" if item["kind"] == "steps" else "•"
        rows = "".join(
            f'<li><span class="li-num">{marker(i)}</span><span class="li-text">{esc(t)}</span></li>'
            for i, t in enumerate(item["items"])
        )
        content = f"""        <h2>{esc(item['title'])}</h2>{lead}
        <ul class="slide-list">{rows}</ul>"""

    kicker = esc(item.get("label", ""))
    state = "slide active" if index == 1 else "slide"
    return f"""      <section class="{state}" data-slide="{index}">
        <div class="slide-kicker">{kicker}</div>
{content}
      </section>"""


def render_page(lecture: dict, module: dict, slides: list[dict]) -> str:
    n = lecture["number"]
    color = ACCENTS[(module["number"] - 1) % len(ACCENTS)]
    slides_html = "\n".join(render_slide(item, i) for i, item in enumerate(slides, 1))
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{esc(lecture['title'])} — {esc(COURSE)}">
  <title>Лекция {n:02d}. {esc(lecture['title'])}</title>
  <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
  <div class="site-bg"></div>
  <main class="deck" style="--accent: {color};">
    <a class="back-link" href="../index.html#module-{module['number']}">← К программе курса</a>
    <div class="deck-head">
      <div class="chips"><span class="chip">Модуль {module['number']}</span><span class="chip">Лекция {n:02d}</span></div>
      <h1>{esc(lecture['title'])}</h1>
      <p class="sub">{esc(COURSE)}</p>
    </div>
    <div class="progress"><span class="progress-bar"></span></div>
    <div class="deck-slides">
{slides_html}
    </div>
    <div class="controls">
      <button class="btn" type="button" data-prev><span aria-hidden="true">←</span> <span class="label">Назад</span></button>
      <div class="dots" data-dots></div>
      <span class="counter" data-counter>01 / {len(slides):02d}</span>
      <button class="btn primary" type="button" data-next><span class="label">Далее</span> <span aria-hidden="true">→</span></button>
    </div>
    <p class="hint">Листайте стрелками ← → или пробелом · печать выведет все слайды</p>
  </main>
  <footer>
    <div class="wrap">
      <span>{esc(COURSE)}</span>
    </div>
  </footer>
  <script src="../assets/app.js"></script>
</body>
</html>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    modules = parse_source()
    total = 0
    for module in modules:
        for lecture in module["lectures"]:
            slides = build_slides(lecture, module)
            path = OUT / f"lecture-{lecture['number']:02d}.html"
            path.write_text(render_page(lecture, module, slides), encoding="utf-8")
            total += 1
    print(f"Готово: {total} страниц-проигрывателей в {OUT}")


if __name__ == "__main__":
    main()
