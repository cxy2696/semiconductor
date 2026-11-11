"""Server-rendered SVG charts.

Charts are generated at build time so the site works without JavaScript or any
third-party CDN. Labels and values are escaped; every chart exposes a text
alternative through <title>/<desc>.
"""

from __future__ import annotations

import html
import math
from dataclasses import dataclass
from typing import Any, Sequence

STAGE_COLORS = {
    "eda_ip": "#6d5efc",
    "design": "#2f80ed",
    "manufacturing": "#0f9d8f",
    "memory": "#e08b2f",
    "equipment": "#c8553d",
    "materials": "#8a9a5b",
    "packaging": "#b5527d",
    "module": "#5b6b7a",
}
MUTED = "#94a3b8"
GRID = "#e2e8f0"
INK = "#334155"


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def sparkline(
    values: Sequence[float],
    width: int = 104,
    height: int = 30,
    color: str = "#0f766e",
    label: str = "",
) -> str:
    clean = [float(v) for v in values if v is not None and math.isfinite(float(v))]
    if len(clean) < 2:
        return f'<svg class="spark" viewBox="0 0 {width} {height}" role="img" aria-label="{_esc(label or "no data")}"><line x1="0" y1="{height/2}" x2="{width}" y2="{height/2}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 3"/></svg>'

    low, high = min(clean), max(clean)
    span = high - low or 1.0
    pad = 3
    step = (width - pad * 2) / (len(clean) - 1)
    points = []
    for index, value in enumerate(clean):
        x = pad + index * step
        y = height - pad - (value - low) / span * (height - pad * 2)
        points.append((x, y))
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f"{path} L{points[-1][0]:.1f},{height} L{points[0][0]:.1f},{height} Z"
    trend = "#c2410c" if clean[-1] < clean[0] else color
    return (
        f'<svg class="spark" viewBox="0 0 {width} {height}" role="img" aria-label="{_esc(label)}">'
        f'<path d="{area}" fill="{trend}" opacity="0.10"/>'
        f'<path d="{path}" fill="none" stroke="{trend}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>'
        f"</svg>"
    )


def range_bar(low: float | None, high: float | None, price: float | None, width: int = 220, height: int = 10) -> str:
    if low is None or high is None or price is None or high <= low:
        return ""
    ratio = min(1.0, max(0.0, (price - low) / (high - low)))
    x = ratio * width
    return (
        f'<svg class="range-bar" viewBox="0 0 {width} {height}" role="img" aria-label="52-week range">'
        f'<rect x="0" y="{height/2 - 1}" width="{width}" height="2" rx="1" fill="{GRID}"/>'
        f'<rect x="0" y="{height/2 - 1}" width="{x:.1f}" height="2" rx="1" fill="#0f9d8f" opacity="0.55"/>'
        f'<circle cx="{x:.1f}" cy="{height/2}" r="4" fill="#0f766e"/>'
        f"</svg>"
    )


@dataclass
class ScatterPoint:
    x: float
    y: float
    size: float
    color: str
    label: str
    href: str = ""
    meta: str = ""


def scatter(
    points: Sequence[ScatterPoint],
    x_label: str,
    y_label: str,
    width: int = 780,
    height: int = 400,
    caption: str = "",
) -> str:
    valid = [point for point in points if point.x and point.x > 0 and math.isfinite(point.x) and math.isfinite(point.y)]
    if not valid:
        return f'<p class="chart-empty">{_esc(caption or "No data")}</p>'

    left, right, top, bottom = 56, 18, 16, 44
    plot_w, plot_h = width - left - right, height - top - bottom
    x_min, x_max = 1.0, 200.0

    def sx(value: float) -> float:
        clamped = min(x_max, max(x_min, value))
        return left + (math.log10(clamped) - math.log10(x_min)) / (math.log10(x_max) - math.log10(x_min)) * plot_w

    y_min = min(0.0, min(point.y for point in valid) * 1.1)
    y_max = max(10.0, max(point.y for point in valid) * 1.1)
    y_span = y_max - y_min or 1.0

    def sy(value: float) -> float:
        return top + plot_h - ((max(y_min, min(y_max, value)) - y_min) / y_span) * plot_h

    max_size = max(point.size for point in valid) or 1.0
    parts = [
        f'<svg class="scatter" viewBox="0 0 {width} {height}" role="img" aria-label="{_esc(caption or x_label)}">',
        f"<desc>{_esc(caption)}</desc>",
    ]
    for step in range(5):
        tick = y_min + y_span * step / 4
        y = sy(tick)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(
            f'<text x="{left - 8}" y="{y + 3:.1f}" text-anchor="end" font-size="10" fill="{MUTED}">{tick:.0f}</text>'
        )
    for tick in (1, 2, 5, 10, 20, 50, 100, 200):
        x = sx(tick)
        parts.append(
            f'<text x="{x:.1f}" y="{height - bottom + 16}" text-anchor="middle" font-size="10" fill="{MUTED}">{tick}</text>'
        )
    parts.append(
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height - bottom}" stroke="{MUTED}" stroke-width="1"/>'
    )
    parts.append(
        f'<line x1="{left}" y1="{height - bottom}" x2="{width - right}" y2="{height - bottom}" stroke="{MUTED}" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{left + plot_w / 2:.0f}" y="{height - 6}" text-anchor="middle" font-size="11" fill="{INK}">{_esc(x_label)}</text>'
    )
    parts.append(
        f'<text x="14" y="{top + plot_h / 2:.0f}" text-anchor="middle" font-size="11" fill="{INK}" transform="rotate(-90 14 {top + plot_h / 2:.0f})">{_esc(y_label)}</text>'
    )

    for point in sorted(valid, key=lambda item: item.size):
        radius = 3.2 + 11 * math.sqrt(max(point.size, 0) / max_size)
        cx, cy = sx(point.x), sy(point.y)
        title = f"{point.label} · {point.meta}"
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" fill="{point.color}" fill-opacity="0.55" stroke="{point.color}" stroke-width="1"><title>{_esc(title)}</title></circle>')

    parts.append("</svg>")
    return "".join(parts)


def legend(stages: Sequence[tuple[str, str]]) -> str:
    items = "".join(
        f'<span class="legend-item"><span class="legend-dot" style="background:{STAGE_COLORS.get(stage_id, MUTED)}"></span>{_esc(label)}</span>'
        for stage_id, label in stages
    )
    return f'<div class="legend">{items}</div>'
