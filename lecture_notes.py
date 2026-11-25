# -*- coding: utf-8 -*-
"""Конспекты лекций. Источник — четыре файла notes_part*.py."""
from __future__ import annotations

from notes_part1 import NOTES as PART1
from notes_part2 import NOTES as PART2
from notes_part3 import NOTES as PART3
from notes_part4 import NOTES as PART4

NOTES: dict[int, list[str]] = {}
for part in (PART1, PART2, PART3, PART4):
    NOTES.update(part)

if sorted(NOTES) != list(range(1, 17)):
    raise RuntimeError(f"Конспекты должны охватывать лекции 1..16, получено: {sorted(NOTES)}")
