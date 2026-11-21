
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ctypes
import json
import os
import sys
import random
import threading
import time
import urllib.request
import urllib.parse
import webbrowser
import subprocess
import tempfile
from pathlib import Path

# =========================================================
# LCB TOOL V3 - AUTO UPDATE CENTER
# =========================================================

APP_NAME = "LCB TOOL"
APP_VERSION = "3.0"

APP_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "LCB_TOOL"
APP_DIR.mkdir(parents=True, exist_ok=True)

PRESET_FILE = APP_DIR / "presets.json"
SETTINGS_FILE = APP_DIR / "settings.json"
LOGIN_FILE = APP_DIR / "login.json"

LOGIN_USERNAME = "geecolor"
LOGIN_PASSWORD = "200913"

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE = "LCB_TOOL"

DEFAULTS = {
    "Brightness": 0,
    "Contrast": 100,
    "Gamma": 100,
    "Red": 100,
    "Green": 100,
    "Blue": 100,
    "Saturation": 100,
    "Vibrance": 0,
    "Temperature": 0
}

FIREBASE_API_KEY = "AIzaSyA_lT8elJ8qJk7Iw_d461ICUSeEpIn0bNk"

FIREBASE_DB = (
    "https://lcb-tool-default-rtdb."
    "asia-southeast1.firebasedatabase.app"
)

GITHUB_RELEASE_API = (
    "https://api.github.com/repos/"
    "primeleaderofficial/LCB-TOOL/releases/latest"
)

GITHUB_RELEASE_PAGE = (
    "https://github.com/primeleaderofficial/"
    "LCB-TOOL/releases"
)

HEARTBEAT_INTERVAL = 10
ONLINE_TIMEOUT = 35
NETWORK_TIMEOUT = 8

BG = "#0b0b0d"
PANEL = "#17171a"
PANEL2 = "#202024"
WHITE = "#f4f4f5"
MUTED = "#a5a5ad"
RED = "#d92d35"
RED_HOVER = "#f0444d"
GREEN = "#20b15a"
GREEN_HOVER = "#2cc96b"


# =========================================================
# NETWORK
# =========================================================

def http_json(url, method="GET", data=None, headers=None):

    body = None

    request_headers = {
        "User-Agent": "LCB-TOOL"
    }

    if headers:
        request_headers.update(headers)

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=body,
        headers=request_headers,
        method=method
    )

    with urllib.request.urlopen(
        req,
        timeout=NETWORK_TIMEOUT
    ) as response:

        content = response.read().decode("utf-8")

        if not content:
            return None

        return json.loads(content)


def version_tuple(version):

    version = str(version).lower().strip()

    if version.startswith("v"):
        version = version[1:]

    parts = []

    for item in version.split("."):

        digits = ""

        for char in item:

            if char.isdigit():
                digits += char
            else:
                break

        if not digits:
            return None

        parts.append(int(digits))

    return tuple(parts)


# =========================================================
# SNOW BACKGROUND
# =========================================================

class SnowBackground:

    def __init__(self, root):

        self.root = root

        self.canvas = tk.Canvas(
            root,
            bg=BG,
            highlightthickness=0,
            bd=0
        )

        self.canvas.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1
        )

        self.flakes = []

        self.root.tk.call("lower", self.canvas._w)

        self.root.bind(
            "<Configure>",
            self.resize,
            add="+"
        )

        self.seed()
        self.animate()

    def seed(self):

        w = max(self.root.winfo_width(), 430)
        h = max(self.root.winfo_height(), 390)

        for _ in range(42):

            x = random.randrange(w)
            y = random.randrange(h)
            r = random.choice((1, 1, 2, 2, 3))

            item = self.canvas.create_oval(
                x, y,
                x + r * 2,
                y + r * 2,
                fill=random.choice(
                    ("#d8d8dc", "#eeeeef", "#9c9ca4")
                ),
                outline=""
            )

            self.flakes.append((
                item,
                random.uniform(0.7, 2.3),
                random.uniform(-0.5, 0.5)
            ))

    def resize(self, event):

        if event.widget is self.root:

            self.canvas.place(
                x=0,
                y=0,
                relwidth=1,
                relheight=1
            )

    def animate(self):

        try:

            if not self.root.winfo_exists():
                return

            h = max(self.root.winfo_height(), 390)
            w = max(self.root.winfo_width(), 430)

            for item, speed, drift in self.flakes:

                self.canvas.move(item, drift, speed)

                coords = self.canvas.coords(item)

                if len(coords) < 4:
                    continue

                x1, y1, x2, y2 = coords

                if y1 > h:

                    new_x = random.randrange(max(1, w - 8))
                    size = max(2, x2 - x1)

                    self.canvas.coords(
                        item,
                        new_x,
                        -5,
                        new_x + size,
                        -3
                    )

            self.root.after(55, self.animate)

        except tk.TclError:
            pass


# =========================================================
# ROUND BUTTON
# =========================================================

class RoundButton(tk.Canvas):

    def __init__(
        self,
        parent,
        text,
        command,
        bg=RED,
        hover=RED_HOVER,
        fg=WHITE,
        height=34,
        width=125,
        **kwargs
    ):

        super().__init__(
            parent,
            height=height,
            width=width,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )

        self.text = text
        self.command = command
        self.normal = bg
        self.hover = hover
        self.fg = fg
        self.height_px = height

        self.bind(
            "<Enter>",
            lambda _e: self.draw(self.hover)
        )

        self.bind(
            "<Leave>",
            lambda _e: self.draw(self.normal)
        )

        self.bind(
            "<Button-1>",
            lambda _e: self.command()
        )

        self.draw(bg)

    def draw(self, color):

        self.delete("all")

        w = max(
            self.winfo_width(),
            int(self.cget("width"))
        )

        h = self.height_px
        r = 9

        self.create_arc(
            0, 0, r * 2, r * 2,
            start=90,
            extent=90,
            fill=color,
            outline=color
        )

        self.create_arc(
            w-r*2, 0, w, h,
            start=0,
            extent=90,
            fill=color,
            outline=color
        )

        self.create_arc(
            w-r*2, h-r*2, w, h,
            start=270,
            extent=90,
            fill=color,
            outline=color
        )

        self.create_arc(
            0, h-r*2, r*2, h,
            start=180,
            extent=90,
            fill=color,
            outline=color
        )

        self.create_rectangle(
            r, 0, w-r, h,
            fill=color,
            outline=color
        )

        self.create_rectangle(
            0, r, w, h-r,
            fill=color,
            outline=color
        )

        self.create_text(
            w / 2,
            h / 2,
            text=self.text,
            fill=self.fg,
            font=("Segoe UI", 9, "bold")
        )


# =========================================================
# LOGIN PAGE
# =========================================================

class LoginPage:

    def __init__(self, root):

        self.root = root
        self.success = False

        root.title("LCB TOOL - Login")
        root.geometry("430x390")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.snow = SnowBackground(root)

        root.protocol(
            "WM_DELETE_WINDOW",
            root.destroy
        )

        remembered = self.load_saved_credentials()

        header = tk.Frame(
            root,
            bg=BG,
            height=105
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="LCB TOOL",
            font=("Segoe UI", 26, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(pady=(17, 0))

        tk.Label(
            header,
            text="WELCOME BACK",
            font=("Segoe UI", 9, "bold"),
            fg=RED,
            bg=BG
        ).pack()

        body = tk.Frame(
            root,
            bg=BG,
            padx=34,
            pady=22
        )

        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="Login to continue",
            font=("Segoe UI", 13, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(pady=(0, 13))

        tk.Label(
            body,
            text="Username",
            font=("Segoe UI", 9, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(anchor="w")

        self.username = tk.Entry(
            body,
            font=("Segoe UI", 10),
            relief="flat",
            bg=PANEL2,
            fg=WHITE,
            insertbackground=WHITE,
            bd=0
        )

        self.username.pack(
            fill="x",
            ipady=6,
            pady=(4, 10)
        )

        tk.Label(
            body,
            text="Password",
            font=("Segoe UI", 9, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(anchor="w")

        self.password = tk.Entry(
            body,
            show="*",
            font=("Segoe UI", 10),
            relief="flat",
            bg=PANEL2,
            fg=WHITE,
            insertbackground=WHITE,
            bd=0
        )

        self.password.pack(
            fill="x",
            ipady=6,
            pady=(4, 8)
        )

        self.remember = tk.BooleanVar(value=True)

        tk.Checkbutton(
            body,
            text="Remember username & password",
            variable=self.remember,
            bg=BG,
            fg=WHITE,
            activebackground=BG,
            selectcolor=PANEL2,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 12))

        RoundButton(
            body,
            text="LOGIN",
            command=self.check_login,
            bg=RED,
            hover=RED_HOVER,
            height=33,
            width=300
        ).pack(fill="x", pady=(2, 0))

        self.password.bind(
            "<Return>",
            lambda _e: self.check_login()
        )

        self.username.bind(
            "<Return>",
            lambda _e: self.password.focus_set()
        )

        if remembered:

            self.username.insert(
                0,
                remembered.get("username", "")
            )

            self.password.insert(
                0,
                remembered.get("password", "")
            )

            self.remember.set(True)
            self.password.focus_set()

        else:

            self.username.focus_set()

    def load_saved_credentials(self):

        try:

            data = json.loads(
                LOGIN_FILE.read_text(encoding="utf-8")
            )

            if data.get("remembered"):

                return {
                    "username": data.get("username", ""),
                    "password": data.get("password", "")
                }

        except Exception:
            pass

        return None

    def check_login(self):

        if (
            self.username.get().strip() == LOGIN_USERNAME
            and self.password.get() == LOGIN_PASSWORD
        ):

            self.success = True

            if self.remember.get():

                try:

                    LOGIN_FILE.write_text(
                        json.dumps({
                            "remembered": True,
                            "username": self.username.get().strip(),
                            "password": self.password.get()
                        }),
                        encoding="utf-8"
                    )

                except Exception as e:

                    messagebox.showwarning(
                        "LCB TOOL",
                        f"Could not save remembered credentials:\n{e}",
                        parent=self.root
                    )

            else:

                try:
                    LOGIN_FILE.unlink(missing_ok=True)
                except Exception:
                    pass

            self.root.destroy()

        else:

            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password.",
                parent=self.root
            )

            self.password.delete(0, "end")
            self.password.focus_set()


# =========================================================
# MAIN COLOR TOOL
# =========================================================

class ColorTool:

    def __init__(self, root, startup_apply=False):

        self.root = root
        self.startup_apply = startup_apply

        self.online_running = False
        self.online_label = None

        self.online_stop = threading.Event()

        self.firebase_uid = None
        self.firebase_token = None

        root.title(APP_NAME)
        root.geometry("790x740")
        root.minsize(730, 680)
        root.configure(bg=BG)

        self.snow = SnowBackground(root)

        self.gdi = ctypes.WinDLL("gdi32")
        self.user = ctypes.WinDLL("user32")

        self.ramp_type = (ctypes.c_ushort * 256) * 3

        self.original = self.ramp_type()
        self.current = self.ramp_type()

        self.dc = self.user.GetDC(None)

        if not self.dc:
            raise RuntimeError(
                "Could not access Windows display device."
            )

        self.gdi.GetDeviceGammaRamp(
            self.dc,
            ctypes.byref(self.original)
        )

        self.presets = {}
        self.load_presets()

        self.vars = {}

        self.load_settings()

        if startup_apply:

            self.apply_startup_settings()

            try:
                self.user.ReleaseDC(None, self.dc)
            except Exception:
                pass

            root.destroy()
            return

        self.build_ui()

        self.apply_values(save=False)

        root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self.start_online_counter()

    # -----------------------------------------------------
    # BUILD UI
    # -----------------------------------------------------

    def build_ui(self):

        header = tk.Frame(
            self.root,
            bg=BG,
            height=88
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="LCB TOOL",
            font=("Segoe UI", 25, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(pady=(12, 0))

        tk.Label(
            header,
            text="LIVE DISPLAY COLOR CONTROL",
            font=("Segoe UI", 9, "bold"),
            fg=RED,
            bg=BG
        ).pack()

        self.online_label = tk.Label(
            header,
            text="ONLINE: CONNECTING...",
            font=("Segoe UI", 8, "bold"),
            fg=GREEN,
            bg=PANEL,
            padx=10,
            pady=7
        )

        self.online_label.place(
            relx=1.0,
            x=-15,
            y=12,
            anchor="ne"
        )

        main = tk.Frame(
            self.root,
            bg=BG,
            padx=20,
            pady=10
        )

        main.pack(fill="both", expand=True)

        panel = tk.Frame(
            main,
            bg=PANEL,
            highlightbackground="#36363b",
            highlightthickness=1,
            padx=16,
            pady=10
        )

        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text="Adjust colours in real time",
            font=("Segoe UI", 14, "bold"),
            bg=PANEL,
            fg=WHITE
        ).pack(anchor="w", pady=(0, 8))

        definitions = [
            ("Brightness", -100, 100),
            ("Contrast", 50, 150),
            ("Gamma", 50, 200),
            ("Red", 50, 150),
            ("Green", 50, 150),
            ("Blue", 50, 150),
            ("Saturation", 0, 200),
            ("Vibrance", -100, 100),
            ("Temperature", -100, 100)
        ]

        for name, lo, hi in definitions:

            row = tk.Frame(
                panel,
                bg=PANEL
            )

            row.pack(
                fill="x",
                pady=4
            )

            tk.Label(
                row,
                text=name,
                width=12,
                anchor="w",
                font=("Segoe UI", 10, "bold"),
                bg=PANEL,
                fg=WHITE
            ).pack(side="left")

            var = tk.IntVar(
                value=self.settings.get(
                    name,
                    DEFAULTS[name]
                )
            )

            self.vars[name] = var

            scale = tk.Scale(
                row,
                from_=lo,
                to=hi,
                orient="horizontal",
                variable=var,
                showvalue=False,
                length=440,
                bg=PANEL,
                fg=RED,
                troughcolor="#45454b",
                highlightthickness=0,
                activebackground=RED_HOVER,
                command=lambda _v: self.apply_values(save=False)
            )

            scale.pack(
                side="left",
                fill="x",
                expand=True
            )

            tk.Label(
                row,
                textvariable=var,
                width=5,
                bg=PANEL,
                fg=WHITE,
                font=("Segoe UI", 9)
            ).pack(side="right")

        preset_row = tk.Frame(
            main,
            bg=BG
        )

        preset_row.pack(
            fill="x",
            pady=(10, 5)
        )

        tk.Label(
            preset_row,
            text="Preset",
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.preset_var = tk.StringVar()

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "LCB.TCombobox",
            fieldbackground=PANEL2,
            background=PANEL2,
            foreground=WHITE,
            arrowcolor=WHITE
        )

        style.map(
            "LCB.TCombobox",
            fieldbackground=[("readonly", PANEL2)],
            foreground=[("readonly", WHITE)]
        )

        self.combo = ttk.Combobox(
            preset_row,
            textvariable=self.preset_var,
            state="readonly",
            width=20,
            style="LCB.TCombobox"
        )

        self.combo.pack(side="left")

        self.refresh_combo()

        for label, func in [
            ("SAVE PRESET", self.save_preset),
            ("LOAD", self.load_selected),
            ("RESET DEFAULT", self.reset)
        ]:

            RoundButton(
                preset_row,
                text=label,
                command=func,
                bg=RED,
                hover=RED_HOVER,
                height=30,
                width=112
            ).pack(
                side="left",
                padx=4
            )

        action_row = tk.Frame(
            main,
            bg=BG
        )

        action_row.pack(
            fill="x",
            pady=(8, 0)
        )

        RoundButton(
            action_row,
            text="APPLY & SAVE",
            command=self.apply_and_save,
            bg=GREEN,
            hover=GREEN_HOVER,
            height=34,
            width=145
        ).pack(side="left")

        RoundButton(
            action_row,
            text="UPDATE CENTER",
            command=self.open_update_center,
            bg=RED,
            hover=RED_HOVER,
            height=34,
            width=145
        ).pack(
            side="left",
            padx=8
        )

        self.startup_var = tk.BooleanVar(
            value=self.startup_enabled()
        )

        tk.Checkbutton(
            action_row,
            text="Apply saved colours when Windows starts",
            variable=self.startup_var,
            command=self.toggle_startup,
            bg=BG,
            fg=WHITE,
            activebackground=BG,
            selectcolor=PANEL2,
            font=("Segoe UI", 9, "bold")
        ).pack(
            side="left",
            padx=8
        )

        tk.Label(
            main,
            text=(
                "Changes remain after closing LCB TOOL. "
                "Apply at Windows startup is optional."
            ),
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            pady=(8, 0)
        )

    # -----------------------------------------------------
    # COLOR ENGINE
    # -----------------------------------------------------

    def get_values(self):

        if self.vars:

            return {
                key: var.get()
                for key, var in self.vars.items()
            }

        return self.settings.copy()

    def apply_startup_settings(self):

        values = self.settings

        brightness = values["Brightness"]
        contrast = values["Contrast"] / 100.0
        gamma = values["Gamma"] / 100.0

        multipliers = {
            c: values[c] / 100.0
            for c in ("Red", "Green", "Blue")
        }

        saturation = values["Saturation"] / 100.0
        vibrance = values["Vibrance"] / 100.0
        temperature = values["Temperature"] / 100.0

        temp_offsets = {
            "Red": temperature * 0.12,
            "Green": -temperature * 0.015,
            "Blue": -temperature * 0.12
        }

        for channel, cname in enumerate(
            ("Red", "Green", "Blue")
        ):

            for i in range(256):

                x = i / 255.0

                x = (
                    (x - 0.5) * contrast
                    + 0.5
                    + brightness / 255.0
                )

                x = max(0.0, min(1.0, x))

                x = pow(
                    x,
                    1.0 / max(0.05, gamma)
                )

                x = 0.5 + (x - 0.5) * saturation

                midtone_weight = (
                    1.0 - abs(2.0 * x - 1.0)
                )

                x = 0.5 + (
                    (x - 0.5)
                    * (1.0 + vibrance * 0.30 * midtone_weight)
                )

                x = (
                    x * multipliers[cname]
                    + temp_offsets[cname]
                )

                x = max(0.0, min(1.0, x))

                self.current[channel][i] = int(x * 65535)

        self.gdi.SetDeviceGammaRamp(
            self.dc,
            ctypes.byref(self.current)
        )

    def apply_values(self, save=False):

        if not self.vars:
            return

        brightness = self.vars["Brightness"].get()
        contrast = self.vars["Contrast"].get() / 100.0
        gamma = self.vars["Gamma"].get() / 100.0

        multipliers = {
            c: self.vars[c].get() / 100.0
            for c in ("Red", "Green", "Blue")
        }

        saturation = self.vars["Saturation"].get() / 100.0
        vibrance = self.vars["Vibrance"].get() / 100.0
        temperature = self.vars["Temperature"].get() / 100.0

        temp_offsets = {
            "Red": temperature * 0.12,
            "Green": -temperature * 0.015,
            "Blue": -temperature * 0.12
        }

        for channel, cname in enumerate(
            ("Red", "Green", "Blue")
        ):

            for i in range(256):

                x = i / 255.0

                x = (
                    (x - 0.5) * contrast
                    + 0.5
                    + brightness / 255.0
                )

                x = max(0.0, min(1.0, x))

                x = pow(
                    x,
                    1.0 / max(0.05, gamma)
                )

                x = 0.5 + (x - 0.5) * saturation

                midtone_weight = (
                    1.0 - abs(2.0 * x - 1.0)
                )

                x = 0.5 + (
                    (x - 0.5)
                    * (1.0 + vibrance * 0.30 * midtone_weight)
                )

                x = (
                    x * multipliers[cname]
                    + temp_offsets[cname]
                )

                x = max(0.0, min(1.0, x))

                self.current[channel][i] = int(x * 65535)

        try:

            result = self.gdi.SetDeviceGammaRamp(
                self.dc,
                ctypes.byref(self.current)
            )

            if not result and save:

                messagebox.showwarning(
                    APP_NAME,
                    "Windows could not apply the display colour settings."
                )

        except Exception as e:

            if save:

                messagebox.showerror(
                    APP_NAME,
                    f"Could not apply display ramp:\n{e}"
                )

        if save:
            self.save_settings()

    def apply_and_save(self):

        self.apply_values(save=True)

        messagebox.showinfo(
            APP_NAME,
            "Display colours applied and saved."
        )

    # -----------------------------------------------------
    # SETTINGS
    # -----------------------------------------------------

    def load_settings(self):

        try:

            self.settings = json.loads(
                SETTINGS_FILE.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            self.settings = DEFAULTS.copy()

        for key, default in DEFAULTS.items():
            self.settings.setdefault(key, default)

    def save_settings(self):

        data = self.get_values()

        try:

            SETTINGS_FILE.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8"
            )

            self.settings = data.copy()

        except Exception as e:

            messagebox.showerror(
                APP_NAME,
                f"Settings save error:\n{e}"
            )

    # -----------------------------------------------------
    # PRESETS
    # -----------------------------------------------------

    def load_presets(self):

        try:

            self.presets = json.loads(
                PRESET_FILE.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            self.presets = {}

    def write_presets(self):

        try:

            PRESET_FILE.write_text(
                json.dumps(
                    self.presets,
                    indent=2
                ),
                encoding="utf-8"
            )

        except Exception as e:

            messagebox.showerror(
                "Preset save error",
                str(e)
            )

    def refresh_combo(self):

        if hasattr(self, "combo"):

            self.combo["values"] = list(
                self.presets.keys()
            )

    def save_preset(self):

        name = simpledialog.askstring(
            "Save Preset",
            "Preset name:",
            parent=self.root
        )

        if not name:
            return

        name = name.strip()

        if not name:
            return

        self.presets[name] = self.get_values()

        self.write_presets()
        self.refresh_combo()

        self.preset_var.set(name)

        messagebox.showinfo(
            APP_NAME,
            "Preset saved!"
        )

    def set_values(self, data):

        for key, value in data.items():

            if key in self.vars:

                try:
                    self.vars[key].set(value)
                except Exception:
                    pass

        self.apply_values(save=False)

    def load_selected(self):

        name = self.preset_var.get()

        if name and name in self.presets:

            self.set_values(
                self.presets[name]
            )

            self.save_settings()

        else:

            messagebox.showwarning(
                APP_NAME,
                "Select a saved preset first."
            )

    def reset(self):

        for key, value in DEFAULTS.items():
            self.vars[key].set(value)

        self.apply_values(save=False)
        self.save_settings()

    # -----------------------------------------------------
    # WINDOWS STARTUP
    # -----------------------------------------------------

    def startup_enabled(self):

        try:

            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                RUN_KEY
            ) as key:

                winreg.QueryValueEx(
                    key,
                    RUN_VALUE
                )

            return True

        except Exception:
            return False

    def startup_command(self):

        if getattr(sys, "frozen", False):

            return (
                f'"{sys.executable}" '
                f'--startup-apply'
            )

        py = sys.executable

        if py.lower().endswith("python.exe"):
            py = py[:-10] + "pythonw.exe"

        return (
            f'"{py}" '
            f'"{Path(__file__).resolve()}" '
            f'--startup-apply'
        )

    def toggle_startup(self):

        try:

            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                RUN_KEY,
                0,
                winreg.KEY_SET_VALUE
            ) as key:

                if self.startup_var.get():

                    self.save_settings()

                    winreg.SetValueEx(
                        key,
                        RUN_VALUE,
                        0,
                        winreg.REG_SZ,
                        self.startup_command()
                    )

                else:

                    try:

                        winreg.DeleteValue(
                            key,
                            RUN_VALUE
                        )

                    except FileNotFoundError:
                        pass

            messagebox.showinfo(
                APP_NAME,
                "Windows startup setting updated."
            )

        except Exception as e:

            self.startup_var.set(
                not self.startup_var.get()
            )

            messagebox.showerror(
                APP_NAME,
                f"Could not update startup setting:\n{e}"
            )

    # -----------------------------------------------------
    # FIREBASE ONLINE USERS
    # -----------------------------------------------------

    def start_online_counter(self):

        self.online_running = True
        self.online_stop.clear()

        threading.Thread(
            target=self.firebase_worker,
            daemon=True
        ).start()

    def schedule_online_update(self, count):

        try:

            if self.online_running:

                self.root.after(
                    0,
                    lambda c=count: self.update_online_label(c)
                )

        except (tk.TclError, RuntimeError):
            pass

    def firebase_worker(self):

        auth_url = (
            "https://identitytoolkit.googleapis.com/v1/"
            "accounts:signUp?key="
            + FIREBASE_API_KEY
        )

        while self.online_running and not self.online_stop.is_set():

            if not self.firebase_uid or not self.firebase_token:

                try:

                    auth_data = http_json(
                        auth_url,
                        method="POST",
                        data={
                            "returnSecureToken": True
                        }
                    )

                    self.firebase_uid = auth_data["localId"]
                    self.firebase_token = auth_data["idToken"]

                except Exception:

                    self.schedule_online_update(None)
                    self.online_stop.wait(HEARTBEAT_INTERVAL)
                    continue

            try:

                uid = self.firebase_uid
                token = self.firebase_token

                encoded_token = urllib.parse.quote(
                    token,
                    safe=""
                )

                heartbeat_url = (
                    f"{FIREBASE_DB}/users/{uid}.json"
                    f"?auth={encoded_token}"
                )

                http_json(
                    heartbeat_url,
                    method="PUT",
                    data={
                        "last_seen": int(time.time()),
                        "version": APP_VERSION
                    }
                )

                users_url = (
                    f"{FIREBASE_DB}/users.json"
                    f"?auth={encoded_token}"
                )

                users = http_json(users_url)

                now = int(time.time())
                count = 0

                if isinstance(users, dict):

                    for user in users.values():

                        if not isinstance(user, dict):
                            continue

                        last_seen = user.get("last_seen", 0)

                        try:

                            if now - int(last_seen) <= ONLINE_TIMEOUT:
                                count += 1

                        except (ValueError, TypeError):
                            pass

                self.schedule_online_update(count)

            except Exception:

                self.schedule_online_update(None)

            self.online_stop.wait(HEARTBEAT_INTERVAL)

    def update_online_label(self, count):

        if not self.online_running or not self.online_label:
            return

        try:

            if not self.online_label.winfo_exists():
                return

            if count is None:

                self.online_label.config(
                    text="ONLINE: CONNECTION FAILED",
                    fg=RED
                )

            else:

                self.online_label.config(
                    text=f"ONLINE USERS: {count}",
                    fg=GREEN
                )

        except tk.TclError:
            pass

    # -----------------------------------------------------
    # UPDATE CENTER - GITHUB AUTO UPDATER
    # -----------------------------------------------------

    def open_update_center(self):

        page = tk.Toplevel(self.root)

        page.title("LCB TOOL - UPDATE CENTER")
        page.geometry("500x450")
        page.configure(bg=BG)
        page.resizable(False, False)
        page.transient(self.root)

        tk.Label(
            page,
            text="UPDATE CENTER",
            font=("Segoe UI", 23, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(pady=(24, 5))

        tk.Label(
            page,
            text=f"CURRENT VERSION: V{APP_VERSION}",
            font=("Segoe UI", 11, "bold"),
            fg=GREEN,
            bg=BG
        ).pack(pady=5)

        status = tk.Label(
            page,
            text="Ready to check for updates.",
            font=("Segoe UI", 10),
            fg=MUTED,
            bg=BG,
            wraplength=430,
            justify="center"
        )

        status.pack(pady=(24, 14))

        progress = ttk.Progressbar(
            page,
            orient="horizontal",
            length=360,
            mode="determinate",
            maximum=100
        )

        progress.pack(pady=8)

        percent_label = tk.Label(
            page,
            text="0%",
            font=("Segoe UI", 9, "bold"),
            fg=WHITE,
            bg=BG
        )

        percent_label.pack(pady=3)

        self.update_page_closed = False

        update_data = {
            "url": None,
            "version": None,
            "available": False
        }

        def safe_ui(callback):

            try:

                if page.winfo_exists():
                    page.after(0, callback)

            except tk.TclError:
                pass

        def check_update():

            status.config(
                text="Checking GitHub for updates..."
            )

            progress["value"] = 0
            percent_label.config(text="0%")

            check_button.config(state="disabled")
            download_button.config(state="disabled")

            def worker():

                try:

                    release = http_json(
                        GITHUB_RELEASE_API
                    )

                    version = release.get("tag_name", "")
                    assets = release.get("assets", [])

                    download_url = None
                    asset_size = 0
                    asset_name = ""

                    for asset in assets:

                        filename = asset.get("name", "")

                        if filename.lower().endswith(".exe"):

                            download_url = asset.get(
                                "browser_download_url"
                            )

                            asset_size = int(
                                asset.get("size", 0)
                            )

                            asset_name = filename
                            break

                    latest_number = version_tuple(version)
                    current_number = version_tuple(APP_VERSION)

                    if latest_number is None or current_number is None:

                        result = "Could not understand the version number."
                        available = False

                    elif latest_number <= current_number:

                        result = "YOUR LCB TOOL IS UP TO DATE."
                        available = False

                    elif not download_url:

                        result = (
                            f"NEW VERSION: {version}\n\n"
                            "No EXE file was attached to this release."
                        )

                        available = False

                    else:

                        result = (
                            f"NEW VERSION AVAILABLE: {version}\n\n"
                            f"EXE FILE: {asset_name}\n\n"
                            "Ready to download and update."
                        )

                        available = True

                    update_data["url"] = download_url
                    update_data["version"] = version
                    update_data["available"] = available
                    update_data["size"] = asset_size

                    def show_result():

                        status.config(text=result)

                        download_button.config(
                            state="normal" if available else "disabled"
                        )

                        check_button.config(state="normal")

                    safe_ui(show_result)

                except Exception as e:

                    error_text = str(e)

                    def show_error():

                        status.config(
                            text="UPDATE CHECK FAILED:\n" + error_text
                        )

                        check_button.config(state="normal")

                    safe_ui(show_error)

            threading.Thread(
                target=worker,
                daemon=True
            ).start()

        def download_update():

            if not update_data["available"]:
                return

            if not getattr(sys, "frozen", False):

                messagebox.showinfo(
                    APP_NAME,
                    "Automatic replacement is available only in the compiled EXE version.\n\n"
                    "Build and run LCB TOOL as a PyInstaller EXE first.",
                    parent=page
                )

                webbrowser.open(GITHUB_RELEASE_PAGE)
                return

            answer = messagebox.askyesno(
                "LCB TOOL UPDATE",
                (
                    f"New version {update_data['version']} is available.\n\n"
                    "Download this EXE and install the update?"
                ),
                parent=page
            )

            if not answer:
                return

            download_button.config(state="disabled")
            check_button.config(state="disabled")

            progress["value"] = 0
            percent_label.config(text="0%")
            status.config(text="Downloading new LCB TOOL version...")

            def worker():

                try:

                    url = update_data["url"]

                    request = urllib.request.Request(
                        url,
                        headers={
                            "User-Agent": "LCB-TOOL-Updater"
                        }
                    )

                    with urllib.request.urlopen(
                        request,
                        timeout=60
                    ) as response:

                        total = int(
                            response.headers.get(
                                "Content-Length",
                                update_data.get("size", 0)
                            )
                        )

                        temp_folder = Path(tempfile.gettempdir()) / "LCB_TOOL_UPDATE"
                        temp_folder.mkdir(parents=True, exist_ok=True)

                        downloaded_file = temp_folder / "LCB_TOOL_NEW.exe"
                        temporary_file = temp_folder / "LCB_TOOL_NEW.download"

                        received = 0

                        with open(temporary_file, "wb") as output:

                            while True:

                                chunk = response.read(1024 * 128)

                                if not chunk:
                                    break

                                output.write(chunk)
                                received += len(chunk)

                                if total > 0:

                                    percent = min(
                                        100,
                                        int(received * 100 / total)
                                    )

                                else:
                                    percent = 0

                                def update_progress(p=percent):

                                    try:

                                        if page.winfo_exists():

                                            progress["value"] = p
                                            percent_label.config(
                                                text=f"{p}%"
                                            )

                                    except tk.TclError:
                                        pass

                                safe_ui(update_progress)

                    if received <= 0:
                        raise RuntimeError("Downloaded file is empty.")

                    if total > 0 and received != total:
                        raise RuntimeError(
                            "Download was incomplete. Please try again."
                        )

                    os.replace(
                        temporary_file,
                        downloaded_file
                    )

                    def confirm_install():

                        status.config(
                            text="Download completed successfully."
                        )

                        percent_label.config(text="100%")
                        progress["value"] = 100

                        install = messagebox.askyesno(
                            "Install Update",
                            (
                                "Download completed successfully.\n\n"
                                f"New version: {update_data['version']}\n\n"
                                "LCB TOOL will close and install the new EXE.\n"
                                "Continue?"
                            ),
                            parent=page
                        )

                        if install:

                            try:

                                self.install_update(
                                    downloaded_file,
                                    page
                                )

                            except Exception as e:

                                messagebox.showerror(
                                    APP_NAME,
                                    f"Could not start updater:\n{e}",
                                    parent=page
                                )

                                download_button.config(state="normal")
                                check_button.config(state="normal")

                        else:

                            status.config(
                                text="Update downloaded. Installation cancelled."
                            )

                            download_button.config(state="normal")
                            check_button.config(state="normal")

                    safe_ui(confirm_install)

                except Exception as e:

                    error_text = str(e)

                    def show_download_error():

                        status.config(
                            text="DOWNLOAD FAILED:\n" + error_text
                        )

                        download_button.config(state="normal")
                        check_button.config(state="normal")

                    safe_ui(show_download_error)

            threading.Thread(
                target=worker,
                daemon=True
            ).start()

        def open_release():

            webbrowser.open(GITHUB_RELEASE_PAGE)

        check_button = tk.Button(
            page,
            text="CHECK FOR UPDATES",
            command=check_update,
            bg=RED,
            fg=WHITE,
            activebackground=RED_HOVER,
            activeforeground=WHITE,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=11
        )

        check_button.pack(pady=7)

        download_button = tk.Button(
            page,
            text="DOWNLOAD & UPDATE",
            command=download_update,
            bg=GREEN,
            fg=WHITE,
            activebackground=GREEN_HOVER,
            activeforeground=WHITE,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=11,
            state="disabled"
        )

        download_button.pack(pady=7)

        tk.Button(
            page,
            text="OPEN GITHUB RELEASES",
            command=open_release,
            bg=PANEL2,
            fg=WHITE,
            activebackground="#34343a",
            activeforeground=WHITE,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=8
        ).pack(pady=5)

        tk.Label(
            page,
            text="LCB TOOL | PRIME LEADER",
            font=("Segoe UI", 8),
            fg=MUTED,
            bg=BG
        ).pack(
            side="bottom",
            pady=14
        )

        page.protocol(
            "WM_DELETE_WINDOW",
            page.destroy
        )

    # -----------------------------------------------------
    # INSTALL DOWNLOADED UPDATE
    # -----------------------------------------------------

    def install_update(self, downloaded_file, update_page):

        if not getattr(sys, "frozen", False):
            raise RuntimeError(
                "This installation method requires the compiled EXE."
            )

        current_exe = Path(sys.executable).resolve()
        downloaded_file = Path(downloaded_file).resolve()

        if not downloaded_file.exists():
            raise FileNotFoundError("Downloaded update file was not found.")

        if not current_exe.exists():
            raise FileNotFoundError("Current LCB TOOL EXE was not found.")

        # Save current settings before closing.
        self.save_settings()

        self.online_running = False
        self.online_stop.set()

        try:

            self.user.ReleaseDC(
                None,
                self.dc
            )

        except Exception:
            pass

        # Create a separate updater batch file.
        # It waits until this EXE closes, then replaces it.

        updater_folder = Path(tempfile.gettempdir()) / "LCB_TOOL_UPDATE"
        updater_folder.mkdir(parents=True, exist_ok=True)

        updater_file = updater_folder / "LCB_TOOL_UPDATER.cmd"

        pid = os.getpid()

        batch_code = f"""@echo off
setlocal
title LCB TOOL UPDATER

set "APP_PID={pid}"
set "NEW_FILE={downloaded_file}"
set "TARGET_FILE={current_exe}"

:WAIT_FOR_APP
tasklist /FI "PID eq %APP_PID%" 2>NUL | find "%APP_PID%" >NUL
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto WAIT_FOR_APP
)

if not exist "%NEW_FILE%" (
    start "" "%TARGET_FILE%"
    exit /b 1
)

copy /Y "%NEW_FILE%" "%TARGET_FILE%" >nul

if errorlevel 1 (
    start "" "%TARGET_FILE%"
    exit /b 1
)

del "%NEW_FILE%" >nul 2>&1
start "" "%TARGET_FILE%"

del "%~f0" >nul 2>&1
exit /b 0
"""

        updater_file.write_text(
            batch_code,
            encoding="utf-8"
        )

        creation_flags = getattr(
            subprocess,
            "CREATE_NO_WINDOW",
            0
        )

        subprocess.Popen(
            [
                "cmd.exe",
                "/c",
                str(updater_file)
            ],
            cwd=str(updater_folder),
            creationflags=creation_flags,
            close_fds=True
        )

        # Close Update Center and main app.
        try:
            update_page.destroy()
        except Exception:
            pass

        self.root.destroy()

    # -----------------------------------------------------
    # CLOSE
    # -----------------------------------------------------

    def close(self):

        self.online_running = False
        self.online_stop.set()

        self.save_settings()

        try:

            self.user.ReleaseDC(
                None,
                self.dc
            )

        except Exception:
            pass

        self.root.destroy()


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    if os.name != "nt":

        print("LCB TOOL is intended for Windows.")

    else:

        startup_apply = (
            "--startup-apply" in sys.argv
        )

        if startup_apply:

            root = tk.Tk()
            root.withdraw()

            try:

                ColorTool(
                    root,
                    startup_apply=True
                )

            except Exception:

                root.destroy()

        else:

            login_root = tk.Tk()

            login = LoginPage(
                login_root
            )

            login_root.mainloop()

            if login.success:

                root = tk.Tk()

                try:

                    app = ColorTool(root)

                    root.mainloop()

                except Exception as e:

                    try:
                        root.destroy()
                    except Exception:
                        pass

                    messagebox.showerror(
                        APP_NAME,
                        f"LCB TOOL Error:\n{e}"
                    )
