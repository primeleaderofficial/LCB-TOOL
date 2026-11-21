import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ctypes, json, os, sys, subprocess, random
from pathlib import Path

APP_NAME = "LCB TOOL"
APP_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME.replace(" ", "_")
APP_DIR.mkdir(parents=True, exist_ok=True)
PRESET_FILE = APP_DIR / "presets.json"
SETTINGS_FILE = APP_DIR / "settings.json"
LOGIN_FILE = APP_DIR / "login.json"
LOGIN_USERNAME = "geecolor"
LOGIN_PASSWORD = "200913"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE = "LCB_TOOL"
DEFAULTS = {"Brightness": 0, "Contrast": 100, "Gamma": 100, "Red": 100, "Green": 100, "Blue": 100, "Saturation": 100, "Vibrance": 0, "Temperature": 0}

# V3 visual theme: charcoal / white / red, with subtle animated snowfall
BG = "#0b0b0d"
PANEL = "#17171a"
PANEL2 = "#202024"
WHITE = "#f4f4f5"
MUTED = "#a5a5ad"
RED = "#d92d35"
RED_HOVER = "#f0444d"
GREEN = "#20b15a"
GREEN_HOVER = "#2cc96b"

class SnowBackground:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, bg=BG, highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.flakes = []
        # Lower the Canvas widget behind other Tk widgets (Canvas.lower is for canvas items).
        self.root.tk.call("lower", self.canvas._w)
        self.root.bind("<Configure>", self.resize, add="+")
        self.seed()
        self.animate()
    def seed(self):
        w=max(self.root.winfo_width(), 430); h=max(self.root.winfo_height(), 390)
        for _ in range(42):
            x=random.randrange(w); y=random.randrange(h); r=random.choice((1,1,2,2,3))
            item=self.canvas.create_oval(x,y,x+r*2,y+r*2,fill=random.choice(("#d8d8dc","#eeeeef","#9c9ca4")),outline="")
            self.flakes.append((item, random.uniform(0.7,2.3), random.uniform(-0.5,0.5)))
    def resize(self, event):
        if event.widget is self.root:
            self.canvas.place(x=0,y=0,relwidth=1,relheight=1)
    def animate(self):
        h=max(self.root.winfo_height(),390); w=max(self.root.winfo_width(),430)
        for item, speed, drift in self.flakes:
            self.canvas.move(item,drift,speed)
            x1,y1,x2,y2=self.canvas.coords(item)
            if y1>h:
                new_x=random.randrange(max(1,w-8)); size=max(2,x2-x1)
                self.canvas.coords(item,new_x,-5,new_x+size,-3)
        self.root.after(55,self.animate)

class RoundButton(tk.Canvas):
    def __init__(self, parent, text, command, bg=RED, hover=RED_HOVER, fg=WHITE, height=34, width=125, **kwargs):
        super().__init__(parent, height=height, width=width, bg=parent.cget("bg"), highlightthickness=0, bd=0, cursor="hand2")
        self.text=text; self.command=command; self.normal=bg; self.hover=hover; self.fg=fg; self.height_px=height
        self.bind("<Enter>",lambda _e:self.draw(self.hover)); self.bind("<Leave>",lambda _e:self.draw(self.normal)); self.bind("<Button-1>",lambda _e:self.command())
        self.draw(bg)
    def draw(self,color):
        self.delete("all"); w=max(self.winfo_width(),int(self.cget("width"))); h=self.height_px
        r=9
        self.create_arc(0,0,r*2,r*2,start=90,extent=90,fill=color,outline=color)
        self.create_arc(w-r*2,0,w,h,start=0,extent=90,fill=color,outline=color)
        self.create_arc(w-r*2,h-r*2,w,h,start=270,extent=90,fill=color,outline=color)
        self.create_arc(0,h-r*2,r*2,h,start=180,extent=90,fill=color,outline=color)
        self.create_rectangle(r,0,w-r,h,fill=color,outline=color); self.create_rectangle(0,r,w,h-r,fill=color,outline=color)
        self.create_text(w/2,h/2,text=self.text,fill=self.fg,font=("Segoe UI",9,"bold"))


class LoginPage:
    def __init__(self, root):
        self.root = root
        self.success = False
        root.title("LCB TOOL - Login")
        root.geometry("430x390")
        root.resizable(False, False)
        root.configure(bg=BG)
        self.snow = SnowBackground(root)
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        remembered = self.load_saved_credentials()

        header = tk.Frame(root, bg=BG, height=105)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="LCB TOOL", font=("Segoe UI", 26, "bold"),
                 fg=WHITE, bg=BG).pack(pady=(17, 0))
        tk.Label(header, text="WELCOME BACK", font=("Segoe UI", 9, "bold"),
                 fg=RED, bg=BG).pack()

        body = tk.Frame(root, bg=BG, padx=34, pady=22)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Login to continue", font=("Segoe UI", 13, "bold"),
                 fg=WHITE, bg=BG).pack(pady=(0, 13))
        tk.Label(body, text="Username", font=("Segoe UI", 9, "bold"),
                 fg=WHITE, bg=BG).pack(anchor="w")
        self.username = tk.Entry(body, font=("Segoe UI", 10), relief="flat",
                                bg=PANEL2, fg=WHITE, insertbackground=WHITE, bd=0)
        self.username.pack(fill="x", ipady=6, pady=(4, 10))
        tk.Label(body, text="Password", font=("Segoe UI", 9, "bold"),
                 fg=WHITE, bg=BG).pack(anchor="w")
        self.password = tk.Entry(body, show="*", font=("Segoe UI", 10), relief="flat",
                                 bg=PANEL2, fg=WHITE, insertbackground=WHITE, bd=0)
        self.password.pack(fill="x", ipady=6, pady=(4, 8))
        self.remember = tk.BooleanVar(value=True)
        tk.Checkbutton(body, text="Remember username & password",
                      variable=self.remember, bg=BG, fg=WHITE,
                      activebackground=BG, selectcolor=PANEL2,
                      font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 12))
        RoundButton(body, text="LOGIN", command=self.check_login, bg=RED, hover=RED_HOVER, height=33, width=300).pack(fill="x", pady=(2,0))
        self.password.bind("<Return>", lambda _e: self.check_login())
        self.username.bind("<Return>", lambda _e: self.password.focus_set())
        if remembered:
            self.username.insert(0, remembered.get("username", ""))
            self.password.insert(0, remembered.get("password", ""))
            self.remember.set(True)
            self.password.focus_set()
        else:
            self.username.focus_set()

    def load_saved_credentials(self):
        try:
            data = json.loads(LOGIN_FILE.read_text(encoding="utf-8"))
            if data.get("remembered"):
                return {"username": data.get("username", ""), "password": data.get("password", "")}
        except Exception:
            pass
        return None

    def check_login(self):
        if self.username.get().strip() == LOGIN_USERNAME and self.password.get() == LOGIN_PASSWORD:
            self.success = True
            if self.remember.get():
                try:
                    LOGIN_FILE.write_text(json.dumps({
                        "remembered": True,
                        "username": self.username.get().strip(),
                        "password": self.password.get()
                    }), encoding="utf-8")
                except Exception as e:
                    messagebox.showwarning("LCB TOOL", f"Could not save remembered credentials:\n{e}", parent=self.root)
            else:
                try:
                    LOGIN_FILE.unlink(missing_ok=True)
                except Exception:
                    pass
            self.root.destroy()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.", parent=self.root)
            self.password.delete(0, "end")
            self.password.focus_set()


class ColorTool:
    def __init__(self, root, startup_apply=False):
        self.root = root
        self.startup_apply = startup_apply
        root.title(APP_NAME)
        root.geometry("790x700")
        root.minsize(730, 650)
        root.configure(bg=BG)
        self.snow = SnowBackground(root)
        self.gdi = ctypes.WinDLL("gdi32")
        self.user = ctypes.WinDLL("user32")
        self.ramp_type = (ctypes.c_ushort * 256) * 3
        self.original = self.ramp_type()
        self.current = self.ramp_type()
        self.dc = self.user.GetDC(None)
        self.gdi.GetDeviceGammaRamp(self.dc, ctypes.byref(self.original))
        self.presets = {}
        self.load_presets()
        self.vars = {}
        self.load_settings()
        if startup_apply:
            self.apply_values(save=False)
            self.user.ReleaseDC(None, self.dc)
            root.destroy()
            return
        self.build_ui()
        self.apply_values(save=False)
        root.protocol("WM_DELETE_WINDOW", self.close)

    def build_ui(self):
        header = tk.Frame(self.root, bg=BG, height=88)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="LCB TOOL", font=("Segoe UI", 25, "bold"), fg=WHITE, bg=BG).pack(pady=(12, 0))
        tk.Label(header, text="LIVE DISPLAY COLOR CONTROL", font=("Segoe UI", 9, "bold"), fg=RED, bg=BG).pack()
        main = tk.Frame(self.root, bg=BG, padx=20, pady=14)
        main.pack(fill="both", expand=True)
        panel = tk.Frame(main, bg=PANEL, highlightbackground="#36363b", highlightthickness=1, padx=16, pady=10)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Adjust colours in real time", font=("Segoe UI", 14, "bold"), bg=PANEL, fg=WHITE).pack(anchor="w", pady=(0, 8))
        definitions = [("Brightness", -100, 100), ("Contrast", 50, 150), ("Gamma", 50, 200), ("Red", 50, 150), ("Green", 50, 150), ("Blue", 50, 150), ("Saturation", 0, 200), ("Vibrance", -100, 100), ("Temperature", -100, 100)]
        for name, lo, hi in definitions:
            row = tk.Frame(panel, bg=PANEL)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=name, width=12, anchor="w", font=("Segoe UI", 10, "bold"), bg=PANEL, fg=WHITE).pack(side="left")
            var = tk.IntVar(value=self.settings.get(name, DEFAULTS[name]))
            self.vars[name] = var
            scale = tk.Scale(row, from_=lo, to=hi, orient="horizontal", variable=var, showvalue=False, length=440,
                             bg=PANEL, fg=RED, troughcolor="#45454b", highlightthickness=0,
                             activebackground=RED_HOVER, command=lambda _v: self.apply_values(save=False))
            scale.pack(side="left", fill="x", expand=True)
            tk.Label(row, textvariable=var, width=5, bg=PANEL, fg=WHITE, font=("Segoe UI", 9)).pack(side="right")

        preset_row = tk.Frame(main, bg=BG)
        preset_row.pack(fill="x", pady=(14, 5))
        tk.Label(preset_row, text="Preset", bg=BG, fg=WHITE, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))
        self.preset_var = tk.StringVar()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("LCB.TCombobox", fieldbackground=PANEL2, background=PANEL2, foreground=WHITE, arrowcolor=WHITE)
        style.map("LCB.TCombobox", fieldbackground=[("readonly", PANEL2)], foreground=[("readonly", WHITE)])
        self.combo = ttk.Combobox(preset_row, textvariable=self.preset_var, state="readonly", width=20)
        self.combo.pack(side="left")
        self.refresh_combo()
        for label, func in [("SAVE PRESET", self.save_preset), ("LOAD", self.load_selected), ("RESET DEFAULT", self.reset)]:
            RoundButton(preset_row, text=label, command=func, bg=RED, hover=RED_HOVER, height=30, width=112).pack(side="left", padx=4)

        action_row = tk.Frame(main, bg=BG)
        action_row.pack(fill="x", pady=(8, 0))
        RoundButton(action_row, text="APPLY & SAVE", command=self.apply_and_save, bg=GREEN, hover=GREEN_HOVER, height=34, width=145).pack(side="left")
        self.startup_var = tk.BooleanVar(value=self.startup_enabled())
        tk.Checkbutton(action_row, text="Apply saved colours when Windows starts", variable=self.startup_var, command=self.toggle_startup,
                      bg=BG, fg=WHITE, activebackground=BG, selectcolor=PANEL2, font=("Segoe UI", 9, "bold")).pack(side="left", padx=12)
        tk.Label(main, text="Changes remain after closing LCB TOOL. Apply at Windows startup is optional.", bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(8, 0))

    def apply_values(self, save=False):
        if not self.vars:
            return
        brightness = self.vars["Brightness"].get()
        contrast = self.vars["Contrast"].get() / 100.0
        gamma = self.vars["Gamma"].get() / 100.0
        multipliers = {c: self.vars[c].get() / 100.0 for c in ("Red", "Green", "Blue")}
        saturation = self.vars["Saturation"].get() / 100.0
        vibrance = self.vars["Vibrance"].get() / 100.0
        temperature = self.vars["Temperature"].get() / 100.0
        # Gamma ramps operate on each channel separately. Saturation/vibrance are
        # approximations through channel curves; true per-pixel colour mixing is not available here.
        temp_offsets = {"Red": temperature * 0.12, "Green": -temperature * 0.015, "Blue": -temperature * 0.12}
        for channel, cname in enumerate(("Red", "Green", "Blue")):
            for i in range(256):
                x = i / 255.0
                x = (x - 0.5) * contrast + 0.5 + brightness / 255.0
                x = max(0.0, min(1.0, x))
                x = pow(x, 1.0 / max(0.05, gamma))
                # Expand/reduce each channel around mid-gray for saturation approximation.
                x = 0.5 + (x - 0.5) * saturation
                # Vibrance approximation: stronger effect in midtones, gentler at extremes.
                midtone_weight = 1.0 - abs(2.0 * x - 1.0)
                x = 0.5 + (x - 0.5) * (1.0 + vibrance * 0.30 * midtone_weight)
                x = x * multipliers[cname] + temp_offsets[cname]
                x = max(0.0, min(1.0, x))
                self.current[channel][i] = int(x * 65535)
        try:
            self.gdi.SetDeviceGammaRamp(self.dc, ctypes.byref(self.current))
        except Exception as e:
            if not save:
                return
            messagebox.showerror(APP_NAME, f"Could not apply display ramp:\n{e}")
        if save:
            self.save_settings()

    def apply_and_save(self):
        self.apply_values(save=True)
        messagebox.showinfo(APP_NAME, "Display colours applied and saved. They will remain after closing this tool.")

    def values(self):
        return {k: v.get() for k, v in self.vars.items()}

    def set_values(self, data):
        for k, v in data.items():
            if k in self.vars:
                self.vars[k].set(v)
        self.apply_values(save=False)

    def load_settings(self):
        try:
            self.settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            self.settings = DEFAULTS.copy()
        for key, default in DEFAULTS.items():
            self.settings.setdefault(key, default)

    def save_settings(self):
        data = self.values() if self.vars else self.settings
        try:
            SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self.settings = data.copy()
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Settings save error:\n{e}")

    def load_presets(self):
        try:
            self.presets = json.loads(PRESET_FILE.read_text(encoding="utf-8"))
        except Exception:
            self.presets = {}

    def write_presets(self):
        try:
            PRESET_FILE.write_text(json.dumps(self.presets, indent=2), encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Preset save error", str(e))

    def refresh_combo(self):
        if hasattr(self, "combo"):
            self.combo["values"] = list(self.presets.keys())

    def save_preset(self):
        name = simpledialog.askstring("Save Preset", "Preset name:", parent=self.root)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        self.presets[name] = self.values()
        self.write_presets()
        self.refresh_combo()
        self.preset_var.set(name)
        messagebox.showinfo(APP_NAME, "Preset saved!")

    def load_selected(self):
        name = self.preset_var.get()
        if name and name in self.presets:
            self.set_values(self.presets[name])
            self.save_settings()
        else:
            messagebox.showwarning(APP_NAME, "Select a saved preset first.")

    def reset(self):
        for key, value in DEFAULTS.items():
            self.vars[key].set(value)
        self.apply_values(save=False)
        self.save_settings()

    def startup_enabled(self):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
                winreg.QueryValueEx(key, RUN_VALUE)
            return True
        except Exception:
            return False

    def startup_command(self):
        if getattr(sys, "frozen", False):
            return f'"{sys.executable}" --startup-apply'
        py = sys.executable
        if py.lower().endswith("python.exe"):
            py = py[:-10] + "pythonw.exe"
        return f'"{py}" "{Path(__file__).resolve()}" --startup-apply'

    def toggle_startup(self):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                if self.startup_var.get():
                    self.save_settings()
                    winreg.SetValueEx(key, RUN_VALUE, 0, winreg.REG_SZ, self.startup_command())
                else:
                    try:
                        winreg.DeleteValue(key, RUN_VALUE)
                    except FileNotFoundError:
                        pass
            messagebox.showinfo(APP_NAME, "Windows startup setting updated.")
        except Exception as e:
            self.startup_var.set(not self.startup_var.get())
            messagebox.showerror(APP_NAME, f"Could not update startup setting:\n{e}")

    def close(self):
        # Deliberately do not restore the old ramp. The applied colour state remains active.
        self.save_settings()
        try:
            self.user.ReleaseDC(None, self.dc)
        except Exception:
            pass
        self.root.destroy()

if __name__ == "__main__":
    startup_apply = "--startup-apply" in sys.argv
    if os.name != "nt":
        print("LCB TOOL is intended for Windows.")
    elif startup_apply:
        root = tk.Tk()
        root.withdraw()
        ColorTool(root, startup_apply=True)
    else:
        login_root = tk.Tk()
        login = LoginPage(login_root)
        login_root.mainloop()
        if login.success:
            root = tk.Tk()
            app = ColorTool(root)
            root.mainloop()
