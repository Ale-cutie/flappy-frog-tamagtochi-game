"""Desenează broscuța Flappy Frog ca SVG, direct din Python (culorile din schiță)."""

PINK, LIGHT, BLUE, GREEN, DARK = "#FF8FA3", "#FFE4F8", "#CDE8E7", "#6BD767", "#3F1515"
S = f'stroke="{DARK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"'


def _eye(cx, cy, dx, dy, mood, petting):
    if petting or mood == "happy_closed":
        return f'<path d="M{cx-16} {cy+6} Q{cx} {cy-14} {cx+16} {cy+6}" fill="none" {S}/>'
    if mood == "sad":
        return f'<path d="M{cx-16} {cy} Q{cx} {cy+12} {cx+16} {cy}" fill="none" {S}/>'
    if mood == "sleepy":
        return f'<path d="M{cx-16} {cy} L{cx+16} {cy}" fill="none" {S}/>'
    eye = (f'<g transform="translate({dx:.1f},{dy:.1f})">'
           f'<ellipse cx="{cx}" cy="{cy}" rx="15" ry="22" fill="{DARK}" {S}/>'
           f'<ellipse cx="{cx-4}" cy="{cy-8}" rx="4" ry="7" fill="white"/>'
           f'<circle cx="{cx+5}" cy="{cy+8}" r="2.5" fill="white"/></g>')
    if mood == "sassy":  # pleoapă pe jumătate lăsată
        eye += f'<path d="M{cx-20} {cy-6} L{cx+20} {cy-12}" {S} fill="none"/>'
    return eye


def _mouth(mood, petting):
    if petting:
        return f'<path d="M185 232 L200 246 L215 232" fill="none" {S}/>'
    return {
        "happy": f'<path d="M185 232 L200 246 L215 232" fill="none" {S}/>',
        "sad": f'<path d="M185 244 Q200 228 215 244" fill="none" {S}/>',
        "sassy": f'<path d="M184 232 L216 230 L200 248 Z" fill="{LIGHT}" {S}/>',
        "hungry": f'<ellipse cx="200" cy="240" rx="9" ry="12" fill="{DARK}" {S}/>'
                  f'<path d="M209 248 q4 14 0 20" stroke="#8fd3ff" stroke-width="5" fill="none"/>',
        "sleepy": f'<ellipse cx="200" cy="240" rx="5" ry="4" fill="none" {S}/>',
    }[mood]


def _extra(mood, petting):
    heart = f'<path d="M200 118 C170 90 185 75 200 90 C215 75 230 90 200 118Z" fill="{PINK}" {S} transform="scale(.55) translate(163 90)"/>'
    if petting or mood == "happy":
        return heart + f'<path d="M95 120 l6 14 14 6 -14 6 -6 14 -6 -14 -14 -6 14 -6z" fill="{LIGHT}" {S}/>'
    if mood == "sad":
        return (f'<path d="M190 100 l8 -10 -6 -8 8 -8" fill="none" {S}/>'
                f'<path d="M232 190 q-6 14 0 20 q6 -6 0 -20" fill="#8fd3ff" stroke="{DARK}" stroke-width="3"/>')
    if mood == "sassy":
        return heart
    if mood == "hungry":
        return f'<text x="200" y="110" font-size="40" text-anchor="middle" fill="{DARK}">?</text>'
    if mood == "sleepy":
        return (f'<text x="262" y="120" font-size="34" fill="{DARK}" font-family="sans-serif">z</text>'
                f'<text x="284" y="92" font-size="26" fill="{DARK}" font-family="sans-serif">z</text>')
    return ""


def frog_svg(mood="happy", dx=0.0, dy=0.0, petting=False, bouncing=True, size=420):
    """dx, dy ∈ [-1, 1] = direcția cursorului față de broscuță (pupilele se mută)."""
    px, py = dx * 7, dy * 6
    spring = "".join(
        f'<ellipse cx="200" cy="{322 + i * 14}" rx="{70 - abs(i - 2) * 2}" ry="9" fill="none" {S}/>'
        for i in range(5))
    anim = "frog-bounce 1.6s ease-in-out infinite" if bouncing else "none"
    return f'''
<svg viewBox="0 0 400 400" width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
<style>
@keyframes frog-bounce {{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-14px)}}}}
@keyframes wing {{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(-8deg)}}}}
.frog{{animation:{anim}}} .wl{{transform-origin:130px 230px;animation:wing .5s infinite}}
.wr{{transform-origin:270px 230px;animation:wing .5s infinite reverse}}
</style>
<g>{spring}</g>
<g class="frog">
  <g class="wl"><path d="M135 225 C95 190 45 130 15 105 C70 100 125 150 150 205Z" fill="{LIGHT}" {S}/>
    <path d="M135 260 C100 250 70 255 62 280 C90 295 125 285 140 268Z" fill="{LIGHT}" {S}/></g>
  <g class="wr"><path d="M265 225 C305 190 355 130 385 105 C330 100 275 150 250 205Z" fill="{LIGHT}" {S}/>
    <path d="M265 260 C300 250 330 255 338 280 C310 295 275 285 260 268Z" fill="{LIGHT}" {S}/></g>
  <circle cx="148" cy="178" r="30" fill="{GREEN}" {S}/><circle cx="252" cy="178" r="30" fill="{GREEN}" {S}/>
  <path d="M105 318 C92 235 125 190 200 190 C275 190 308 235 295 318 Q200 330 105 318Z" fill="{GREEN}" {S}/>
  {_eye(148, 180, px, py, mood, petting)}{_eye(252, 180, px, py, mood, petting)}
  <circle cx="135" cy="248" r="20" fill="{PINK}" {S}/><circle cx="265" cy="248" r="20" fill="{PINK}" {S}/>
  {_mouth(mood, petting)}
  {_extra(mood, petting)}
</g></svg>'''
