# -*- coding: utf-8 -*-
"""Собирает главную страницу курса из плана лекций.

Запуск: python generate_site.py
Презентации создаются отдельно командой python generate_presentations.py
"""
from __future__ import annotations

import html
import re
from pathlib import Path

from generate_presentations import DETAILS
from sources import SOURCE_URLS, TEACHER_SOURCES

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "plan-lectures.txt"
COURSE = "Искусственный интеллект в профессиональной деятельности"

# Цвета модулей: 1-й, 2-й, 3-й, 4-й.
ACCENTS = ["#6f9cff", "#2ad6bd", "#ffb454", "#ff7ba8"]


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def parse_source() -> list[dict]:
    modules: list[dict] = []
    for raw in SOURCE.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("Модуль "):
            found = re.match(r"Модуль\s+(\d+)\.\s*(.+)", line)
            if found:
                number, title = found.groups()
                title = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
                modules.append({"number": int(number), "title": title, "lectures": []})
        elif line.startswith("Лекция "):
            found = re.match(r"Лекция\s+(\d+)\.\s*(.+)", line)
            if found and modules:
                number, title = found.groups()
                modules[-1]["lectures"].append(
                    {"number": int(number), "title": title.strip(), "bullets": []}
                )
        elif modules and modules[-1]["lectures"]:
            modules[-1]["lectures"][-1]["bullets"].append(line)
    if not modules:
        raise SystemExit("Не удалось найти модули в исходном файле: " + str(SOURCE))
    return modules


def teaser(bullets: list[str]) -> str:
    if not bullets:
        return ""
    clean = bullets[0].strip().rstrip(".")
    match = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", clean)
    base = match.group(1) if match else clean
    if ":" in base:
        base = base.split(":", 1)[0]
    return base.strip().rstrip(".")


def render_references() -> str:
    entries: dict[str, tuple[str, str]] = {}
    missing = []
    for data in DETAILS.values():
        for ref in data.get("refs", []):
            url = SOURCE_URLS.get(ref)
            if not url:
                missing.append(ref)
                continue
            entries.setdefault(url.rstrip("/").lower(), (ref, url))
    if missing:
        raise RuntimeError("Не заданы ссылки на источники: " + "; ".join(missing))

    for title, url in TEACHER_SOURCES:
        entries.setdefault(url.rstrip("/").lower(), (title, url))

    items = [
        f'      <li><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(title)}</a></li>'
        for title, url in sorted(entries.values(), key=lambda pair: pair[0].lower())
    ]
    return f"""    <section class="references" id="literature">
      <div class="section-head">
        <h2>Литература и источники</h2>
      </div>
      <p class="references-lead">Источники, использованные при подготовке курса, и материалы с сайта преподавателя. Ссылки открываются в новой вкладке.</p>
      <ul class="reference-list">
{chr(10).join(items)}
      </ul>
    </section>"""


def render_index(modules: list[dict]) -> str:
    total = sum(len(m["lectures"]) for m in modules)
    blocks = []
    for module in modules:
        color = ACCENTS[(module["number"] - 1) % len(ACCENTS)]
        cards = []
        for lecture in module["lectures"]:
            cards.append(
                f"""        <a class="lecture-card" href="lectures/lecture-{lecture['number']:02d}.html">
          <span class="card-top"><span class="card-num">Лекция {lecture['number']:02d}</span></span>
          <span class="card-title">{esc(lecture['title'])}</span>
          <span class="card-teaser">{esc(teaser(lecture['bullets']))}</span>
          <span class="card-arrow" aria-hidden="true">↗</span>
        </a>"""
            )
        blocks.append(
            f"""    <section class="module" id="module-{module['number']}" style="--accent: {color};">
      <div class="module-head">
        <span class="module-index">{module['number']:02d}</span>
        <div><h3>Модуль {module['number']}. {esc(module['title'])}</h3></div>
      </div>
      <div class="lecture-grid">
{chr(10).join(cards)}
      </div>
    </section>"""
        )

    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{esc(COURSE)} — теория, практические кейсы и конспекты по искусственному интеллекту">
  <title>{esc(COURSE)}</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <div class="site-bg"></div>
  <main class="wrap">
    <section class="hero">
      <h1>Искусственный интеллект<br><em>в профессиональной деятельности</em></h1>
      <p class="subtitle">Салина Анна гр. МЭЭ2501</p>
      <p class="hero-lead">От стратегии внедрения и данных до LLM, ИИ-агентов и целевой архитектуры компании.</p>
    </section>
    <section class="modules">
      <div class="section-head">
        <h2>Программа курса</h2>
      </div>
{chr(10).join(blocks)}
    </section>
{render_references()}
  </main>
  <footer>
    <div class="wrap">
      <span>{esc(COURSE)}</span>
    </div>
  </footer>
</body>
</html>
"""


def main() -> None:
    modules = parse_source()
    (ROOT / "index.html").write_text(render_index(modules), encoding="utf-8")
    print(f"Готово: index.html с {sum(len(m['lectures']) for m in modules)} лекциями")


if __name__ == "__main__":
    main()
