"""World Clock - one Python/Kivy codebase for Windows/Mac/Linux AND Android (APK)."""
import json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.utils import platform

Window.clearcolor = (.06, .07, .10, 1)
if platform not in ("android", "ios"):
    Window.size = (430, 780)

US = {}
for zone, names in {
    "America/New_York": "Connecticut,Delaware,Florida,Georgia,Indiana,Kentucky,Maine,Maryland,Massachusetts,Michigan,New Hampshire,New Jersey,New York,North Carolina,Ohio,Pennsylvania,Rhode Island,South Carolina,Vermont,Virginia,West Virginia,Washington DC",
    "America/Chicago": "Alabama,Arkansas,Illinois,Iowa,Kansas,Louisiana,Minnesota,Mississippi,Missouri,Nebraska,North Dakota,Oklahoma,South Dakota,Tennessee,Texas,Wisconsin",
    "America/Denver": "Colorado,Idaho,Montana,New Mexico,Utah,Wyoming",
    "America/Phoenix": "Arizona",
    "America/Los_Angeles": "California,Nevada,Oregon,Washington",
    "America/Anchorage": "Alaska",
    "Pacific/Honolulu": "Hawaii",
}.items():
    for n in names.split(","):
        US[n] = zone

COUNTRIES = {"United States": None}
for line in """Bulgaria:Europe/Sofia|United Kingdom:Europe/London|Ireland:Europe/Dublin|Germany:Europe/Berlin|France:Europe/Paris|Spain:Europe/Madrid|Portugal:Europe/Lisbon|Italy:Europe/Rome|Netherlands:Europe/Amsterdam|Belgium:Europe/Brussels|Switzerland:Europe/Zurich|Austria:Europe/Vienna|Poland:Europe/Warsaw|Romania:Europe/Bucharest|Greece:Europe/Athens|Turkey:Europe/Istanbul|Ukraine:Europe/Kyiv|Russia (Moscow):Europe/Moscow|Sweden:Europe/Stockholm|Norway:Europe/Oslo|Finland:Europe/Helsinki|Denmark:Europe/Copenhagen|Canada (Toronto):America/Toronto|Canada (Vancouver):America/Vancouver|Mexico:America/Mexico_City|Brazil (Sao Paulo):America/Sao_Paulo|Argentina:America/Argentina/Buenos_Aires|Colombia:America/Bogota|Chile:America/Santiago|Egypt:Africa/Cairo|Nigeria:Africa/Lagos|Kenya:Africa/Nairobi|South Africa:Africa/Johannesburg|Morocco:Africa/Casablanca|Saudi Arabia:Asia/Riyadh|UAE (Dubai):Asia/Dubai|Israel:Asia/Jerusalem|Iran:Asia/Tehran|Pakistan:Asia/Karachi|India:Asia/Kolkata|Bangladesh:Asia/Dhaka|Thailand:Asia/Bangkok|Vietnam:Asia/Ho_Chi_Minh|Indonesia (Jakarta):Asia/Jakarta|China:Asia/Shanghai|Hong Kong:Asia/Hong_Kong|Singapore:Asia/Singapore|Philippines:Asia/Manila|Japan:Asia/Tokyo|South Korea:Asia/Seoul|Australia (Sydney):Australia/Sydney|Australia (Perth):Australia/Perth|New Zealand:Pacific/Auckland""".split("|"):
    k, v = line.split(":")
    COUNTRIES[k] = v


def now(tz):
    return datetime.now(ZoneInfo(tz)) if tz else datetime.now().astimezone()


class WorldClock(App):
    def build(self):
        self.title = "World Clock"
        self.path = os.path.join(self.user_data_dir, "clocks.json")
        self.clocks = [{"name": "My time", "tz": None}]
        self.main = 0
        self.rows = []
        self.load()
        self.root_box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        # main clock card
        card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(190), padding=dp(10))
        self.m_name = Label(font_size=dp(20), color=(.55, .75, 1, 1), size_hint_y=.25)
        self.m_time = Label(font_size=dp(64), bold=True, size_hint_y=.5)
        self.m_date = Label(font_size=dp(16), color=(.7, .7, .75, 1), size_hint_y=.25)
        for w in (self.m_name, self.m_time, self.m_date):
            card.add_widget(w)
        self.root_box.add_widget(card)
        # list of clocks
        self.list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        self.list.bind(minimum_height=self.list.setter("height"))
        sv = ScrollView()
        sv.add_widget(self.list)
        self.root_box.add_widget(sv)
        # picker
        pick = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
        self.sp_country = Spinner(text="Pick country", values=sorted(COUNTRIES), size_hint_x=.4)
        self.sp_state = Spinner(text="State", values=sorted(US), size_hint_x=.35, disabled=True)
        self.sp_country.bind(text=lambda s, t: setattr(self.sp_state, "disabled", t != "United States"))
        add = Button(text="+ Add", size_hint_x=.25, background_color=(.2, .5, .9, 1), on_release=self.add_clock)
        for w in (self.sp_country, self.sp_state, add):
            pick.add_widget(w)
        self.root_box.add_widget(pick)
        if sys.platform == "win32":
            self.btn_start = Button(size_hint_y=None, height=dp(40), on_release=self.toggle_startup)
            self.root_box.add_widget(self.btn_start)
            self.update_startup_btn()
        self.rebuild()
        Clock.schedule_interval(self.tick, 1)
        return self.root_box

    # ---------- data ----------
    def load(self):
        try:
            d = json.load(open(self.path))
            self.clocks, self.main = d["clocks"], d["main"]
        except Exception:
            pass

    def save(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            json.dump({"clocks": self.clocks, "main": self.main}, open(self.path, "w"))
        except Exception:
            pass

    def add_clock(self, *_):
        c = self.sp_country.text
        if c == "United States":
            s = self.sp_state.text
            if s not in US:
                return
            name, tz = f"{s}, USA", US[s]
        elif c in COUNTRIES:
            name, tz = c, COUNTRIES[c]
        else:
            return
        if any(x["tz"] == tz and x["name"] == name for x in self.clocks):
            return
        self.clocks.append({"name": name, "tz": tz})
        self.save()
        self.rebuild()

    def set_main(self, i):
        self.main = i
        self.save()
        self.rebuild()

    def remove(self, i):
        if len(self.clocks) <= 1:
            return
        del self.clocks[i]
        self.main = min(self.main, len(self.clocks) - 1) if i != self.main else 0
        self.save()
        self.rebuild()

    # ---------- ui ----------
    def rebuild(self):
        self.list.clear_widgets()
        self.rows = []
        for i, c in enumerate(self.clocks):
            if i == self.main:
                continue
            row = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(8), spacing=dp(6))
            info = BoxLayout(orientation="vertical", size_hint_x=.55)
            n = Label(text=c["name"], halign="left", font_size=dp(16))
            n.bind(size=lambda w, s: setattr(w, "text_size", s))
            d = Label(font_size=dp(12), color=(.6, .6, .65, 1), halign="left")
            d.bind(size=lambda w, s: setattr(w, "text_size", s))
            info.add_widget(n); info.add_widget(d)
            t = Label(font_size=dp(26), bold=True, size_hint_x=.25)
            b1 = Button(text="Main", size_hint_x=.12, on_release=lambda _, i=i: self.set_main(i))
            b2 = Button(text="X", size_hint_x=.08, background_color=(.8, .25, .25, 1), on_release=lambda _, i=i: self.remove(i))
            for w in (info, t, b1, b2):
                row.add_widget(w)
            self.list.add_widget(row)
            self.rows.append((c, t, d))
        self.tick()

    def tick(self, *_):
        m = self.clocks[self.main]
        n = now(m["tz"])
        self.m_name.text = m["name"] + "  (main)"
        self.m_time.text = n.strftime("%H:%M:%S")
        self.m_date.text = n.strftime("%A, %d %B %Y")
        for c, t, d in self.rows:
            n = now(c["tz"])
            t.text = n.strftime("%H:%M")
            d.text = n.strftime("%a %d %b")

    # ---------- Android notification on exit ----------
    def on_start(self):
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.POST_NOTIFICATIONS])
            except Exception:
                pass

    def on_pause(self):
        if platform == "android":
            try:
                from plyer import notification
                m = self.clocks[self.main]
                others = [c for c in self.clocks if c is not m][:2]
                notification.notify(
                    title=f"{m['name']}  {now(m['tz']).strftime('%H:%M')}",
                    message="   |   ".join(f"{c['name']} {now(c['tz']).strftime('%H:%M')}" for c in others),
                    app_name="World Clock", timeout=30)
            except Exception:
                pass
        return True

    # ---------- Windows start-with-PC ----------
    RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def startup_cmd(self):
        if getattr(sys, "frozen", False):
            return f'"{sys.executable}"'
        py = sys.executable.replace("python.exe", "pythonw.exe")
        return f'"{py}" "{os.path.abspath(__file__)}"'

    def startup_on(self):
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.RUN_KEY) as k:
                winreg.QueryValueEx(k, "WorldClock")
            return True
        except OSError:
            return False

    def toggle_startup(self, *_):
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.RUN_KEY, 0, winreg.KEY_ALL_ACCESS) as k:
            if self.startup_on():
                winreg.DeleteValue(k, "WorldClock")
            else:
                winreg.SetValueEx(k, "WorldClock", 0, winreg.REG_SZ, self.startup_cmd())
        self.update_startup_btn()

    def update_startup_btn(self):
        self.btn_start.text = "Start with PC: " + ("ON" if self.startup_on() else "OFF")


if __name__ == "__main__":
    WorldClock().run()
