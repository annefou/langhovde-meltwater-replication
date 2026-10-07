"""Extract polylines from a MATLAB-written EPS figure.

The deposit ships the EPS output of the authors' MATLAB scripts (`fig3.eps`,
`fig_s6.eps`). MATLAB writes each plotted line as a vertex list followed by a
start point and a draw command (`DL` absolute, `DRL` relative, defined in the EPS
prolog). This module interprets just enough PostScript to recover those
polylines with their stroke colour, width and dash pattern, in the file's own
drawing units. Calibrate to data units from tick positions in the same file.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

TOKEN = re.compile(r"\[[^\]]*\]|\([^)]*\)|/?[^\s\[\]()]+")


@dataclass
class Polyline:
    xy: np.ndarray            # (n, 2) drawing units, y increasing downwards
    rgb: tuple[float, float, float]
    width: float
    dash: str
    index: int = field(default=0)


def _num(tok: str) -> float | None:
    try:
        return float(tok)
    except ValueError:
        return None


def read_polylines(path: Path) -> list[Polyline]:
    text = Path(path).read_text(errors="replace")
    body = text.split("%%EndPageSetup", 1)[1]
    stack: list = []
    rgb, width, dash = (0.0, 0.0, 0.0), 1.0, "[]"
    out: list[Polyline] = []
    for tok in TOKEN.findall(body):
        v = _num(tok)
        if v is not None:
            stack.append(v)
            continue
        if tok.startswith("[") or tok.startswith("(") or tok.startswith("/"):
            stack.append(tok)
            continue
        if tok in ("DL", "DRL"):
            y0, x0, n = stack.pop(), stack.pop(), int(stack.pop())
            verts = [(stack.pop(-2), stack.pop()) for _ in range(n)] if n else []
            # PostScript pops vertices from the top of the stack: last-written vertex first.
            pts = [(x0, y0)]
            for vx, vy in verts:
                if tok == "DL":
                    pts.append((vx, vy))
                else:
                    pts.append((pts[-1][0] + vx, pts[-1][1] + vy))
            out.append(Polyline(np.array(pts), rgb, width, dash, len(out)))
        elif tok == "LAR":
            b, g, r = stack.pop(), stack.pop(), stack.pop()
            stack.pop()                      # dash offset
            dash = stack.pop()
            stack.pop(); stack.pop()         # cap, join
            width = stack.pop()
            rgb = (r, g, b)
        elif tok == "LAG":
            gray = stack.pop()
            stack.pop()
            dash = stack.pop()
            stack.pop(); stack.pop()
            width = stack.pop()
            rgb = (gray, gray, gray)
        elif tok == "RC":
            b, g, r = stack.pop(), stack.pop(), stack.pop()
            rgb = (r, g, b)
        elif tok == "GC":
            gray = stack.pop()
            rgb = (gray, gray, gray)
        elif tok == "LW":
            width = stack.pop()
        else:
            # Any other operator: drop the operands it would have consumed is not
            # knowable in general; MATLAB's EPS keeps operands and operators on one
            # logical statement, so clearing the stack is safe between statements.
            stack.clear()
    return out
