from PIL import Image

from redact_app.export import apply_redactions_to_image
from redact_app.redaction import RedactionRect, RedactionStore


def test_rect_from_points_normalizes_drag_direction() -> None:
    rect = RedactionRect.from_points(
        page_index=2,
        start_x=30,
        start_y=40,
        end_x=10,
        end_y=15,
    )

    assert rect == RedactionRect(page_index=2, x=10, y=15, width=20, height=25)


def test_rect_clips_to_image_bounds() -> None:
    rect = RedactionRect(page_index=0, x=-10, y=5, width=30, height=40)

    assert rect.clipped(100, 20) == RedactionRect(
        page_index=0,
        x=0,
        y=5,
        width=20,
        height=15,
    )


def test_redaction_store_groups_by_page() -> None:
    store = RedactionStore()
    first = RedactionRect(page_index=0, x=1, y=2, width=3, height=4)
    second = RedactionRect(page_index=1, x=5, y=6, width=7, height=8)

    store.add(first)
    store.add(second)

    assert store.for_page(0) == [first]
    assert store.for_page(1) == [second]
    assert store.total_count() == 2


def test_apply_redactions_burns_black_pixels() -> None:
    image = Image.new("RGB", (10, 10), "white")
    rect = RedactionRect(page_index=0, x=2, y=3, width=4, height=2)

    redacted = apply_redactions_to_image(image, [rect])

    assert redacted.getpixel((2, 3)) == (0, 0, 0)
    assert redacted.getpixel((5, 4)) == (0, 0, 0)
    assert redacted.getpixel((1, 3)) == (255, 255, 255)
    assert image.getpixel((2, 3)) == (255, 255, 255)

