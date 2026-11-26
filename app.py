"""Flappy Frog – pet virtual în cameră, 100% Python (NiceGUI)."""

import importlib.util
import json
import math
import pathlib
import random
import subprocess
import sys
import time
import urllib.parse
import webbrowser

from nicegui import app, ui
from frog import frog_svg, BLUE, LIGHT, PINK, DARK, GREEN
from brain import reply


PORT = 8081
HERE = pathlib.Path(__file__).parent
SAVE = pathlib.Path(__file__).with_name("pet.json")

MOODS = {
    "happy": "😊 Fericit",
    "sad": "😢 Trist",
    "sassy": "😏 Sassy",
    "hungry": "🍽️ Flămând",
    "sleepy": "😴 Somnoros"
}

MOOD_FX = {
    "happy": dict(happiness=40, energy=70),
    "sad": dict(happiness=10, energy=35),
    "sassy": dict(happiness=55, energy=60),
    "hungry": dict(food=10, happiness=30),
    "sleepy": dict(energy=10, happiness=45)
}

FOODS = [
    ("🍎", 12, 3),
    ("🍌", 14, 3),
    ("🍓", 8, 5),
    ("🥕", 10, 1),
    ("🥦", 10, 0),
    ("🍉", 16, 4),
    ("🍪", 6, 9),
    ("🪰", 8, 8)
]

TRAY_X0, TRAY_DX, TRAY_Y = 110, 82, 572
SOAP, SHOWER = (150, 572), (690, 190)

FROG_X, FROG_Y, FROG_S = 255, 230, 290

SLEEP_RATE = 2.5

STUDY_OPTIONS = [
    ("30 min", 30),
    ("1 oră", 60),
    ("1,5 ore", 90),
    ("2 ore", 120),
    ("2,5 ore", 150),
    ("3 ore", 180),
    ("⏱️ 1 min (test)", 1)
]

EMOJI = (
    "font-family:'Segoe UI Emoji',"
    "'Apple Color Emoji','Noto Color Emoji',sans-serif"
)


pet = {
    "mood": "happy",
    "happiness": 70,
    "energy": 70,
    "food": 70,
    "clean": 70
}

if SAVE.exists():
    pet.update(json.loads(SAVE.read_text()))

history = []

sc = {
    "mode": "feed",
    "drag": None,
    "mx": 400,
    "my": 300,
    "foam": [],
    "eat_until": 0.0,
    "refuse_until": 0.0,
    "popup": ("", 0.0),
    "sleeping": False,
    "study_end": 0.0,
    "study_total": 1.0,
    "last": time.time()
}

look = {
    "dx": 0.0,
    "dy": 0.0,
    "inside": 0,
    "t": 0.0
}

procs = {
    "widget": None
}


def save():
    SAVE.write_text(json.dumps(pet))


def clamp(k, d):
    pet[k] = max(0, min(100, pet[k] + d))


def set_mood(m):
    pet["mood"] = m

    for k, v in MOOD_FX[m].items():
        pet[k] = v

    save()


def room_svg():

    D = (
        f'stroke="{DARK}" stroke-width="4" '
        'stroke-linejoin="round" stroke-linecap="round"'
    )

    books = "".join(
        f'<rect x="{578 + i * 18}" y="{86 - h}" '
        f'width="15" height="{h}" fill="{c}" {D}/>'
        for i, (c, h) in enumerate([
            (PINK, 38),
            (GREEN, 46),
            (LIGHT, 34),
            ("#FFD27A", 42)
        ])
    )

    planks = "".join(
        f'<line x1="0" y1="{y}" x2="800" y2="{y}" '
        f'stroke="{DARK}" stroke-opacity=".15" '
        'stroke-width="3"/>'
        for y in (470, 510, 550, 590)
    )

    return f'''
<svg xmlns="http://www.w3.org/2000/svg"
     width="800" height="600" viewBox="0 0 800 600">

<defs>
    <pattern id="dots" width="40" height="40"
             patternUnits="userSpaceOnUse">

        <circle cx="10" cy="10" r="3"
                fill="#fff" fill-opacity=".5"/>

        <circle cx="30" cy="30" r="3"
                fill="{PINK}" fill-opacity=".25"/>
    </pattern>
</defs>

<rect width="800" height="600" fill="{BLUE}"/>
<rect width="800" height="440" fill="url(#dots)"/>

<rect y="440" width="800" height="160" fill="#F8CDB8"/>

{planks}

<rect y="428" width="800" height="16" fill="{LIGHT}" {D}/>

<!-- Fereastra -->

<rect x="80" y="60" width="180" height="200"
      rx="10" fill="#BDE7FF" {D}/>

<circle cx="205" cy="115" r="24" fill="#FFE27A" {D}/>

<ellipse cx="130" cy="170" rx="34" ry="14" fill="#fff"/>
<ellipse cx="150" cy="158" rx="22" ry="14" fill="#fff"/>

<line x1="170" y1="60" x2="170" y2="260" {D}/>
<line x1="80" y1="160" x2="260" y2="160" {D}/>

<rect x="66" y="256" width="208" height="16"
      rx="6" fill="{LIGHT}" {D}/>

<path d="M60 40 L60 250 Q95 235 110 250 L110 40Z"
      fill="{PINK}" {D}/>

<path d="M280 40 L280 250 Q245 235 230 250 L230 40Z"
      fill="{PINK}" {D}/>

<line x1="50" y1="40" x2="290" y2="40" {D}/>

<circle cx="50" cy="40" r="7" fill="{GREEN}" {D}/>
<circle cx="290" cy="40" r="7" fill="{GREEN}" {D}/>

<!-- Tablouri -->

<rect x="330" y="70" width="110" height="90"
      rx="8" fill="{LIGHT}" {D}/>

<rect x="344" y="84" width="82" height="62"
      rx="4" fill="#BDE7FF" {D}/>

<ellipse cx="385" cy="138" rx="26" ry="18"
         fill="{GREEN}" {D}/>

<circle cx="374" cy="116" r="7" fill="{GREEN}" {D}/>
<circle cx="396" cy="116" r="7" fill="{GREEN}" {D}/>

<path d="M385 100 c-12 -12 -4 -20 0 -13
         c4 -7 12 1 0 13z" fill="{PINK}" {D}/>

<rect x="470" y="100" width="60" height="60"
      rx="30" fill="{PINK}" {D}/>

<text x="500" y="140" font-size="34"
      text-anchor="middle" style="{EMOJI}">⭐</text>

<!-- Raft -->

<rect x="565" y="90" width="210" height="14"
      rx="5" fill="#C98F6B" {D}/>

{books}

<rect x="682" y="52" width="38" height="38"
      rx="6" fill="{PINK}" {D}/>

<circle cx="701" cy="40" r="20" fill="{GREEN}" {D}/>
<circle cx="745" cy="78" r="12" fill="{LIGHT}" {D}/>

<!-- Lampadar -->

<line x1="745" y1="270" x2="745" y2="420" {D}/>

<ellipse cx="745" cy="424" rx="28" ry="8" fill="{DARK}"/>

<path d="M712 270 L778 270 L762 215 L728 215Z"
      fill="{PINK}" {D}/>

<!-- Planta -->

<ellipse cx="62" cy="355" rx="26" ry="38"
         fill="{GREEN}" {D}/>

<ellipse cx="30" cy="378" rx="18" ry="30"
         fill="{GREEN}" transform="rotate(-25 30 378)" {D}/>

<ellipse cx="96" cy="378" rx="18" ry="30"
         fill="{GREEN}" transform="rotate(25 96 378)" {D}/>

<path d="M32 392 L92 392 L84 440 L40 440Z"
      fill="{PINK}" {D}/>

<!-- Covor -->

<ellipse cx="400" cy="505" rx="285" ry="62"
         fill="{LIGHT}" {D}/>

<ellipse cx="400" cy="505" rx="235" ry="46"
         fill="none" stroke="{PINK}"
         stroke-width="6" stroke-dasharray="14 12"/>

</svg>
'''


ROOM_URI = (
    "data:image/svg+xml;utf8,"
    + urllib.parse.quote(room_svg())
)


def over_frog(x, y):

    return (
        ((x - 400) / 150) ** 2
        + ((y - 415) / 135) ** 2
        <= 1
    )


def render():

    t = now = time.time()

    eating = now < sc["eat_until"]
    refusing = now < sc["refuse_until"]
    sleeping = sc["sleeping"]
    studying = sc["study_end"] > 0

    d = sc["drag"]
    mx = sc["mx"]
    my = sc["my"]

    rubbing = (
        d is not None
        and d[0] == "soap"
        and over_frog(mx, my)
    )

    showering = d is not None and d[0] == "shower"

    petting = (
        eating
        or rubbing
        or (
            d is None
            and over_frog(mx, my)
            and sc["mode"] == "feed"
        )
    ) and not refusing and not sleeping

    if petting and not eating and d is None:
        clamp("happiness", 0.08)

    dx = max(-1, min(1, (mx - 400) / 250))
    dy = max(-1, min(1, (my - 340) / 200))

    if studying:
        dx, dy = 0.3, 0.9

    if eating:
        bob = math.sin(t * 14) * 9
    elif sleeping:
        bob = math.sin(t * 1.2) * 4
    else:
        bob = math.sin(t * 3) * 6

    shake = math.sin(t * 35) * 9 if refusing else 0
    flap = math.sin(t * 9) * 9

    mood = (
        "sleepy" if sleeping
        else "sad" if refusing
        else pet["mood"]
    )

    f = frog_svg(
        mood,
        dx,
        dy,
        petting,
        False,
        FROG_S
    ).strip()

    f = f.replace(
        "<svg ",
        f'<svg x="{FROG_X + shake:.1f}" '
        f'y="{FROG_Y + bob:.1f}" ',
        1
    )

    f = f.replace(
        '<g class="wl">',
        f'<g transform="rotate({flap:.1f} 130 230)">'
    )

    f = f.replace(
        '<g class="wr">',
        f'<g transform="rotate({-flap:.1f} 270 230)">'
    )

    out = []

    # Camera pe timpul noptii

    if sleeping:

        out.append(
            '<rect width="800" height="600" '
            'fill="#1d2b6b" fill-opacity=".5"/>'

            '<circle cx="205" cy="115" r="27" fill="#3b4a9c"/>'

            f'<text x="205" y="116" font-size="40" '
            'text-anchor="middle" dominant-baseline="central" '
            f'style="{EMOJI}">🌙</text>'

            '<circle cx="125" cy="95" r="3" fill="#fff"/>'
            '<circle cx="235" cy="205" r="3" fill="#fff"/>'
            '<circle cx="110" cy="215" r="2" fill="#fff"/>'
            '<circle cx="150" cy="130" r="2" fill="#fff"/>'
        )

    out.append(f)

    # Ochelari si carte pentru Study

    if studying and not sleeping:

        k = FROG_S / 400
        fx = FROG_X + shake
        fy = FROG_Y + bob

        lx = fx + 148 * k
        rx = fx + 252 * k
        ey = fy + 180 * k

        out.append(
            f'<circle cx="{lx:.0f}" cy="{ey:.0f}" r="25" '
            'fill="#fff" fill-opacity=".3" '
            f'stroke="{DARK}" stroke-width="5"/>'

            f'<circle cx="{rx:.0f}" cy="{ey:.0f}" r="25" '
            'fill="#fff" fill-opacity=".3" '
            f'stroke="{DARK}" stroke-width="5"/>'

            f'<path d="M{lx + 25:.0f} {ey - 4:.0f} '
            f'Q{(lx + rx) / 2:.0f} {ey - 14:.0f} '
            f'{rx - 25:.0f} {ey - 4:.0f}" '
            f'fill="none" stroke="{DARK}" stroke-width="5"/>'

            f'<path d="M{lx - 25:.0f} {ey - 2:.0f} '
            f'L{lx - 40:.0f} {ey - 10:.0f} '
            f'M{rx + 25:.0f} {ey - 2:.0f} '
            f'L{rx + 40:.0f} {ey - 10:.0f}" '
            f'stroke="{DARK}" stroke-width="5" '
            'stroke-linecap="round"/>'
        )

        out.append(
            '<path d="M478 488 L527 480 L527 510 L478 518Z" '
            f'fill="#fff" stroke="{DARK}" stroke-width="4" '
            'stroke-linejoin="round"/>'

            '<path d="M527 480 L576 488 L576 518 L527 510Z" '
            f'fill="#fff" stroke="{DARK}" stroke-width="4" '
            'stroke-linejoin="round"/>'

            '<path d="M488 496 L518 491 M488 504 L518 499 '
            'M536 491 L566 496 M536 499 L566 504" '
            f'stroke="{PINK}" stroke-width="3" '
            'stroke-linecap="round"/>'
        )

        wob = math.sin(t * 6) * 12

        out.append(
            f'<text x="566" y="478" font-size="34" '
            'text-anchor="middle" '
            f'transform="rotate({wob:.0f} 566 478)" '
            f'style="{EMOJI}">✏️</text>'
        )

    # Refuzarea mancarii

    if refusing:

        gx = 400 + shake
        gy = 404 + bob

        out.append(
            f'<ellipse cx="{gx:.0f}" cy="{gy - 2:.0f}" '
            f'rx="20" ry="13" fill="{GREEN}"/>'

            f'<path d="M{gx - 16:.0f} {gy:.0f} '
            'q4 -10 8 0 t8 0 t8 0 t8 0" '
            f'fill="none" stroke="{DARK}" stroke-width="5" '
            'stroke-linecap="round"/>'

            f'<ellipse cx="{gx + 6:.0f}" cy="{gy + 12:.0f}" '
            f'rx="7" ry="10" fill="{PINK}" '
            f'stroke="{DARK}" stroke-width="3"/>'
        )

    # Murdarie

    op = max(0, (70 - pet["clean"]) / 70) * 0.85

    if op > 0:

        spots = [
            (355, 425, 9),
            (440, 400, 7),
            (400, 445, 10),
            (372, 455, 7),
            (450, 440, 8),
            (412, 385, 6)
        ]

        for sx, sy, r in spots:

            out.append(
                f'<circle cx="{sx}" cy="{sy + bob:.0f}" '
                f'r="{r}" fill="#8B5E3C" '
                f'fill-opacity="{op:.2f}"/>'
            )

    # Spuma de sapun

    for x, y, r in sc["foam"]:

        out.append(
            f'<circle cx="{x:.0f}" cy="{y + bob:.0f}" '
            f'r="{r}" fill="#fff" '
            'stroke="#9fd8f2" stroke-width="2"/>'
        )

    # Mesaje deasupra broscutei

    if now < sc["popup"][1]:

        k = sc["popup"][1] - now

        out.append(
            f'<text x="400" y="{300 - (1.5 - k) * 40:.0f}" '
            'font-size="34" text-anchor="middle" '
            f'fill="{DARK}" fill-opacity="{min(1, k):.2f}" '
            f'style="{EMOJI}">{sc["popup"][0]}</text>'
        )

    out.append(
        f'<text x="470" y="{330 + bob:.0f}" '
        f'font-size="26" fill="{DARK}" '
        f'fill-opacity="{1 if eating else 0}" '
        f'style="{EMOJI}">nom!</text>'
    )

    # Panoul inferior

    if sleeping:

        out.append(
            '<rect x="60" y="540" width="680" height="54" '
            f'rx="27" fill="{LIGHT}" '
            f'stroke="{DARK}" stroke-width="4"/>'

            f'<text x="400" y="{TRAY_Y}" font-size="18" '
            'text-anchor="middle" dominant-baseline="central" '
            f'fill="{DARK}">'
            f'Shhh... doarme 💤 energie {pet["energy"]:.0f}%'
            '</text>'
        )

    elif sc["mode"] == "feed":

        out.append(
            '<rect x="60" y="540" width="680" height="54" '
            f'rx="27" fill="{LIGHT}" stroke="{DARK}" '
            'stroke-width="4"/>'
        )

        for i, (emo, *_) in enumerate(FOODS):

            if d != ("food", i):

                out.append(
                    f'<text x="{TRAY_X0 + i * TRAY_DX}" '
                    f'y="{TRAY_Y}" font-size="38" '
                    'text-anchor="middle" '
                    'dominant-baseline="central" '
                    f'style="{EMOJI}">{emo}</text>'
                )

    else:

        out.append(
            '<rect x="60" y="540" width="680" height="54" '
            f'rx="27" fill="{LIGHT}" '
            f'stroke="{DARK}" stroke-width="4"/>'
        )

        if d != ("soap", 0):

            out.append(
                f'<text x="{SOAP[0]}" y="{SOAP[1]}" '
                'font-size="44" text-anchor="middle" '
                'dominant-baseline="central" '
                f'style="{EMOJI}">🧼</text>'
            )

        out.append(
            f'<text x="400" y="{TRAY_Y}" font-size="16" '
            'text-anchor="middle" dominant-baseline="central" '
            f'fill="{DARK}">'
            'freacă săpunul pe el, apoi trage dușul deasupra'
            '</text>'
        )

        hx, hy = (mx, my) if showering else SHOWER

        out.append(
            f'<line x1="{SHOWER[0] + 6}" y1="0" '
            f'x2="{hx + 6}" y2="{hy - 30}" '
            f'stroke="{DARK}" stroke-width="8" '
            'stroke-linecap="round"/>'
        )

        out.append(
            f'<text x="{hx}" y="{hy}" font-size="64" '
            'text-anchor="middle" dominant-baseline="central" '
            f'style="{EMOJI}">🚿</text>'
        )

        if showering:

            for i in range(16):

                px = hx - 40 + (i * 5.5) + (i % 3) * 3
                py = hy + 40 + ((t * 520 + i * 47) % 300)

                if py < 535:

                    out.append(
                        f'<line x1="{px:.0f}" y1="{py:.0f}" '
                        f'x2="{px - 2:.0f}" y2="{py + 14:.0f}" '
                        'stroke="#58B9EE" stroke-width="4" '
                        'stroke-linecap="round"/>'
                    )

    # Obiecte trase cu mouse-ul

    if d is not None and d[0] == "food":

        out.append(
            f'<text x="{mx}" y="{my}" font-size="56" '
            'text-anchor="middle" dominant-baseline="central" '
            f'style="{EMOJI}">{FOODS[d[1]][0]}</text>'
        )

    if d is not None and d[0] == "soap":

        out.append(
            f'<text x="{mx}" y="{my}" font-size="60" '
            'text-anchor="middle" dominant-baseline="central" '
            f'style="{EMOJI}">🧼</text>'
        )

    return "".join(out)

def game_tick():

    now = time.time()

    dt = min(now - sc["last"], 0.5)
    sc["last"] = now

    msg = None
    d = sc["drag"]

    if (
        d
        and d[0] == "shower"
        and abs(sc["mx"] - 400) < 160
        and sc["my"] < 470
        and sc["foam"]
    ):

        for _ in range(2):

            if sc["foam"]:

                sc["foam"].pop(
                    random.randrange(len(sc["foam"]))
                )

                clamp("clean", 1.2)
                clamp("happiness", 0.25)

    if sc["sleeping"]:

        clamp("energy", SLEEP_RATE * dt)

        if pet["energy"] >= 99.9:

            sc["sleeping"] = False
            pet["mood"] = "happy"

            clamp("happiness", 15)

            sc["popup"] = (
                "Bună dimineața! ☀️",
                now + 2.2
            )

            save()

            msg = "S-a trezit odihnit și fericit! ☀️"

    if sc["study_end"] and now >= sc["study_end"]:

        sc["study_end"] = 0.0

        clamp("happiness", 10)

        sc["popup"] = (
            "Bravo! 🎉",
            now + 2.2
        )

        save()

        msg = "Sesiunea de study s-a terminat! 🎉"

    return msg


def toggle_sleep():

    if sc["sleeping"]:

        sc["sleeping"] = False

        if pet["energy"] < 60:
            pet["mood"] = "sleepy"

        ui.notify("L-ai trezit 🥱")

        return

    if sc["study_end"]:

        ui.notify(
            "Termină sau oprește mai întâi sesiunea de study 📚"
        )

        return

    if pet["energy"] >= 95:

        sc["refuse_until"] = time.time() + 1.4

        sc["popup"] = (
            "Nu mi-e somn! 😤",
            time.time() + 1.5
        )

        return

    sc.update(
        sleeping=True,
        drag=None
    )


def start_study(minutes):

    if sc["sleeping"]:

        ui.notify("Doarme acum 😴")

        return

    sc.update(
        study_end=time.time() + minutes * 60,
        study_total=minutes * 60,
        drag=None
    )


def stop_study():

    sc["study_end"] = 0.0

    ui.notify("Sesiune oprită")


def fmt(sec):

    sec = max(0, int(sec + 0.99))

    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)

    return (
        f"{h}:{m:02d}:{s:02d}"
        if h
        else f"{m:02d}:{s:02d}"
    )

def widget_running():

    p = procs["widget"]

    return p is not None and p.poll() is None


def open_widget():

    if importlib.util.find_spec("webview") is None:

        ui.notify(
            "Lipsește pywebview. Rulează: "
            f"{sys.executable} -m pip install pywebview",
            type="warning",
            multi_line=True
        )

        return

    if widget_running():

        ui.notify("Widgetul e deja pornit 🐸")

        return

    procs["widget"] = subprocess.Popen([
        sys.executable,
        str(HERE / "widget.py"),
        str(PORT)
    ])

    ui.notify(
        "Widgetul apare în colțul din dreapta-jos al ecranului 🐸"
    )


def close_widget():

    if widget_running():

        procs["widget"].terminate()

    else:

        ui.notify("Widgetul nu a fost pornit din joc")


@app.get("/api/look")
def api_look(
    dx: float = 0.0,
    dy: float = 0.0,
    inside: int = 0
):

    look.update(
        dx=max(-1, min(1, dx)),
        dy=max(-1, min(1, dy)),
        inside=inside,
        t=time.monotonic()
    )

    return {"ok": True}


def widget_svg(size, dx, dy, petting):

    t = time.time()

    sleeping = sc["sleeping"]
    studying = sc["study_end"] > 0

    petting = (
        petting or t < sc["eat_until"]
    ) and not sleeping and not studying

    if studying:

        dx, dy = 0.3, 0.9

    bob = math.sin(
        t * (1.2 if sleeping else 3)
    ) * 5

    flap = math.sin(t * 9) * 9

    f = frog_svg(
        "sleepy" if sleeping else pet["mood"],
        dx,
        dy,
        petting,
        False,
        400
    ).strip()

    # Eliminarea SVG-ului exterior.
    # Pastram doar continutul desenului.

    f = f[
        f.index(">") + 1:
        f.rindex("</svg>")
    ]

    # Animatia corpului

    f = f.replace(
        '<g class="frog">',
        f'<g transform="translate(0 {bob:.1f})">'
    )

    # Animatia aripioarelor

    f = f.replace(
        '<g class="wl">',
        f'<g transform="rotate({flap:.1f} 130 230)">'
    )

    f = f.replace(
        '<g class="wr">',
        f'<g transform="rotate({-flap:.1f} 270 230)">'
    )

    glasses = ""

    if studying and not sleeping:

        glasses = (
            f'<g transform="translate(0 {bob:.1f})" '
            'fill="white" fill-opacity=".3" '
            f'stroke="{DARK}" stroke-width="7">'

            '<circle cx="148" cy="180" r="34"/>'
            '<circle cx="252" cy="180" r="34"/>'

            '<path d="M182 175 Q200 160 218 175" '
            'fill="none"/>'

            '</g>'
        )

    # SVG adaptabil la dimensiunea widgetului.

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="100%" height="100%" '
        'viewBox="-20 65 440 350" '
        'preserveAspectRatio="xMidYMid meet" '
        'style="display:block">'

        f'{f}{glasses}'

        '</svg>'
    )

def on_mouse(e):

    x, y = e.image_x, e.image_y

    sc["mx"], sc["my"] = x, y

    if sc["sleeping"]:

        sc["drag"] = None

        return

    if e.type == "mousedown" and sc["drag"] is None:

        if sc["mode"] == "feed":

            for i in range(len(FOODS)):

                if math.hypot(
                    x - TRAY_X0 - i * TRAY_DX,
                    y - TRAY_Y
                ) < 36:

                    sc["drag"] = ("food", i)

        elif math.hypot(
            x - SOAP[0],
            y - SOAP[1]
        ) < 40:

            sc["drag"] = ("soap", 0)

        elif math.hypot(
            x - SHOWER[0],
            y - SHOWER[1]
        ) < 48:

            sc["drag"] = ("shower", 0)

    elif e.type == "mousemove":

        d = sc["drag"]

        if (
            d
            and d[0] == "soap"
            and over_frog(x, y)
            and len(sc["foam"]) < 80
        ):

            for _ in range(2):

                sc["foam"].append((
                    x + random.uniform(-18, 18),
                    y + random.uniform(-18, 18),
                    random.randint(9, 22)
                ))

            clamp("happiness", 0.1)

    elif e.type in ("mouseup", "mouseleave"):

        d = sc["drag"]

        sc["drag"] = None

        if (
            d
            and d[0] == "food"
            and e.type == "mouseup"
            and over_frog(x, y)
        ):

            _, fd, hp = FOODS[d[1]]

            if pet["food"] >= 95:

                sc["refuse_until"] = time.time() + 1.4

                sc["popup"] = (
                    "Bleah! Sunt plină! 🤢",
                    time.time() + 1.5
                )

                return

            clamp("food", fd)
            clamp("happiness", hp)
            clamp("energy", 2)

            sc["eat_until"] = time.time() + 1.3

            sc["popup"] = (
                f"+{fd} 🍽️",
                time.time() + 1.5
            )

            save()

        elif d:

            save()


def style():

    ui.colors(
        primary=PINK,
        secondary=GREEN,
        accent=DARK
    )

    ui.query("body").style(
        f"background:linear-gradient(#FFE4F8,{BLUE});"
        f"color:{DARK};"
        "font-family:'Comic Sans MS',sans-serif"
    )


def stat_bar(label, key):

    with ui.row().classes(
        "items-center no-wrap"
    ).style(
        "min-width:170px;flex:1"
    ):

        ui.label(label).classes("text-lg")

        ui.linear_progress(
            show_value=False,
            size="14px",
            color="pink"
        ).bind_value_from(
            pet,
            key,
            backward=lambda v: v / 100
        ).classes("flex-grow")


@ui.page("/")
def main_page():

    style()

    with ui.dialog() as dlg, ui.card().style(
        f"background:{LIGHT}"
    ):

        ui.label(
            "📚 Cât vrei să înveți?"
        ).classes("text-lg")

        with ui.grid(columns=2):

            for label, m in STUDY_OPTIONS:

                ui.button(
                    label,
                    on_click=lambda m=m: (
                        start_study(m),
                        dlg.close()
                    )
                ).props("unelevated color=pink")

        ui.button(
            "Anulează",
            on_click=dlg.close
        ).props("flat")

    with ui.column().classes(
        "items-center w-full max-w-5xl mx-auto p-3 gap-2"
    ):

        with ui.row().classes(
            "w-full items-center no-wrap"
        ):

            mood_sel = ui.select(
                MOODS,
                value=pet["mood"],
                label="Mood",
                on_change=lambda e: (
                    set_mood(e.value)
                    if e.value != pet["mood"]
                    else None
                )
            ).props(
                "filled dense bg-color=pink-1"
            ).classes("w-44")

            ui.toggle(
                {
                    "feed": "🍎 Mâncare",
                    "bath": "🛁 Baie"
                },
                value=sc["mode"],
                on_change=lambda e: sc.update(
                    mode=e.value,
                    drag=None
                )
            ).props("color=pink toggle-color=pink")

            sleep_btn = ui.button(
                "😴 Somn",
                on_click=toggle_sleep
            ).props("unelevated color=pink")

            ui.space()

            ui.button(
                "🪟 Widget",
                on_click=open_widget
            ).props("unelevated color=pink")

            ui.button(
                "💬 CHAT",
                on_click=lambda: ui.navigate.to("/chat")
            ).props("unelevated color=pink")

        with ui.card().classes("w-full").style(
            f"background:{LIGHT}"
        ):

            with ui.row().classes(
                "w-full no-wrap gap-4"
            ):

                stat_bar("💗", "happiness")
                stat_bar("⚡", "energy")
                stat_bar("🍽️", "food")
                stat_bar("🫧", "clean")

        with ui.row().classes(
            "w-full items-start gap-3"
        ):

            img = ui.interactive_image(
                ROOM_URI,
                content="",
                on_mouse=on_mouse,
                cross=False,
                events=[
                    "mousedown",
                    "mousemove",
                    "mouseup",
                    "mouseleave"
                ]
            ).style(
                f"flex:1 1 520px;min-width:0;"
                f"border:5px solid {DARK};"
                "border-radius:18px;"
                "user-select:none;"
                "-webkit-user-drag:none;"
                "cursor:grab"
            )

            img.on(
                "dragstart.prevent",
                lambda: None
            )

            with ui.card().classes(
                "items-center gap-2"
            ).style(
                f"width:190px;"
                f"background:{LIGHT};"
                f"border:4px solid {DARK}"
            ):

                ui.label("🕒 Ceas").classes("text-lg")

                clock = ui.label(
                    "--:--"
                ).classes("text-3xl font-bold")

                sub = ui.label(
                    "ora curentă"
                ).classes("text-xs opacity-70")

                prog = ui.linear_progress(
                    value=0,
                    show_value=False,
                    color="green",
                    size="12px"
                ).classes("w-full")

                study_btn = ui.button(
                    "📚 Study",
                    on_click=dlg.open
                ).props("unelevated color=pink")

                stop_btn = ui.button(
                    "⏹ Oprește",
                    on_click=stop_study
                ).props("unelevated color=accent")

        def frame():

            msg = game_tick()

            if msg:

                ui.notify(msg)

            img.content = render()

            if mood_sel.value != pet["mood"]:

                mood_sel.set_value(pet["mood"])

            sleep_btn.text = (
                "☀️ Trezește-l"
                if sc["sleeping"]
                else "😴 Somn"
            )

            studying = sc["study_end"] > 0

            if studying:

                left = sc["study_end"] - time.time()

                clock.text = fmt(left)
                sub.text = "timp rămas la study"

                prog.value = (
                    1 - left / sc["study_total"]
                )

            else:

                clock.text = time.strftime("%H:%M")
                sub.text = "ora curentă"
                prog.value = 0

            prog.set_visibility(studying)
            stop_btn.set_visibility(studying)
            study_btn.set_visibility(not studying)

        ui.timer(0.08, frame)

        ui.label(
            "Trage mâncarea la broscuță · "
            "în Baie: freacă săpunul, apoi trage dușul · "
            "mângâie-o cu cursorul"
        ).classes("text-xs opacity-70")

@ui.page("/widget")
def widget_page():

    ui.add_head_html("""
    <style>

        html,
        body,
        #q-app,
        .q-layout,
        .q-page-container,
        .q-page,
        .nicegui-content {

            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;

        }

    </style>
    """)

    html = ui.html(
        "",
        sanitize=False
    ).style(
        "position:fixed;"
        "left:0;"
        "right:0;"
        "top:28px;"
        "bottom:0;"
        "width:100%;"
        "height:calc(100% - 28px);"
        "pointer-events:none;"
        "overflow:hidden"
    )

    with ui.row().classes(
        "no-wrap"
    ).style(
        "position:fixed;"
        "top:0;"
        "right:4px;"
        "opacity:.7;"
        "gap:0;"
        "z-index:10"
    ):

        ui.button(
            "🎮",
            on_click=lambda: webbrowser.open(
                f"http://localhost:{PORT}/"
            )
        ).props(
            "flat dense round size=sm"
        ).tooltip("Deschide jocul")

        ui.button(
            "✕",
            on_click=close_widget
        ).props(
            "flat dense round size=sm"
        ).tooltip("Închide widgetul")

    def draw():

        fresh = time.monotonic() - look["t"] < 1

        if fresh:

            dx = look["dx"]
            dy = look["dy"]

        else:

            dx = dy = 0.0

        inside = bool(
            fresh and look["inside"]
        )

        if (
            inside
            and not sc["sleeping"]
            and not sc["study_end"]
        ):

            clamp("happiness", 0.03)

        html.content = widget_svg(
            400,
            dx,
            dy,
            inside
        )

    draw()

    ui.timer(0.05, draw)


@ui.page("/chat")
def chat_page():

    style()

    with ui.column().classes(
        "w-full max-w-2xl mx-auto p-4 h-screen no-wrap"
    ):

        with ui.row().classes("items-center"):

            ui.button(
                icon="arrow_back",
                on_click=lambda: ui.navigate.to("/")
            ).props("flat round")

            ui.label().bind_text_from(
                pet,
                "mood",
                backward=lambda m: (
                    "Chat cu Flappy · " + MOODS[m]
                )
            ).classes("text-lg")

        with ui.scroll_area().classes(
            "flex-grow w-full"
        ) as area:

            box = ui.column().classes("w-full")

        with box:

            for role, text in history:

                ui.chat_message(
                    text,
                    sent=role == "user"
                )

        with ui.row().classes(
            "w-full no-wrap items-center"
        ):

            ui.select(
                MOODS,
                value=pet["mood"],
                on_change=lambda e: set_mood(e.value)
            ).props("filled dense")

            inp = ui.input(
                placeholder="Scrie ceva..."
            ).props(
                "rounded outlined bg-color=pink-1"
            ).classes("flex-grow")

            async def send():

                text = inp.value.strip()

                if not text:

                    return

                inp.value = ""

                history.append(("user", text))

                with box:

                    ui.chat_message(
                        text,
                        sent=True
                    )

                    wait = ui.chat_message(
                        "...",
                        sent=False
                    )

                area.scroll_to(percent=1)

                ans = await reply(
                    history,
                    pet["mood"],
                    pet
                )

                history.append(
                    ("assistant", ans)
                )

                wait.delete()

                with box:

                    ui.chat_message(
                        ans,
                        sent=False
                    )

                clamp("happiness", 2)

                save()

                area.scroll_to(percent=1)

            inp.on("keydown.enter", send)

def tick():

    clamp("food", -1)
    clamp("clean", -1)

    if not sc["sleeping"]:

        clamp("energy", -1)

    if pet["food"] < 25 or pet["clean"] < 20:

        clamp("happiness", -2)

    save()


app.timer(30, tick)

ui.run(
    title="Flappy Frog",
    port=PORT,
    reload=False,
    favicon="🐸"
)