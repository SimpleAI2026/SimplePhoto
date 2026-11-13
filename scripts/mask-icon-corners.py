#!/usr/bin/env python3
"""Detect the rounded-square radius of SimplePhoto icons and write RGBA PNGs
whose pixels outside the rounded rect have alpha=0 (anti-aliased)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "branding" / "simplephoto-logo-1024.png"


def coverage_from_bg(pix, x: int, y: int, bg: tuple[int, int, int]) -> float:
    r, g, b, *_ = pix[x, y]
    dist = math.sqrt(sum((int(c) - int(bc)) ** 2 for c, bc in zip((r, g, b), bg)))
    # 0 = background, 1 = clearly artwork. 0.12 * 441.67 ≈ 53 RGB units.
    return max(0.0, min(1.0, dist / 53.0))


def crossing_x(im: Image.Image, y: int, bg: tuple[int, int, int], from_right: bool = False) -> float:
    """Subpixel x where coverage crosses 50% along row y, from a side."""
    w, _ = im.size
    pix = im.load()
    xs = range(w - 1, -1, -1) if from_right else range(w)
    prev_c, prev_x = 0.0, (w - 1 if from_right else 0)
    for x in xs:
        c = coverage_from_bg(pix, x, y, bg)
        if c >= 0.5:
            if abs(c - prev_c) < 1e-9:
                return float(x)
            t = (0.5 - prev_c) / (c - prev_c)
            return prev_x + t * (x - prev_x)
        prev_c, prev_x = c, x
    return float(w / 2)


def crossing_y(im: Image.Image, x: int, bg: tuple[int, int, int], from_bottom: bool = False) -> float:
    _, h = im.size
    pix = im.load()
    ys = range(h - 1, -1, -1) if from_bottom else range(h)
    prev_c, prev_y = 0.0, (h - 1 if from_bottom else 0)
    for y in ys:
        c = coverage_from_bg(pix, x, y, bg)
        if c >= 0.5:
            if abs(c - prev_c) < 1e-9:
                return float(y)
            t = (0.5 - prev_c) / (c - prev_c)
            return prev_y + t * (y - prev_y)
        prev_c, prev_y = c, y
    return float(h / 2)


def detect_radius(im: Image.Image) -> float:
    """Corner radius for a flush rounded-rect: 50% coverage inset on each edge."""
    w, h = im.size
    pix = im.load()
    bg = pix[0, 0][:3]
    samples = [
        crossing_x(im, 0, bg, False),
        w - 1 - crossing_x(im, 0, bg, True),
        crossing_x(im, h - 1, bg, False),
        w - 1 - crossing_x(im, h - 1, bg, True),
        crossing_y(im, 0, bg, False),
        h - 1 - crossing_y(im, 0, bg, True),
        crossing_y(im, w - 1, bg, False),
        h - 1 - crossing_y(im, w - 1, bg, True),
    ]
    samples.sort()
    r = (samples[3] + samples[4]) / 2.0  # median of 8
    return r, samples


def sdf_rounded_box(px: float, py: float, w: float, h: float, r: float) -> float:
    """Signed distance: negative inside. Box occupies [0,w] x [0,h]."""
    cx, cy = w / 2.0, h / 2.0
    hx, hy = w / 2.0, h / 2.0
    ax, ay = abs(px - cx), abs(py - cy)
    dx, dy = ax - (hx - r), ay - (hy - r)
    ox, oy = max(dx, 0.0), max(dy, 0.0)
    return math.hypot(ox, oy) + min(max(dx, dy), 0.0) - r


def apply_mask(im: Image.Image, radius: float, samples: int = 8) -> Image.Image:
    src = im.convert("RGBA")
    w, h = src.size
    pix = src.load()
    bg = pix[0, 0][:3]
    out = Image.new("RGBA", (w, h))
    dest = out.load()
    r = min(radius, w / 2.0, h / 2.0)
    step = 1.0 / samples
    # offset to pixel-center grid for each subsample
    for y in range(h):
        for x in range(w):
            pr, pg, pb, pa = pix[x, y]
            # Supersample the rounded-rect coverage
            acc = 0.0
            yy = y + step / 2.0
            for _i in range(samples):
                xx = x + step / 2.0
                for _j in range(samples):
                    if sdf_rounded_box(xx, yy, w, h, r) <= 0.0:
                        acc += 1.0
                    xx += step
                yy += step
            geo = acc / (samples * samples)
            # In the four corner squares, drop leftover opaque-white slivers
            # that sit inside a circular RR but are still background paint.
            in_corner = (x < r and y < r) or (x > w - 1 - r and y < r) or (x < r and y > h - 1 - r) or (x > w - 1 - r and y > h - 1 - r)
            if in_corner:
                cov = coverage_from_bg(pix, x, y, bg)
                geo *= cov
            a = int(round(pa * geo)) if geo > 0.0 else 0
            if a <= 0:
                dest[x, y] = (0, 0, 0, 0)
            else:
                dest[x, y] = (pr, pg, pb, a)
        # Exact image corners must be transparent for a rounded square with r>=1.
        if r >= 1.0:
            for cx, cy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
                dest[cx, cy] = (0, 0, 0, 0)
    return out


def verify(path: Path, label: str = "") -> list[str]:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    pix = im.load()
    problems = []
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    for x, y in corners:
        a = pix[x, y][3]
        if a != 0:
            problems.append(f"{path} corner ({x},{y}) alpha={a}")
    # A couple of near-corner pixels should also be 0 or very low for R>>2
    # Neighbours of the corner stay fully transparent only when r is large enough
    # that the inset covers them (not on 16px, where r≈2.5 and (1,0) is on the AA fringe).
    if min(w, h) >= 48:
        for x, y in [(1, 0), (0, 1), (w - 2, 0), (0, h - 2)]:
            a = pix[x, y][3]
            if a != 0:
                problems.append(f"{path} near-corner ({x},{y}) alpha={a}")
    mid = pix[w // 2, h // 2][3]
    if mid < 200:
        problems.append(f"{path} center alpha={mid} (expected opaque artwork)")
    print(f"verify {label or path}: {w}x{h} corners={[pix[x, y][3] for x, y in corners]} center_a={mid} {'OK' if not problems else 'FAIL'}")
    return problems


def main() -> int:
    master = Image.open(MASTER).convert("RGBA")
    if master.getpixel((0, 0))[3] < 128:
        raise SystemExit(
            f"{MASTER} already has a transparent corner; restore the unmasked original before running"
        )
    r, samples = detect_radius(master)
    print(f"master {MASTER.name} {master.size[0]}x{master.size[1]}")
    print(f"detected radius R={r:.2f} (edge insets: {', '.join(f'{s:.2f}' for s in samples)})")
    masked = apply_mask(master, r)
    # Branding masters
    dest_1024 = ROOT / "branding" / "simplephoto-logo-1024.png"
    dest_source = ROOT / "branding" / "simplephoto-logo-source.png"
    dest_app = ROOT / "branding" / "simplephoto-app-128.png"
    masked.save(dest_1024, "PNG")
    masked.save(dest_source, "PNG")
    print(f"wrote {dest_1024} and {dest_source}")

    sizes = {
        ROOT / "branding" / "simplephoto-app-128.png": 128,
        ROOT / "extension" / "icons" / "icon128.png": 128,
        ROOT / "extension" / "icons" / "icon48.png": 48,
        ROOT / "extension" / "icons" / "icon32.png": 32,
        ROOT / "extension" / "icons" / "icon16.png": 16,
    }
    problems = []
    problems += verify(dest_1024, "logo-1024")
    problems += verify(dest_source, "logo-source")
    for path, size in sizes.items():
        # Downsample from the masked master, then re-apply a scaled rounded mask
        # so Lanczos alpha bleed cannot dirty the corner pixels.
        icon = masked.resize((size, size), Image.Resampling.LANCZOS)
        scaled_r = r * (size / master.size[0])
        icon = apply_mask(icon, scaled_r)
        path.parent.mkdir(parents=True, exist_ok=True)
        icon.save(path, "PNG")
        print(f"wrote {path} ({size}x{size}, R={scaled_r:.2f})")
        problems += verify(path)

    if problems:
        print("FAILURES:")
        for p in problems:
            print(" -", p)
        return 1
    print("all icons: corner alpha is 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
