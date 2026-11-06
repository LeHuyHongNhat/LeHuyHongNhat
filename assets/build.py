#!/usr/bin/env python3
"""Build the animated SVG cards used by the profile README.

    python3 assets/build.py          # writes assets/dark/*.svg and assets/light/*.svg

Standard library only. Every card is generated twice (GitHub dark / light theme) and the README
picks one with <picture> + prefers-color-scheme. Fonts are embedded as base64 (see fonts/README.md).
Content comes straight from the CV; edit the data blocks below, then re-run.
"""
from __future__ import annotations

import base64
import math
import pathlib
import random
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent
FONTS = ROOT / "fonts"
W = 840  # card width; GitHub's README column is ~840-880 px

THEMES = {
    "dark": dict(
        card="#0d1117", card2="#141b24", border="#2a3340", grid="#161d27",
        text="#e6edf3", muted="#8d96a0", faint="#4b5563",
        teal="#2dd4bf", amber="#f5b942", violet="#a78bfa", blue="#60a5fa",
        green="#3fb950", red="#f87171", glow=0.20,
    ),
    "light": dict(
        card="#ffffff", card2="#f6f8fa", border="#d0d7de", grid="#eef1f5",
        text="#1f2328", muted="#59636e", faint="#b4bcc6",
        teal="#0d9488", amber="#b45309", violet="#7c3aed", blue="#2563eb",
        green="#1a7f37", red="#cf222e", glow=0.10,
    ),
}

LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
         "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
VIET = ("U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,"
        "U+0303-0304,U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB")


def _b64(name: str) -> str:
    return base64.b64encode((FONTS / name).read_bytes()).decode()


def font_css(sans: bool = True, mono: bool = True, vi: bool = False) -> str:
    out = []
    face = "@font-face{{font-family:'{f}';src:url(data:font/woff2;base64,{d}) format('woff2');font-weight:100 900;unicode-range:{r}}}"
    if sans:
        out.append(face.format(f="G", d=_b64("Geist-latin.woff2"), r=LATIN))
    if mono:
        out.append(face.format(f="GM", d=_b64("GeistMono-latin.woff2"), r=LATIN))
    if vi:
        out.append(face.format(f="GM", d=_b64("GeistMono-vietnamese.woff2"), r=VIET))
    return "".join(out)


BASE_CSS = """
.s{font-family:'G',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}
.m{font-family:'GM',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}
@keyframes fu{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes fi{from{opacity:0}to{opacity:1}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes ping{0%{transform:scale(1);opacity:.6}80%,100%{transform:scale(3.2);opacity:0}}
.fu{animation:fu .8s cubic-bezier(.2,.7,.2,1) both}
.fi{animation:fi .9s ease both}
.blink{animation:blink 1.05s step-end infinite}
.ping{transform-box:fill-box;transform-origin:center;animation:ping 2.2s cubic-bezier(0,0,.2,1) infinite}
"""
REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def mw(text: str, size: float, ls: float = 0.0) -> float:
    """Width of a Geist Mono string (advance = 0.6 em)."""
    return len(text) * (size * 0.6 + ls) - (ls if text else 0)


def e(s: str) -> str:
    return escape(s, {'"': "&quot;"})


def delay(sec: float) -> str:
    return f'style="animation-delay:{sec:.2f}s"'


def smil_in(begin: float, dur: float = 0.7, dy: float = 10) -> str:
    """Fade/rise on the SMIL clock, so it stays in step with other SMIL motion in the same card."""
    return (f'<animate attributeName="opacity" values="0;1" dur="{dur}s" begin="{begin:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 {dy};0 0" dur="{dur}s" '
            f'begin="{begin:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .2 1"/>')


def svg(w: int, h: int, title: str, desc: str, css: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="t d" fill="none">'
        f'<title id="t">{e(title)}</title><desc id="d">{e(desc)}</desc>'
        f"<!-- Geist / Geist Mono (c) Vercel, SIL OFL 1.1 -->"
        f"<style>{css}{BASE_CSS}{REDUCED}</style>{body}</svg>"
    )


def frame(t: dict, w: int, h: int, rx: int = 16, grid: bool = True) -> str:
    out = [f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{rx}" fill="{t["card"]}" stroke="{t["border"]}"/>']
    if grid:
        out.append(
            f'<defs><pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">'
            f'<path d="M28 0H0V28" stroke="{t["grid"]}" stroke-width="1"/></pattern>'
            f'<radialGradient id="gridfade" cx="70%" cy="20%" r="85%"><stop offset="0" stop-color="#fff"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<mask id="gm"><rect width="{w}" height="{h}" fill="url(#gridfade)"/></mask></defs>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="url(#grid)" mask="url(#gm)"/>'
        )
    return "".join(out)


def header(t: dict, num: str, title: str, meta: str, color: str, w: int = W) -> str:
    return (
        f'<g class="fi">'
        f'<rect x="28" y="22" width="40" height="24" rx="7" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-opacity=".55"/>'
        f'<text x="48" y="38.5" class="m" font-size="12" font-weight="600" fill="{color}" text-anchor="middle">{e(num)}</text>'
        f'<text x="82" y="40" class="s" font-size="19" font-weight="650" fill="{t["text"]}" letter-spacing="-.2">{e(title)}</text>'
        f'<text x="{w-28}" y="39" class="m" font-size="11" fill="{t["muted"]}" text-anchor="end" letter-spacing=".4">{e(meta)}</text>'
        f'<line x1="28" y1="62" x2="{w-28}" y2="62" stroke="{t["border"]}"/>'
        f"</g>"
    )


def chip(t: dict, x: float, y: float, label: str, color: str | None = None, size: float = 11, cls: str = "", style: str = "") -> tuple[str, float]:
    pad = 8
    w = mw(label, size) + 2 * pad
    h = size + 11
    c = color or t["muted"]
    s = (
        f'<g class="{cls}" {style}><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h/2:.1f}" '
        f'fill="{c}" fill-opacity=".08" stroke="{c}" stroke-opacity=".45"/>'
        f'<text x="{x+pad:.1f}" y="{y+h/2+size*0.36:.1f}" class="m" font-size="{size}" fill="{c}">{e(label)}</text></g>'
    )
    return s, w


# --------------------------------------------------------------------------------------------
# 1. HERO
# --------------------------------------------------------------------------------------------
def signal_path(seed: int, n: int, x0: float, x1: float, ytop: float, ybot: float) -> tuple[str, float, list]:
    rnd = random.Random(seed)
    v, ys = 0.0, []
    for _ in range(n):
        v += rnd.gauss(0.22, 1.0)
        ys.append(v)
    sm = [sum(ys[max(0, i - 2): i + 3]) / len(ys[max(0, i - 2): i + 3]) for i in range(n)]
    lo, hi = min(sm), max(sm)
    pts = [(x0 + (x1 - x0) * i / (n - 1), ybot - (y - lo) / (hi - lo) * (ybot - ytop)) for i, y in enumerate(sm)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(n - 1))
    return d, length, pts


def typing_values(n: int, cw: float, cycle: float, t_type: tuple, t_erase: tuple) -> tuple[str, str]:
    """Discrete SMIL values/keyTimes: type n chars, hold, erase, stay empty till the cycle ends."""
    pts = [(0.0, 0.0)]
    a, b = t_type
    for k in range(1, n + 1):
        pts.append((a + (b - a) * k / n, k * cw))
    a, b = t_erase
    for k in range(n - 1, -1, -1):
        pts.append((a + (b - a) * (n - k) / n, k * cw))
    vals = ";".join(f"{v:.1f}" for _, v in pts)
    keys = ";".join(f"{tt / cycle:.4f}" for tt, _ in pts)
    return vals, keys


def hero(t: dict) -> str:
    H = 300
    d, L, pts = signal_path(seed=11, n=110, x0=36, x1=804, ytop=226, ybot=282)
    area = d + f" L804,{H-1} L36,{H-1} Z"
    hx, hy = pts[-1]

    # rotating role line ------------------------------------------------------------------------
    size, cw, tx, ty = 19, 19 * 0.6, 66, 198
    roles = [
        [("AI Engineer", t["teal"], 600), (" — evaluating & shipping LLM agents", t["text"], 400)],
        [("AI Quant Researcher", t["amber"], 600), (" — liquid, robust alpha research", t["text"], 400)],
    ]
    cycle = 12.0
    role_svg = []
    for i, parts in enumerate(roles):
        txt = "".join(p for p, _, _ in parts)
        n = len(txt)
        vals, keys = typing_values(n, cw, cycle, (0.15, 0.15 + n * 0.045), (5.2, 5.2 + n * 0.012))
        xvals = ";".join(f"{tx + float(v):.1f}" for v in vals.split(";"))
        begin = 1.3 + i * 6.0
        tspans = "".join(f'<tspan fill="{c}" font-weight="{wgt}">{e(p)}</tspan>' for p, c, wgt in parts)
        role_svg.append(
            f'<clipPath id="rc{i}"><rect x="{tx}" y="{ty-20}" width="0" height="28">'
            f'<animate attributeName="width" values="{vals}" keyTimes="{keys}" dur="{cycle}s" begin="{begin}s" '
            f'calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'
            f'<text x="{tx}" y="{ty}" class="m" font-size="{size}" clip-path="url(#rc{i})">{tspans}</text>'
            f'<g visibility="hidden"><set attributeName="visibility" to="visible" begin="{begin}s"/>'
            f'<animate attributeName="visibility" values="visible;hidden" keyTimes="0;0.5" dur="{cycle}s" '
            f'begin="{begin}s" calcMode="discrete" repeatCount="indefinite"/>'
            f'<rect class="blink" x="{tx}" y="{ty-16}" width="10" height="21" rx="1.5" fill="{t["teal"] if i == 0 else t["amber"]}">'
            f'<animate attributeName="x" values="{xvals}" keyTimes="{keys}" dur="{cycle}s" begin="{begin}s" '
            f'calcMode="discrete" repeatCount="indefinite"/></rect></g>'
        )

    chip_txt = "AIAC 2.0  ·  GLOBAL #5  ·  VIETNAM #1"
    chip_w = mw(chip_txt, 11.5, 1.0) + 40
    chip_x = W - 28 - chip_w

    css = font_css(sans=True, mono=True, vi=True) + f"""
@keyframes drift{{0%{{transform:translate(0,0)}}50%{{transform:translate(-26px,14px)}}100%{{transform:translate(0,0)}}}}
@keyframes drift2{{0%{{transform:translate(0,0)}}50%{{transform:translate(30px,-10px)}}100%{{transform:translate(0,0)}}}}
@keyframes march{{to{{stroke-dashoffset:-24}}}}
.g1{{animation:drift 14s ease-in-out infinite}} .g2{{animation:drift2 17s ease-in-out infinite}}
.ants{{animation:march 1.6s linear infinite}}
"""
    body = [
        frame(t, W, H, rx=18),
        f'<defs>'
        f'<radialGradient id="gt"><stop offset="0" stop-color="{t["teal"]}" stop-opacity="{t["glow"]}"/><stop offset="1" stop-color="{t["teal"]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="ga"><stop offset="0" stop-color="{t["amber"]}" stop-opacity="{t["glow"]*0.8:.2f}"/><stop offset="1" stop-color="{t["amber"]}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="af" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["amber"]}" stop-opacity=".28"/><stop offset="1" stop-color="{t["amber"]}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="lf" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["amber"]}" stop-opacity=".25"/><stop offset=".6" stop-color="{t["amber"]}"/><stop offset="1" stop-color="{t["amber"]}"/></linearGradient>'
        # name: reveal wipe + travelling sheen
        f'<linearGradient id="rv" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff"/><stop offset=".86" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
        f'<mask id="nm"><rect x="-900" y="60" width="1000" height="110" fill="url(#rv)">'
        f'<animate attributeName="x" from="-900" to="20" dur="1.5s" begin=".15s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".3 .1 .2 1"/></rect></mask>'
        f'<linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="0" y2="0">'
        f'<stop offset="0" stop-color="{t["text"]}"/><stop offset=".42" stop-color="{t["text"]}"/>'
        f'<stop offset=".5" stop-color="{t["teal"]}"/><stop offset=".58" stop-color="{t["text"]}"/><stop offset="1" stop-color="{t["text"]}"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="-200 0;1100 0;1100 0" keyTimes="0;.35;1" dur="9s" begin="2s" repeatCount="indefinite"/>'
        f'</linearGradient>'
        f'<clipPath id="cc"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18"/></clipPath>'
        f'</defs>',
        f'<g clip-path="url(#cc)">'
        f'<circle class="g1" cx="700" cy="40" r="260" fill="url(#gt)"/>'
        f'<circle class="g2" cx="90" cy="300" r="230" fill="url(#ga)"/>'
        f'<path d="{area}" fill="url(#af)" opacity="0"><animate attributeName="opacity" values="0;1" dur="1.4s" begin="2.2s" fill="freeze"/></path>'
        f'<line class="ants" x1="36" y1="{H-14}" x2="804" y2="{H-14}" stroke="{t["faint"]}" stroke-dasharray="2 10" stroke-linecap="round"/>'
        f'<path d="{d}" stroke="url(#lf)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}">'
        f'<animate attributeName="stroke-dashoffset" values="{L:.0f};0" dur="2.6s" begin=".5s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".45 .05 .35 1"/></path>'
        f'<g opacity="0"><set attributeName="opacity" to="1" begin=".5s"/>'
        f'<animateMotion path="{d}" dur="2.6s" begin=".5s" keyPoints="0;1" keyTimes="0;1" calcMode="spline" keySplines=".45 .05 .35 1" fill="freeze"/>'
        f'<circle class="ping" r="4" fill="{t["amber"]}"/><circle r="4" fill="{t["amber"]}"/></g>'
        f'<text x="{hx-12:.0f}" y="{min(hy-14, 236):.0f}" class="m" opacity="0" font-size="10.5" fill="{t["muted"]}" text-anchor="end" letter-spacing="1">OUT-OF-SAMPLE &gt; IN-SAMPLE<animate attributeName="opacity" values="0;1" dur=".8s" begin="3.1s" fill="freeze"/></text>'
        f'</g>',
        # top row
        f'<g class="fi" {delay(.1)}>'
        f'<circle class="ping" cx="40" cy="36" r="3.5" fill="{t["teal"]}"/><circle cx="40" cy="36" r="3.5" fill="{t["teal"]}"/>'
        f'<text x="52" y="40" class="m" font-size="11.5" fill="{t["muted"]}" letter-spacing="1.2">HANOI, VIETNAM  ·  GMT+7</text>'
        f'<rect x="{chip_x:.1f}" y="22" width="{chip_w:.1f}" height="28" rx="14" fill="{t["amber"]}" fill-opacity=".10" stroke="{t["amber"]}" stroke-opacity=".5"/>'
        f'<path d="M{chip_x+16:.1f} 41 l5 -10 l5 10 z" fill="{t["amber"]}"/>'
        f'<text x="{chip_x+30:.1f}" y="40" class="m" font-size="11.5" font-weight="600" fill="{t["amber"]}" letter-spacing="1">{e(chip_txt)}</text>'
        f'</g>',
        f'<text x="38" y="84" class="m fi" {delay(.2)} font-size="14" fill="{t["muted"]}" letter-spacing="1">// lê huy hồng nhật</text>',
        f'<g mask="url(#nm)"><text x="34" y="148" class="s" font-size="60" font-weight="800" letter-spacing="-1.8" fill="url(#sh)">LE HUY HONG NHAT</text></g>',
        f'<rect x="-10" y="96" width="2.5" height="66" fill="{t["teal"]}" opacity="0">'
        f'<animate attributeName="x" from="-10" to="812" dur="1.5s" begin=".15s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".3 .1 .2 1"/>'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="1.5s" begin=".15s" fill="freeze"/></rect>',
        f'<text x="38" y="{ty}" class="m" font-size="{size}" font-weight="700" fill="{t["muted"]}">$</text>',
        *role_svg,
    ]
    return svg(W, H, "Le Huy Hong Nhat — AI Engineer & AI Quant Researcher",
               "Animated header. AI Engineer evaluating and shipping LLM agents; AI Quant Researcher doing alpha research, "
               "Global Rank #5 and Vietnam #1 in AI Alpha Competition 2.0. Hanoi, Vietnam.", css, "".join(body))


# --------------------------------------------------------------------------------------------
# 2. TICKER TAPE
# --------------------------------------------------------------------------------------------
TICKER = [
    ("AIAC 2.0 GLOBAL RANK", "#5", "up"),
    ("VIETNAM RANK", "#1", "up"),
    ("FIELD", "~10,000", None),
    ("FOCUS", "AGENT EVALS", None),
    ("TRACING", "LANGFUSE", None),
    ("GATE", "LLM-AS-JUDGE", None),
    ("FOCUS", "ALPHA RESEARCH", None),
    ("BIAS CHECK", "OUT-OF-SAMPLE", None),
    ("CORE", "PYTHON · SQL", None),
    ("OPEN SOURCE", "DOCS-SKILLS", None),
]


def ticker(t: dict) -> str:
    H, size, ls = 44, 12, 0.6
    cw = size * 0.6 + ls
    y = H / 2 + size * 0.36
    items, x = [], 0.0
    for label, val, arrow in TICKER:
        items.append(f'<text x="{x:.1f}" y="{y:.1f}" class="m" font-size="{size}" letter-spacing="{ls}" fill="{t["muted"]}">{e(label)}</text>')
        x += len(label) * cw + 10
        color = t["text"] if arrow is None else t["green"]
        items.append(f'<text x="{x:.1f}" y="{y:.1f}" class="m" font-size="{size}" letter-spacing="{ls}" font-weight="650" fill="{color}">{e(val)}</text>')
        x += len(val) * cw + 6
        if arrow:
            cy = H / 2
            pts = f"{x:.1f},{cy+4} {x+8:.1f},{cy+4} {x+4:.1f},{cy-4}" if arrow == "up" else f"{x:.1f},{cy-4} {x+8:.1f},{cy-4} {x+4:.1f},{cy+4}"
            items.append(f'<polygon points="{pts}" fill="{t["green"]}"/>')
            x += 10
        x += 18
        items.append(f'<rect x="{x:.1f}" y="{H/2-2.5}" width="5" height="5" transform="rotate(45 {x+2.5:.1f} {H/2})" fill="{t["faint"]}"/>')
        x += 23
    span = x
    strip = "".join(items)
    css = font_css(sans=False, mono=True) + f"""
@keyframes tape{{from{{transform:translateX(0)}}to{{transform:translateX(-{span:.1f}px)}}}}
.tape{{animation:tape {span/34:.1f}s linear infinite}}
"""
    body = (
        f'<defs><linearGradient id="fe" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset=".07" stop-color="#fff"/>'
        f'<stop offset=".93" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
        f'<mask id="fm"><rect width="{W}" height="{H}" fill="url(#fe)"/></mask></defs>'
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>'
        f'<g mask="url(#fm)"><g class="tape"><g transform="translate(24 0)">{strip}<g transform="translate({span:.1f} 0)">{strip}</g>'
        f'<g transform="translate({2*span:.1f} 0)">{strip}</g></g></g></g>'
    )
    desc = "Scrolling ticker: " + "; ".join(f"{a} {b}" for a, b, _ in TICKER)
    return svg(W, H, "Highlights ticker", desc, css, body)


# --------------------------------------------------------------------------------------------
# 3. WHOAMI TERMINAL
# --------------------------------------------------------------------------------------------
WHOAMI = [
    ("name", [("Lê Huy Hồng Nhật", "text")], ""),
    ("role", [("AI Engineer", "text"), (" · ", "muted"), ("agent evaluation & deployment", "teal")], ""),
    ("also", [("Quant Researcher", "text"), (" · ", "muted"), ("alpha research, part-time", "amber")], ""),
    ("edu", [("Engineer's Degree in IT", "text"), (" @ ", "muted"), ("PTIT", "blue")], ""),
    ("focus", [("agent evaluation · LLM tracing · alpha research", "text")], ""),
    ("creed", [("liquid, robust signals > in-sample fit", "text")], ""),
]


def whoami(t: dict) -> str:
    size, lh = 14, 27
    top = 36
    y0 = top + 38
    H = y0 + lh * (len(WHOAMI) + 1) + 14
    cmd = "whoami --verbose"
    prompt = [("nhat", "teal"), ("@", "muted"), ("hanoi", "teal"), (" ~ ", "blue"), ("$ ", "muted")]
    plen = sum(len(p) for p, _ in prompt)
    cw = size * 0.6
    cx = 28 + plen * cw
    vals, keys = typing_values(len(cmd), cw, 100.0, (0.5, 0.5 + len(cmd) * 0.06), (98.0, 99.0))
    out_start = 0.5 + len(cmd) * 0.06 + 0.25

    def prompt_tspans() -> str:
        return "".join(f'<tspan fill="{t[c]}">{e(p)}</tspan>' for p, c in prompt)

    rows = []
    for i, (key, parts, right) in enumerate(WHOAMI):
        y = y0 + lh * (i + 1)
        val = "".join(f'<tspan fill="{t[c]}">{e(p)}</tspan>' for p, c in parts)
        r = (f'<text x="{W-28}" y="{y}" class="m" font-size="12.5" fill="{t["muted"]}" text-anchor="end">{e(right)}</text>' if right else "")
        rows.append(
            f'<g opacity="0">{smil_in(out_start + i * 0.14)}'
            f'<text x="28" y="{y}" class="m" font-size="{size}" fill="{t["muted"]}">{e(key)}</text>'
            f'<text x="{28 + 9 * cw:.1f}" y="{y}" class="m" font-size="{size}">{val}</text>{r}'
            f'<line x1="{28 + 9 * cw:.1f}" y1="{y+9}" x2="{W-28}" y2="{y+9}" stroke="{t["grid"]}"/></g>'
        )
    last_y = y0 + lh * (len(WHOAMI) + 1)
    end_t = out_start + len(WHOAMI) * 0.14 + 0.3
    body = [
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["card"]}" stroke="{t["border"]}"/>',
        f'<path d="M1 {top}H{W-1}" stroke="{t["border"]}"/>',
        f'<path d="M14.5 .5H{W-14.5}A14 14 0 0 1 {W-.5} 14.5V{top}H.5V14.5A14 14 0 0 1 14.5 .5Z" fill="{t["card2"]}" stroke="{t["border"]}"/>',
        "".join(f'<circle cx="{22 + i * 18}" cy="18" r="5" stroke="{t["faint"]}" stroke-width="1.4"/>' for i in range(3)),
        f'<text x="{W/2}" y="22" class="m" font-size="11.5" fill="{t["muted"]}" text-anchor="middle">nhat@hanoi — zsh — whoami</text>',
        f'<text x="{W-24}" y="22" class="m" font-size="10.5" fill="{t["faint"]}" text-anchor="end">⌘ 1</text>',
        f'<clipPath id="cmdc"><rect x="{cx:.1f}" y="{y0-18}" width="0" height="26">'
        f'<animate attributeName="width" values="{vals}" keyTimes="{keys}" dur="100s" calcMode="discrete" fill="freeze"/></rect></clipPath>',
        f'<text x="28" y="{y0}" class="m" font-size="{size}">{prompt_tspans()}</text>',
        f'<text x="{cx:.1f}" y="{y0}" class="m" font-size="{size}" fill="{t["text"]}" clip-path="url(#cmdc)">{e(cmd)}</text>',
        *rows,
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{end_t:.2f}s"/><text x="28" y="{last_y}" class="m" font-size="{size}">{prompt_tspans()}</text>'
        f'<rect class="blink" x="{cx:.1f}" y="{last_y-13}" width="8.5" height="17" rx="1" fill="{t["teal"]}"/></g>',
    ]
    css = font_css(sans=False, mono=True, vi=True)
    desc = "Terminal: whoami. " + " | ".join(f"{k}: {''.join(p for p, _ in parts)} {r}".strip() for k, parts, r in WHOAMI)
    return svg(W, H, "whoami", desc, css, "".join(body))


# --------------------------------------------------------------------------------------------
# 4. MODE 01 — AGENT EVALUATION
# --------------------------------------------------------------------------------------------
EVAL_ROWS = ["functional suite", "integration suite", "golden set · LLM judge", "trace review", "regression check"]


def _vis(name: str, windows: list) -> str:
    """Opacity keyframes: visible only inside the given [on, off) percent windows of the cycle."""
    pts = []
    for on, off in windows:
        if on > 0:
            pts.append((on - 0.01, 0))
        pts.append((on, 1))
        pts.append((off - 0.01, 1))
        if off < 100:
            pts.append((off, 0))
    if pts[0][0] > 0:
        pts.insert(0, (0, 0))
    if pts[-1][0] < 100:
        pts.append((100, pts[-1][1]))
    body = "".join(f"{p:.2f}%{{opacity:{v}}}" for p, v in pts)
    return f"@keyframes {name}{{{body}}}"


def mode_agent(t: dict) -> str:
    H = 330
    T, A = t["teal"], t["amber"]
    x0, x1, y0, y1, r = 126, 396, 120, 256, 26
    loop = (f"M{x0+r},{y0} H{x1-r} A{r},{r} 0 0 1 {x1},{y0+r} V{y1-r} A{r},{r} 0 0 1 {x1-r},{y1} "
            f"H{x0+r} A{r},{r} 0 0 1 {x0},{y1-r} V{y0+r} A{r},{r} 0 0 1 {x0+r},{y0} Z")
    per = 2 * (x1 - x0 - 2 * r) + 2 * (y1 - y0 - 2 * r) + 2 * math.pi * r
    arc = math.pi * r / 4
    s2 = (x1 - x0 - 2 * r + arc) / per
    s3 = s2 + (2 * arc + y1 - y0 - 2 * r) / per
    s4 = s3 + (2 * arc + x1 - x0 - 2 * r) / per
    s1 = s4 + (2 * arc + y1 - y0 - 2 * r) / per
    cyc = 8.0
    stations = [
        ((x0, y0), "1", "Change the harness", "skills · prompts · flow", s1),
        ((x1, y0), "2", "Run the evals", "human-graded suites", s2),
        ((x1, y1), "3", "Judge & gate", "LLM-as-judge regression", s3),
        ((x0, y1), "4", "Trace & diagnose", "Langfuse · root cause", s4),
    ]
    st_svg, css = [], []
    for i, ((cx, cy), n, lab, sub, frac) in enumerate(stations):
        bw, bh = 194, 52
        css.append(f".st{i}{{animation:hl {cyc}s linear {frac * cyc - 0.35 - cyc:.2f}s infinite}}")
        st_svg.append(
            f'<g class="fu" {delay(0.3 + i * 0.12)}>'
            f'<rect class="st{i}" x="{cx-bw/2}" y="{cy-bh/2}" width="{bw}" height="{bh}" rx="11" fill="{t["card2"]}" stroke="{t["border"]}" stroke-width="1.3"/>'
            f'<circle cx="{cx-bw/2+20}" cy="{cy}" r="10" fill="{T}" fill-opacity=".14"/>'
            f'<text x="{cx-bw/2+20}" y="{cy+4}" class="m" font-size="11" font-weight="700" fill="{T}" text-anchor="middle">{n}</text>'
            f'<text x="{cx-bw/2+38}" y="{cy-3}" class="s" font-size="13" font-weight="600" fill="{t["text"]}">{e(lab)}</text>'
            f'<text x="{cx-bw/2+38}" y="{cy+13}" class="m" font-size="9.8" fill="{t["muted"]}">{e(sub)}</text></g>'
        )
    chev = lambda x, y, rot: f'<path d="M-4,-5 L3,0 L-4,5" transform="translate({x} {y}) rotate({rot})" stroke="{T}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/>'
    arrows = chev((x0 + x1) / 2, y0, 0) + chev(x1, (y0 + y1) / 2, 90) + chev((x0 + x1) / 2, y1, 180) + chev(x0, (y0 + y1) / 2, 270)

    # right panel: a looping eval run, statuses only (no numbers) --------------------------------
    px, pw, run_cyc = 520, 292, 9.0
    reset, gate_on = 90.0, 76.0
    rows = []
    for i, label in enumerate(EVAL_ROWS):
        y = 118 + i * 31
        run_on = 8 + i * 13
        ok_on = run_on + 7
        css.append(_vis(f"q{i}", [(0, run_on), (reset, 100)]) + f".q{i}{{animation:q{i} {run_cyc}s linear infinite}}")
        css.append(_vis(f"r{i}", [(run_on, ok_on)]) + f".r{i}{{animation:r{i} {run_cyc}s linear infinite}}")
        css.append(_vis(f"k{i}", [(ok_on, reset)]) + f".k{i}{{animation:k{i} {run_cyc}s linear infinite}}")
        ix, iy, rx_ = px + 16, y - 4, px + pw - 14
        rows.append(
            f'<g class="fu" {delay(0.4 + i * 0.08)}>'
            f'<rect x="{px}" y="{y-17}" width="{pw}" height="26" rx="7" fill="{t["card2"]}" stroke="{t["border"]}"/>'
            f'<text x="{px+32}" y="{y}" class="m" font-size="11.5" fill="{t["text"]}">{e(label)}</text>'
            # queued
            f'<g class="q{i}" opacity="0"><circle cx="{ix}" cy="{iy}" r="5" stroke="{t["faint"]}" stroke-width="1.5"/>'
            f'<text x="{rx_}" y="{y}" class="m" font-size="10.5" fill="{t["faint"]}" text-anchor="end">queued</text></g>'
            # running
            f'<g class="r{i}" opacity="0"><rect x="{px+.5}" y="{y-16.5}" width="{pw-1}" height="25" rx="6.5" stroke="{A}" stroke-opacity=".7"/>'
            f'<circle cx="{ix}" cy="{iy}" r="5" stroke="{A}" stroke-opacity=".3" stroke-width="1.5"/>'
            f'<path class="spin" d="M{ix},{iy-5} A5,5 0 0 1 {ix+5},{iy}" stroke="{A}" stroke-width="1.6" stroke-linecap="round"/>'
            f'<text x="{rx_}" y="{y}" class="m" font-size="10.5" fill="{A}" text-anchor="end">running</text></g>'
            # pass (also the static / reduced-motion state)
            f'<g class="k{i}"><circle cx="{ix}" cy="{iy}" r="6" fill="{T}"/>'
            f'<path d="M{ix-2.6},{iy} l1.8,1.9 l3.4,-3.6" stroke="{t["card"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<text x="{rx_}" y="{y}" class="m" font-size="10.5" font-weight="600" fill="{T}" text-anchor="end">pass</text></g></g>'
        )
    css.append(_vis("gh", [(0, gate_on), (reset, 100)]) + f".gh{{animation:gh {run_cyc}s linear infinite}}")
    css.append(_vis("gp", [(gate_on, reset)]) + f".gp{{animation:gp {run_cyc}s linear infinite}}")
    css.append(f"@keyframes bar{{0%{{transform:scaleX(0)}}{gate_on}%,{reset}%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}"
               f".bar{{transform-box:fill-box;transform-origin:left center;animation:bar {run_cyc}s linear infinite}}")
    gy = 118 + len(EVAL_ROWS) * 31 + 8
    gate = (
        f'<g class="fu" {delay(0.9)}>'
        f'<rect x="{px}" y="{gy}" width="{pw}" height="4" rx="2" fill="{t["grid"]}"/>'
        f'<rect class="bar" x="{px}" y="{gy}" width="{pw}" height="4" rx="2" fill="{T}"/>'
        f'<text x="{px}" y="{gy+26}" class="m" font-size="10.5" fill="{t["muted"]}" letter-spacing="1">RELEASE GATE</text>'
        f'<g class="gh" opacity="0"><rect x="{px+pw-74}" y="{gy+11}" width="74" height="22" rx="11" fill="{A}" fill-opacity=".12" stroke="{A}" stroke-opacity=".6"/>'
        f'<text x="{px+pw-37}" y="{gy+26}" class="m" font-size="11" font-weight="700" fill="{A}" text-anchor="middle" letter-spacing="1">HOLD</text></g>'
        f'<g class="gp"><rect x="{px+pw-74}" y="{gy+11}" width="74" height="22" rx="11" fill="{T}" fill-opacity=".14" stroke="{T}" stroke-opacity=".7"/>'
        f'<text x="{px+pw-37}" y="{gy+26}" class="m" font-size="11" font-weight="700" fill="{T}" text-anchor="middle" letter-spacing="1">SHIP</text></g></g>'
    )

    style = font_css(sans=True, mono=True) + f"""
@keyframes hl{{0%{{stroke:{t["border"]}}}4%{{stroke:{T}}}16%{{stroke:{T}}}26%,100%{{stroke:{t["border"]}}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.spin{{transform-box:view-box;animation:spin .8s linear infinite}}
{''.join(css)}
"""
    # the spinner rotates around its own ring centre
    body_rows = []
    for i, s in enumerate(rows):
        y = 118 + i * 31
        body_rows.append(s.replace('class="spin"', f'class="spin" style="transform-origin:{px+16}px {y-4}px"'))
    body = [
        frame(t, W, H),
        header(t, "01", "Agent evaluation & deployment", "AI ENGINEER", T),
        f'<path d="{loop}" stroke="{t["border"]}" stroke-width="1.5" stroke-dasharray="3 5"/>',
        arrows,
        f'<text x="{(x0+x1)/2}" y="182" class="m" font-size="10" fill="{t["muted"]}" text-anchor="middle" letter-spacing="1.5">EVAL LOOP</text>',
        f'<text x="{(x0+x1)/2}" y="205" class="s" font-size="16" font-weight="700" fill="{T}" text-anchor="middle">every change</text>',
        f'<g><animateMotion path="{loop}" dur="{cyc}s" repeatCount="indefinite"/><circle r="9" fill="{T}" opacity=".18"/><circle r="4.5" fill="{T}"/></g>',
        f'<g opacity=".45"><animateMotion path="{loop}" dur="{cyc}s" begin="-.12s" repeatCount="indefinite"/><circle r="3" fill="{T}"/></g>',
        f'<g opacity=".2"><animateMotion path="{loop}" dur="{cyc}s" begin="-.24s" repeatCount="indefinite"/><circle r="2.4" fill="{T}"/></g>',
        *st_svg,
        f'<text x="28" y="{H-22}" class="m" font-size="10.5" fill="{t["muted"]}" letter-spacing="1">NOTHING SHIPS UNTIL THE LOOP COMES BACK GREEN</text>',
        f'<text x="{px}" y="90" class="m fu" {delay(.3)} font-size="10.5" fill="{t["muted"]}" letter-spacing="1">EVAL RUN</text>',
        f'<g class="fu" {delay(.3)}><circle class="ping" cx="{px+pw-46}" cy="86" r="3" fill="{T}"/><circle cx="{px+pw-46}" cy="86" r="3" fill="{T}"/>'
        f'<text x="{px+pw}" y="90" class="m" font-size="10.5" fill="{T}" text-anchor="end" letter-spacing="1">LIVE</text></g>',
        *body_rows,
        gate,
    ]
    desc = ("Mode 01, agent evaluation and deployment: every harness change runs an eval loop of change, run "
            "human-graded suites, LLM-as-judge regression gate, and Langfuse tracing to root cause; an eval run "
            "moves functional, integration, golden-set, trace-review and regression checks from queued to pass "
            "before the release gate opens.")
    return svg(W, H, "Mode 01 — Agent evaluation & deployment", desc, style, "".join(body))


# --------------------------------------------------------------------------------------------
# 5. MODE 02 — ALPHA RESEARCH
# --------------------------------------------------------------------------------------------
STAGES = [
    ("HYPOTHESIS", "economic prior", "before any search"),
    ("GENERATE", "expression", "generation"),
    ("TRACK", "operator-usage", "tracking"),
    ("SIMULATE", "large-scale", "simulations"),
    ("FILTER", "liquidity · turnover", "· coverage"),
    ("SELECT", "predicted OS perf,", "low pool correlation"),
    ("SUBMIT", "tradable,", "high-bar alphas"),
]


def mode_alpha(t: dict) -> str:
    H = 344
    A, T = t["amber"], t["teal"]
    rail = 156
    xs = [56 + i * (728 / 6) for i in range(7)]
    X0, X6 = xs[0], xs[-1]
    css_p, parts = [], []
    rnd = random.Random(5)
    fates = [3] * 4 + [4] * 7 + [5] * 5 + [6] * 2
    rnd.shuffle(fates)
    cyc, travel = 9.0, 78.0  # seconds per cycle, % of cycle spent travelling X0 -> X6
    for i, f in enumerate(fates):
        y0 = rnd.uniform(-26, 26)
        yat = lambda x: y0 * (1 - 0.9 * (x - X0) / (X6 - X0))
        pct = lambda x: (x - X0) / (X6 - X0) * travel
        kf = [f"0%{{transform:translate({X0:.1f}px,{rail+y0:.1f}px);opacity:0;fill:{t['muted']}}}",
              f"3%{{opacity:1}}"]
        for k in range(1, f + 1):
            kf.append(f"{pct(xs[k]):.1f}%{{transform:translate({xs[k]:.1f}px,{rail+yat(xs[k]):.1f}px);fill:{A if k >= 5 else t['muted']}}}")
        p = pct(xs[f])
        if f < 6:
            kf.append(f"{p+1:.1f}%{{fill:{t['red']};opacity:1}}")
            kf.append(f"{p+8:.1f}%{{transform:translate({xs[f]+10:.1f}px,{rail+yat(xs[f])+38:.1f}px);opacity:0;fill:{t['red']}}}")
        else:
            kf.append(f"{p+1:.1f}%{{opacity:1;fill:{A}}}")
            kf.append(f"{p+9:.1f}%{{transform:translate({X6+22:.1f}px,{rail:.1f}px);opacity:0;fill:{A}}}")
        kf.append("100%{opacity:0}")
        css_p.append(f"@keyframes p{i}{{{''.join(kf)}}} .p{i}{{animation:p{i} {cyc}s linear {-i*cyc/len(fates):.2f}s infinite}}")
        parts.append(f'<circle class="p{i}" r="{4 if f == 6 else 3.2}" fill="{t["muted"]}" opacity="0"/>')

    st = []
    for i, (name, l1, l2) in enumerate(STAGES):
        x = xs[i]
        gate = name in ("FILTER", "SELECT")
        node = (f'<rect x="{x-3}" y="{rail-22}" width="6" height="44" rx="3" fill="{A}" fill-opacity=".22" stroke="{A}" stroke-opacity=".8"/>'
                if gate else
                f'<circle cx="{x}" cy="{rail}" r="{7 if i == 6 else 5.5}" fill="{A if i == 6 else t["card"]}" stroke="{A}" stroke-width="1.6"/>')
        st.append(
            f'<g class="fu" {delay(0.2 + i * 0.1)}>{node}'
            f'<text x="{x}" y="96" class="m" font-size="9.5" fill="{t["faint"]}" text-anchor="middle">S{i+1}</text>'
            f'<text x="{x}" y="112" class="m" font-size="10.5" font-weight="600" fill="{A if gate or i in (0, 6) else t["text"]}" text-anchor="middle" letter-spacing="1">{name}</text>'
            f'<text x="{x}" y="204" class="s" font-size="11.5" fill="{t["muted"]}" text-anchor="middle">{e(l1)}</text>'
            f'<text x="{x}" y="219" class="s" font-size="11.5" fill="{t["muted"]}" text-anchor="middle">{e(l2)}</text></g>'
        )
    funnel = (f'<polygon points="{X0},{rail-36} {X6},{rail-8} {X6},{rail+8} {X0},{rail+36}" fill="{A}" fill-opacity=".06"/>'
              f'<path d="M{X0},{rail-36} L{X6},{rail-8} M{X0},{rail+36} L{X6},{rail+8}" stroke="{A}" stroke-opacity=".3" stroke-dasharray="3 5"/>'
              f'<line x1="{X0}" y1="{rail}" x2="{X6}" y2="{rail}" stroke="{t["border"]}" stroke-width="1.2"/>')

    stats = [("#5", "GLOBAL RANK · AIAC 2.0", A), ("#1", "IN VIETNAM", t["text"]), ("~10k", "PARTICIPANTS", t["text"])]
    st_svg = []
    for i, (big, small, c) in enumerate(stats):
        x = (28, 206, 306)[i]
        st_svg.append(
            f'<g class="fu" {delay(1.0 + i * 0.15)}>'
            f'<text x="{x}" y="296" class="s" font-size="42" font-weight="750" fill="{c}" letter-spacing="-1.5">{e(big)}</text>'
            f'<text x="{x+2}" y="318" class="m" font-size="10" fill="{t["muted"]}" letter-spacing="1">{e(small)}</text></g>'
        )
    quote = ["Constrain the search with economic hypotheses",
             "first: less data-mining bias than unconstrained",
             "random search, and alphas that stay tradable."]
    q = "".join(f'<text x="468" y="{272 + i * 19}" class="s" font-size="13.5" fill="{t["text"] if i == 0 else t["muted"]}">{e(s)}</text>' for i, s in enumerate(quote))

    css = font_css(sans=True, mono=True) + "".join(css_p)
    body = [
        frame(t, W, H),
        header(t, "02", "Systematic alpha research", "QUANT RESEARCHER · PART-TIME", A),
        funnel, *parts, *st,
        f'<line x1="28" y1="240" x2="{W-28}" y2="240" stroke="{t["border"]}" stroke-dasharray="2 4"/>',
        *st_svg,
        f'<g class="fu" {delay(1.5)}><rect x="452" y="258" width="3" height="58" rx="1.5" fill="{A}"/>{q}</g>',
    ]
    desc = ("Mode 02, systematic alpha research: an automated pipeline from economic hypothesis, expression "
            "generation, operator-usage tracking and simulation to liquidity/turnover/coverage filters and a selection model "
            "that ranks alphas by predicted out-of-sample performance and low correlation to the pool. AI Alpha Competition "
            "2.0: Global Rank #5, #1 in Vietnam, of about 10,000 participants.")
    return svg(W, H, "Mode 02 — Systematic alpha research", desc, css, "".join(body))


# --------------------------------------------------------------------------------------------
# 6. STACK AS A PERIODIC TABLE
# --------------------------------------------------------------------------------------------
GROUPS = [
    ("LANGUAGES", "blue", [("Py", "Python"), ("Sq", "SQL")]),
    ("LLM & AGENTS", "teal", [("Ev", "Agent evals"), ("Lj", "LLM-as-judge"), ("Lf", "Langfuse"), ("Rg", "RAG"),
                              ("Lc", "LangChain"), ("Sk", "Prompt/skills")]),
    ("MACHINE LEARNING", "violet", [("Pt", "PyTorch"), ("Hf", "Transformers"), ("Sl", "scikit-learn"), ("Cv", "OpenCV")]),
    ("QUANT & MATH", "amber", [("Ar", "Alpha research"), ("Bt", "Backtesting"), ("Os", "OS validation"), ("Np", "NumPy"),
                               ("Pd", "Pandas"), ("Ps", "Prob & stats"), ("La", "Lin. algebra")]),
    ("ENGINEERING", "green", [("Fa", "FastAPI"), ("Dk", "Docker"), ("Rq", "RabbitMQ"), ("Aw", "AWS"), ("Gt", "Git"),
                              ("Ch", "ChromaDB"), ("My", "MySQL")]),
]


def stack(t: dict) -> str:
    tw, th, gap, rowh = 86, 60, 6, 70
    gx = 168
    top = 84
    H = top + rowh * len(GROUPS) + 16
    tiles, idx = [], 0
    labels = []
    for r, (gname, ck, items) in enumerate(GROUPS):
        c = t[ck]
        y = top + r * rowh
        labels.append(
            f'<g class="fi" {delay(0.1 + r * 0.1)}><rect x="28" y="{y+th/2-5}" width="3" height="10" rx="1.5" fill="{c}"/>'
            f'<text x="38" y="{y+th/2+4}" class="m" font-size="10.5" font-weight="600" fill="{c}" letter-spacing="1">{e(gname)}</text>'
            f'<text x="38" y="{y+th/2+18}" class="m" font-size="9.5" fill="{t["faint"]}">{len(items)} elements</text></g>'
        )
        for k, (sym, name) in enumerate(items):
            idx += 1
            x = gx + k * (tw + gap)
            tiles.append(
                f'<g class="fu" {delay(0.25 + idx * 0.035)}>'
                f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="9" fill="{t["card2"]}" stroke="{t["border"]}"/>'
                f'<rect x="{x+10}" y="{y}" width="{tw-20}" height="2" rx="1" fill="{c}" fill-opacity=".9"/>'
                f'<text x="{x+7}" y="{y+14}" class="m" font-size="8.5" fill="{t["faint"]}">{idx:02d}</text>'
                f'<text x="{x+tw/2}" y="{y+36}" class="s" font-size="21" font-weight="700" fill="{c}" text-anchor="middle" letter-spacing="-.3">{e(sym)}</text>'
                f'<text x="{x+tw/2}" y="{y+52}" class="m" font-size="9" fill="{t["muted"]}" text-anchor="middle">{e(name)}</text></g>'
            )
    css = font_css(sans=True, mono=True) + f"""
@keyframes scan{{0%{{transform:translateX(0)}}60%,100%{{transform:translateX({W-gx+40}px)}}}}
.scan{{animation:scan 7s cubic-bezier(.5,0,.5,1) 1.8s infinite}}
"""
    body = [
        frame(t, W, H),
        header(t, "03", "Periodic table of my stack", f"{idx} ELEMENTS · {len(GROUPS)} GROUPS", t["violet"]),
        f'<defs><linearGradient id="sg" x1="0" x2="1"><stop offset="0" stop-color="{t["teal"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{t["teal"]}" stop-opacity=".10"/><stop offset="1" stop-color="{t["teal"]}" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="tc"><rect x="{gx}" y="{top-6}" width="{W-gx-20}" height="{H-top}"/></clipPath></defs>',
        *labels, *tiles,
        f'<g clip-path="url(#tc)"><rect class="scan" x="{gx-120}" y="{top-6}" width="110" height="{H-top}" fill="url(#sg)"/></g>',
    ]
    desc = "Stack: " + "; ".join(f"{g}: " + ", ".join(n for _, n in items) for g, _, items in GROUPS)
    return svg(W, H, "Periodic table of my stack", desc, css, "".join(body))


# --------------------------------------------------------------------------------------------
# 7. PROJECT CARDS (two per row)
# --------------------------------------------------------------------------------------------
PROJECTS = [
    ("docs-skills", "P/01", "Agent Skills for real docs", "LeHuyHongNhat/docs-skills", "teal",
     ["Four Agent Skills that let Claude, Codex, Cursor and", "Gemini CLI write PRDs, READMEs, ADRs and specs",
      "from diagrams, with a wording linter and visual QA."],
     ["Agent Skills", "Claude plugin", "EN / VI"]),
    ("Sentiment_Analysis_Using_PhoBert_Trained", "P/02", "Vietnamese sentiment, PhoBERT", "…/Sentiment_Analysis_Using_PhoBert_Trained", "violet",
     ["Fine-tunes PhoBERT on UIT-VSFC student feedback to", "label Vietnamese text as positive, negative or",
      "neutral, with Hugging Face Transformers."],
     ["PhoBERT", "Transformers", "NLP"]),
]


def project_card(t: dict, p: tuple, k: int) -> str:
    _, tag, title, path, ck, lines, tags = p
    w, h, rx = 412, 184, 14
    c = t[ck]
    perim = 2 * (w - 2 * rx) + 2 * (h - 2 * rx) + 2 * math.pi * rx
    body_lines = "".join(
        f'<text x="24" y="{104 + i * 18}" class="s" font-size="12.5" fill="{t["muted"]}">{e(s)}</text>' for i, s in enumerate(lines))
    cx, chips = 24.0, []
    for s in tags:
        cs, cw = chip(t, cx, 150, s, c, 10.5)
        chips.append(cs)
        cx += cw + 6
    css = font_css(sans=True, mono=True) + f"""
@keyframes run{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-{perim:.0f}}}}}
.run{{stroke-dasharray:110 {perim-110:.0f};animation:run 7s linear {-k*1.7:.1f}s infinite}}
"""
    body = (
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{rx}" fill="{t["card"]}" stroke="{t["border"]}"/>'
        f'<rect class="run" x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx-.5}" stroke="{c}" stroke-width="1.6" stroke-linecap="round" opacity=".9"/>'
        f'<text x="24" y="34" class="m" font-size="10.5" fill="{c}" letter-spacing="1">{tag}</text>'
        f'<text x="{24 + mw(tag, 10.5, 1) + 10:.1f}" y="34" class="m" font-size="10.5" fill="{t["faint"]}" letter-spacing="1">PUBLIC REPO</text>'
        f'<g transform="translate({w-40} 20)"><rect width="20" height="20" rx="6" fill="{c}" fill-opacity=".1"/>'
        f'<path d="M7 13 L13 7 M8.5 7 H13 V11.5" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></g>'
        f'<text x="24" y="62" class="s" font-size="19" font-weight="700" fill="{t["text"]}" letter-spacing="-.3">{e(title)}</text>'
        f'<text x="24" y="80" class="m" font-size="10" fill="{t["faint"]}">{e(path)}</text>'
        f'{body_lines}{"".join(chips)}'
    )
    return svg(w, h, title, f"{title} ({path}): {' '.join(lines)} Stack: {', '.join(tags)}.", css, body)


# --------------------------------------------------------------------------------------------
# 8. CONTACT PILLS + FOOTER
# --------------------------------------------------------------------------------------------
CONTACTS = [
    ("email", "EMAIL", "nhat050403@gmail.com", "teal"),
    ("linkedin", "LINKEDIN", "in/lenhat543-it", "blue"),
]


def contact(t: dict, kind: str, label: str, value: str, ck: str) -> str:
    w, h = 412, 64
    c = t[ck]
    if kind == "email":
        icon = (f'<rect x="-9" y="-6.5" width="18" height="13" rx="2.5" stroke="{c}" stroke-width="1.6"/>'
                f'<path d="M-8 -5 L0 1.5 L8 -5" stroke="{c}" stroke-width="1.6" stroke-linejoin="round"/>')
    else:
        icon = f'<text x="0" y="5" class="s" font-size="15" font-weight="800" fill="{c}" text-anchor="middle">in</text>'
    css = font_css(sans=True, mono=True)
    body = (
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{h/2-.5}" fill="{t["card"]}" stroke="{t["border"]}"/>'
        f'<circle class="ping" cx="34" cy="{h/2}" r="14" fill="{c}" fill-opacity=".25"/>'
        f'<circle cx="34" cy="{h/2}" r="18" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-opacity=".5"/>'
        f'<g transform="translate(34 {h/2})">{icon}</g>'
        f'<text x="66" y="27" class="m" font-size="10" fill="{t["muted"]}" letter-spacing="1.4">{label}</text>'
        f'<text x="66" y="46" class="s" font-size="16" font-weight="600" fill="{t["text"]}">{e(value)}</text>'
        f'<path d="M{w-40} {h/2-5} l5 5 l-5 5" stroke="{t["muted"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return svg(w, h, f"{label.title()}: {value}", f"{label.title()}: {value}", css, body)


SECTIONS = [
    ("section-repos", "04", "Open source", "CLICK A CARD TO OPEN THE REPO", "blue"),
    ("section-contact", "05", "Get in touch", "HANOI · GMT+7 · EN / VI", "teal"),
]


def section(t: dict, num: str, title: str, meta: str, ck: str) -> str:
    h = 66
    c = t[ck]
    css = font_css(sans=True, mono=True) + """
@keyframes sweep{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.sw{transform-box:fill-box;transform-origin:left center;animation:sweep 1.4s cubic-bezier(.3,.7,.2,1) .2s both}
"""
    body = (header(t, num, title, meta, c).replace(f'<line x1="28" y1="62"', f'<line x1="28" y1="62" class="sw"')
            .replace(f'stroke="{t["border"]}"/></g>', f'stroke="{t["border"]}"/><line class="sw" x1="28" y1="62" x2="160" y2="62" stroke="{c}" stroke-width="1.5"/></g>'))
    return svg(W, h, f"{num} {title}", f"Section: {title}", css, body)


def footer(t: dict) -> str:
    H = 150
    rnd = random.Random(3)
    n, bw = 84, 7
    bars, css_b = [], []
    for i in range(n):
        x = 24 + i * ((W - 48) / n)
        hh = 8 + abs(math.sin(i / 6.5)) * 26 + rnd.uniform(0, 14)
        c = t["amber"] if (i // 7) % 2 else t["teal"]
        dur = rnd.uniform(1.8, 3.4)
        bars.append(f'<rect class="v" style="animation-duration:{dur:.2f}s;animation-delay:{-rnd.uniform(0, 3):.2f}s" '
                    f'x="{x:.1f}" y="{H-10-hh:.1f}" width="{bw}" height="{hh:.1f}" rx="2" fill="{c}" fill-opacity=".22"/>')
    css = font_css(sans=True, mono=True) + """
@keyframes vol{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.35)}}
.v{transform-box:fill-box;transform-origin:center bottom;animation:vol 2.6s ease-in-out infinite}
"""
    body = (
        f'<defs><linearGradient id="ff" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#fff"/></linearGradient><mask id="fm"><rect width="{W}" height="{H}" fill="url(#ff)"/></mask></defs>'
        f'<g mask="url(#fm)">{"".join(bars)}</g>'
        f'<text x="{W/2}" y="44" class="s fu" font-size="22" font-weight="700" fill="{t["text"]}" text-anchor="middle" letter-spacing="-.4">'
        f'Build things that hold up <tspan fill="{t["teal"]}">out of sample</tspan>.</text>'
        f'<text x="{W/2}" y="70" class="m fu" {delay(.25)} font-size="11.5" fill="{t["muted"]}" text-anchor="middle" letter-spacing=".6">'
        f'evals for agents  ·  validation for alphas  ·  same discipline</text>'
    )
    return svg(W, H, "Build things that hold up out of sample",
               "Closing line: evals for agents, validation for alphas, same discipline.", css, body)


# --------------------------------------------------------------------------------------------
def main() -> None:
    for name, t in THEMES.items():
        out = ROOT / name
        out.mkdir(exist_ok=True)
        files = {
            "hero.svg": hero(t),
            "ticker.svg": ticker(t),
            "whoami.svg": whoami(t),
            "mode-agent.svg": mode_agent(t),
            "mode-alpha.svg": mode_alpha(t),
            "stack.svg": stack(t),
            "footer.svg": footer(t),
        }
        for k, p in enumerate(PROJECTS):
            files[f"project-{k+1}.svg"] = project_card(t, p, k)
        for fn, num, title, meta, ck in SECTIONS:
            files[f"{fn}.svg"] = section(t, num, title, meta, ck)
        for kind, label, value, ck in CONTACTS:
            files[f"contact-{kind}.svg"] = contact(t, kind, label, value, ck)
        for fn, s in files.items():
            (out / fn).write_text(s, encoding="utf-8")
        print(f"{name}: {len(files)} files, {sum(len(s) for s in files.values()) / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
