"""Flappy Frog - Desktop Widget."""

import sys
import time
import ctypes
import urllib.request

from ctypes import wintypes

import webview


PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
BASE = f"http://127.0.0.1:{PORT}"

W = 260
H = 250

TITLE = "Flappy Frog Desktop"


def get_hwnd():

    if sys.platform != "win32":
        return None

    user32 = ctypes.windll.user32

    user32.FindWindowW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.LPCWSTR
    ]

    user32.FindWindowW.restype = wintypes.HWND

    return user32.FindWindowW(None, TITLE)


def show_widget(window):

    window.show()

    if sys.platform != "win32":
        return

    user32 = ctypes.windll.user32

    hwnd = get_hwnd()

    if not hwnd:
        return

    work_area = wintypes.RECT()

    user32.SystemParametersInfoW(
        0x0030,
        0,
        ctypes.byref(work_area),
        0
    )

    rect = wintypes.RECT()

    user32.GetWindowRect(
        hwnd,
        ctypes.byref(rect)
    )

    width = rect.right - rect.left
    height = rect.bottom - rect.top

    x = work_area.right - width - 20
    y = work_area.bottom - height - 20

    x = max(work_area.left, x)
    y = max(work_area.top, y)

    # Restaureaza fereastra daca este minimizata.
    user32.ShowWindow(hwnd, 9)

    # Pozitioneaza fereastra deasupra celorlalte.
    user32.SetWindowPos(
        hwnd,
        ctypes.c_void_p(-1),
        x,
        y,
        0,
        0,
        0x0001 | 0x0040
    )


def geometry():

    if sys.platform != "win32":
        return None

    user32 = ctypes.windll.user32

    hwnd = get_hwnd()

    if not hwnd:
        return None

    rect = wintypes.RECT()
    origin = wintypes.POINT(0, 0)
    cursor = wintypes.POINT()

    if not user32.GetClientRect(
        hwnd,
        ctypes.byref(rect)
    ):
        return None

    if not user32.ClientToScreen(
        hwnd,
        ctypes.byref(origin)
    ):
        return None

    if not user32.GetCursorPos(
        ctypes.byref(cursor)
    ):
        return None

    try:
        dpi = user32.GetDpiForWindow(hwnd) or 96
    except Exception:
        dpi = 96

    return (
        cursor.x - origin.x,
        cursor.y - origin.y,
        rect.right - rect.left,
        rect.bottom - rect.top,
        dpi / 96
    )


def follow(window):

    time.sleep(0.5)

    show_widget(window)

    fails = 0

    while True:

        time.sleep(0.05)

        try:

            g = geometry()

            if g is None:
                continue

            x, y, w, h, dpi = g

            top = 28 * dpi

            scale = min(
                w / 440,
                (h - top) / 350
            )

            if scale <= 0:
                continue

            # Coordonatele cursorului in SVG.

            sx = (
                x - (w - 440 * scale) / 2
            ) / scale - 20

            sy = (
                y - top
                - (h - top - 350 * scale) / 2
            ) / scale + 65

            # Miscarea ochilor.

            dx = max(
                -1,
                min(1, (sx - 200) / 220)
            )

            dy = max(
                -1,
                min(1, (sy - 180) / 180)
            )

            # Detectarea mangaierii.

            inside = int(
                ((sx - 200) / 115) ** 2
                + ((sy - 240) / 105) ** 2
                <= 1
            )

            url = (
                f"{BASE}/api/look"
                f"?dx={dx:.4f}"
                f"&dy={dy:.4f}"
                f"&inside={inside}"
            )

            with urllib.request.urlopen(
                url,
                timeout=1
            ) as response:

                response.read()

            fails = 0

        except Exception as e:

            fails += 1

            if fails == 1:
                print("Widget error:", e)

            if fails >= 20:

                try:
                    window.destroy()
                except Exception:
                    pass

                return


if __name__ == "__main__":

    window = webview.create_window(
        title=TITLE,
        url=f"{BASE}/widget",

        width=W,
        height=H,

        x=100,
        y=100,

        frameless=True,
        easy_drag=True,

        on_top=True,
        transparent=False,
        hidden=False,
        minimized=False,

        resizable=False,

        background_color="#FFE4F8"
    )

    webview.start(
        follow,
        window,
        gui="edgechromium",
        debug=False
    )