from __future__ import annotations

from dataclasses import dataclass
from typing import DefaultDict
from collections import defaultdict


@dataclass(frozen=True)
class RedactionRect:
    """A redaction rectangle in rendered page-image pixel coordinates."""

    page_index: int
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_points(
        cls,
        page_index: int,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ) -> "RedactionRect":
        """Create a normalized rectangle from two drag points."""
        left = min(start_x, end_x)
        top = min(start_y, end_y)
        right = max(start_x, end_x)
        bottom = max(start_y, end_y)
        return cls(page_index, left, top, right - left, bottom - top)

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    @property
    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    def clipped(self, image_width: int, image_height: int) -> "RedactionRect":
        """Return this rectangle clipped to the rendered image bounds."""
        left = max(0, min(self.x, image_width))
        top = max(0, min(self.y, image_height))
        right = max(0, min(self.right, image_width))
        bottom = max(0, min(self.bottom, image_height))
        return RedactionRect(
            page_index=self.page_index,
            x=left,
            y=top,
            width=max(0, right - left),
            height=max(0, bottom - top),
        )

    def contains(self, x: int, y: int) -> bool:
        return self.x <= x <= self.right and self.y <= y <= self.bottom


class RedactionStore:
    """In-memory redaction rectangles grouped by zero-based page index."""

    def __init__(self) -> None:
        self._rects: DefaultDict[int, list[RedactionRect]] = defaultdict(list)

    def add(self, rect: RedactionRect) -> None:
        if rect.is_empty:
            return
        self._rects[rect.page_index].append(rect)

    def remove(self, rect: RedactionRect) -> None:
        rects = self._rects.get(rect.page_index)
        if not rects:
            return
        try:
            rects.remove(rect)
        except ValueError:
            return

    def for_page(self, page_index: int) -> list[RedactionRect]:
        return list(self._rects.get(page_index, []))

    def clear(self) -> None:
        self._rects.clear()

    def total_count(self) -> int:
        return sum(len(rects) for rects in self._rects.values())

