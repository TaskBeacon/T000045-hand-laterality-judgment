from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


CANVAS = (420, 280)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)


def _draw_base_left_hand(view: str) -> Image.Image:
    """Draw a simple line-art left hand in upright orientation."""
    img = Image.new("RGBA", CANVAS, WHITE)
    draw = ImageDraw.Draw(img)

    # Palm and wrist.
    draw.rounded_rectangle((142, 108, 252, 225), radius=18, outline=BLACK, width=5)
    draw.rounded_rectangle((171, 216, 223, 252), radius=10, outline=BLACK, width=5)

    # Fingers.
    finger_boxes = [
        (150, 54, 171, 116),
        (176, 44, 197, 115),
        (202, 42, 223, 116),
        (228, 52, 249, 117),
    ]
    for box in finger_boxes:
        draw.rounded_rectangle(box, radius=8, outline=BLACK, width=5)

    # Thumb protrusion.
    thumb_points = [(142, 146), (120, 132), (104, 142), (111, 168), (142, 162)]
    draw.polygon(thumb_points, outline=BLACK, fill=WHITE)
    draw.line((142, 146, 120, 132), fill=BLACK, width=5)
    draw.line((120, 132, 104, 142), fill=BLACK, width=5)
    draw.line((104, 142, 111, 168), fill=BLACK, width=5)
    draw.line((111, 168, 142, 162), fill=BLACK, width=5)

    # View-specific inner details.
    if view == "back":
        # Fingernail hints.
        for x in (154, 180, 206, 232):
            draw.line((x, 58, x + 14, 58), fill=BLACK, width=3)
        draw.line((154, 79, 164, 81), fill=BLACK, width=2)
        draw.line((180, 69, 190, 71), fill=BLACK, width=2)
        draw.line((206, 67, 216, 69), fill=BLACK, width=2)
        draw.line((232, 77, 242, 79), fill=BLACK, width=2)
    else:
        # Palm creases.
        draw.arc((165, 145, 235, 205), start=205, end=340, fill=BLACK, width=3)
        draw.line((176, 155, 220, 172), fill=BLACK, width=3)
        draw.line((174, 178, 226, 178), fill=BLACK, width=3)

    return img


def build_assets(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    left_back = _draw_base_left_hand("back")
    left_palm = _draw_base_left_hand("palm")
    right_back = ImageOps.mirror(left_back)
    right_palm = ImageOps.mirror(left_palm)

    outputs = {
        "hand_back_left.png": left_back,
        "hand_back_right.png": right_back,
        "hand_palm_left.png": left_palm,
        "hand_palm_right.png": right_palm,
    }

    written: list[Path] = []
    for name, image in outputs.items():
        path = out_dir / name
        image.save(path)
        written.append(path)

    return written


if __name__ == "__main__":
    assets_dir = Path(__file__).resolve().parent
    files = build_assets(assets_dir)
    for path in files:
        print(path)
