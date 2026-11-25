# -*- coding: utf-8 -*-
"""Создаёт 16 подробных презентаций PPTX по плану лекций.

Запуск: python generate_presentations.py
Результат: presentations/lecture-01.pptx ... lecture-16.pptx
"""
from __future__ import annotations

import re
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from course_content import LECTURES as DETAILS

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "plan-lectures.txt"
OUT = ROOT / "presentations"
COURSE = "Искусственный интеллект в профессиональной деятельности"
AUTHOR = "Салина Анна гр. МЭЭ2501"
FONT_REG = "Arial"

MODULE_COLORS = ["2F6BFF", "12A594", "E08A2C", "D9537F"]

# Содержание лекций вынесено в course_content.py: оттуда же берутся тексты
# слайдов и справочники для главной страницы.


def parse_source():
    modules = []
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
    return modules


# Заголовки, которые после автоматического сокращения теряют смысл.
TITLE_OVERRIDES = {
    "Почему данные — новая нефть: качество, разметка и синтез данных":
        "Почему данные — новая нефть: качество, разметка и синтез",
    "Тренды: Общий искусственный интеллект (AGI), квантовый ИИ, нейроморфные вычисления":
        "Тренды: общий ИИ, квантовый ИИ и нейроморфные вычисления",
}


def block_title(bullet: str) -> str:
    clean = bullet.strip().rstrip(".")
    if clean in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[clean]
    match = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", clean)
    if match:
        base = match.group(1)
    else:
        base = clean
    if ":" in base:
        base = base.split(":", 1)[0]
    elif " — " in base:
        base = base.split(" — ", 1)[0]
    return base.strip().rstrip(".")


def build_slides(lecture: dict, module: dict) -> list[dict]:
    n = lecture["number"]
    d = DETAILS[n]
    titles = [block_title(b) for b in lecture["bullets"][:3]]
    # Практические выводы используем и на промежуточном слайде, и в итогах,
    # убирая повторяющийся префикс «Практический вывод:».
    takeaways = []
    for item in d["block_notes"]:
        clean = re.sub(r"^Практический вывод:\s*", "", item)
        takeaways.append(clean[:1].upper() + clean[1:])
    slides = [
        {
            "kind": "cover",
            "title": lecture["title"],
            "sub": f"Лекция {n:02d} · Модуль {module['number']} · {COURSE}",
        },
        {
            "kind": "list",
            "title": "Цели и результаты лекции",
            "lead": d["goal"],
            "items": d["outcomes"],
            "label": "После лекции вы сможете",
        },
        {
            "kind": "list",
            "title": "Почему тема важна",
            "lead": "",
            "items": d["context"],
            "label": "Контекст",
        },
    ]
    for i in range(3):
        slides.append(
            {
                "kind": "list",
                "title": f"Теория · {titles[i] if i < len(titles) else 'ключевые положения'}",
                "lead": "",
                "items": d["blocks"][i],
                "label": f"Блок {i + 1}",
            }
        )
        slides.append(
            {
                "kind": "note",
                "title": f"Вывод в практику · {i + 1}",
                "lead": takeaways[i],
                "items": [],
                "label": "Для бизнес-информатика",
            }
        )
    slides.extend(
        [
            {
                "kind": "steps",
                "title": d["case"]["title"],
                "lead": "",
                "items": d["case"]["steps"],
                "label": "Разбор кейса",
            },
            {"kind": "list", "title": "Типичные ошибки и риски", "lead": "", "items": d["pitfalls"], "label": "Что чаще всего идёт не так"},
            {"kind": "list", "title": "Метрики и критерии оценки", "lead": "", "items": d["metrics"], "label": "Как измерить эффект"},
            {"kind": "chips", "title": "Инструменты и стек", "lead": "", "items": d["tools"], "label": "Практический инструментарий"},
            {"kind": "list", "title": "Итоги лекции", "lead": "", "items": takeaways, "label": "Три главных вывода"},
            {
                "kind": "question",
                "title": "Вопросы и источники",
                "lead": d["question"],
                "items": d["refs"],
                "label": "Для обсуждения и самостоятельного изучения",
            },
        ]
    )
    return slides


# ----------------------------- PPTX ----------------------------------------
def add_text(slide, left, top, width, height, text, size=18, bold=False, color="1B2740", align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = box.text_frame
    frame.word_wrap = True
    p = frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = FONT_REG
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    return box


def make_pptx(path: Path, lecture: dict, module: dict, slides: list[dict]) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    accent = MODULE_COLORS[(module["number"] - 1) % len(MODULE_COLORS)]
    blank = prs.slide_layouts[6]

    for idx, item in enumerate(slides):
        slide = prs.slides.add_slide(blank)
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = RGBColor(247, 249, 252) if item["kind"] != "cover" else RGBColor.from_string(accent)

        if item["kind"] == "cover":
            add_text(slide, 1.0, 1.0, 11.3, 0.5, COURSE.upper(), 15, True, "FFFFFF")
            add_text(slide, 1.0, 1.8, 11.3, 0.8, f"ЛЕКЦИЯ {lecture['number']:02d}", 22, True, "FFFFFF")
            add_text(slide, 1.0, 2.6, 11.3, 2.2, item["title"], 38, True, "FFFFFF")
            add_text(slide, 1.0, 5.5, 11.3, 0.5, AUTHOR, 18, False, "FFFFFF")
            continue

        bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(0.16))
        bar.fill.solid()
        bar.fill.fore_color.rgb = RGBColor.from_string(accent)
        bar.line.fill.background()

        add_text(slide, 0.8, 0.45, 11.7, 0.35, item["label"].upper(), 12, True, accent)
        add_text(slide, 0.8, 0.85, 11.7, 0.9, item["title"], 28, True, "14213D")
        if item["lead"] and item["kind"] != "note":
            add_text(slide, 0.8, 1.75, 11.7, 0.9, item["lead"], 17, False, "44546A")

        top = 2.7 if (item["lead"] and item["kind"] != "note") else 2.1
        if item["kind"] == "note":
            add_text(slide, 0.8, top, 11.7, 1.6, item["lead"], 22, False, "14213D")
        elif item["kind"] == "chips":
            x, y = 0.8, top
            for term in item["items"]:
                box = slide.shapes.add_shape(5, Inches(x), Inches(y), Inches(3.7), Inches(0.85))
                box.fill.solid()
                box.fill.fore_color.rgb = RGBColor(232, 239, 252)
                box.line.color.rgb = RGBColor.from_string(accent)
                tf = box.text_frame
                tf.word_wrap = True
                tf.paragraphs[0].text = term
                tf.paragraphs[0].runs[0].font.size = Pt(16)
                tf.paragraphs[0].runs[0].font.color.rgb = RGBColor.from_string("14213D")
                x += 3.9
                if x > 9.5:
                    x, y = 0.8, y + 1.0
        else:
            y = top
            for i, line in enumerate(item["items"]):
                marker = f"{i + 1:02d}" if item["kind"] == "steps" else "•"
                add_text(slide, 0.8, y, 0.6, 0.5, marker, 17, True, accent)
                add_text(slide, 1.4, y, 11.1, 0.8, line, 16, False, "24324D")
                y += 0.88 if len(line) < 120 else 1.0

        add_text(slide, 0.8, 6.95, 6.0, 0.3, f"{COURSE} · лекция {lecture['number']:02d}", 10, False, "8895A8")
        add_text(slide, 11.8, 6.95, 0.8, 0.3, f"{idx + 1:02d} / {len(slides):02d}", 10, True, accent, PP_ALIGN.RIGHT)

    prs.save(str(path))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    modules = parse_source()
    total = 0
    for module in modules:
        for lecture in module["lectures"]:
            slides = build_slides(lecture, module)
            base = f"lecture-{lecture['number']:02d}"
            make_pptx(OUT / f"{base}.pptx", lecture, module, slides)
            total += 1
    print(f"Готово: {total} презентаций PPTX в {OUT}")


if __name__ == "__main__":
    main()
