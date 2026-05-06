"""
Undetected PC Tweaks — Main Application
A modern HUD-style PC optimization tool with KeyAuth authentication.
Community: Undetected
"""
import os
import threading

import customtkinter as ctk
from PIL import Image

from keyauth_api import KeyAuth
from tweaks import (
    ALL_TWEAKS,
    TWEAK_CATEGORIES,
    apply_tweak,
    get_tweaks_by_category,
    load_tweaks_state,
    revert_tweak,
)

# ── App-wide configuration ──────────────────────────────────────
APP_NAME = os.environ.get("KEYAUTH_APP_NAME", "WaleAdvanced")
APP_SECRET = os.environ.get("KEYAUTH_APP_SECRET", "")
APP_VERSION = os.environ.get("KEYAUTH_APP_VERSION", "1.0")
OWNER_ID = os.environ.get("KEYAUTH_OWNER_ID", "")

# ── Theme colours ───────────────────────────────────────────────
BG_DARK = "#0C0C12"
BG_PANEL = "#111119"
BG_CARD = "#181822"
BG_HOVER = "#1E1E2E"
CYAN = "#00FFF2"
CYAN_DIM = "#00B8AD"
CYAN_DARK = "#005F58"
RED = "#FF3B5C"
GREEN = "#00FF88"
YELLOW = "#FFD600"
TEXT_PRIMARY = "#EAEAEA"
TEXT_SECONDARY = "#888899"
TEXT_MUTED = "#555566"

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


class HUDButton(ctk.CTkButton):
    """A styled HUD button with glow effect."""

    def __init__(self, master, **kwargs):
        defaults = {
            "fg_color": "transparent",
            "border_color": CYAN,
            "border_width": 1,
            "hover_color": CYAN_DARK,
            "text_color": CYAN,
            "corner_radius": 4,
            "font": ("Consolas", 13),
            "height": 36,
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)


class HUDToggle(ctk.CTkFrame):
    """A tweak toggle row with name, description, risk badge, and switch."""

    def __init__(self, master, tweak: dict, is_applied: bool, on_toggle, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=6, **kwargs)
        self.tweak = tweak
        self.on_toggle = on_toggle

        self.grid_columnconfigure(1, weight=1)
        self.configure(height=64)

        # Risk badge
        risk_colors = {"low": GREEN, "medium": YELLOW, "high": RED}
        risk_col = risk_colors.get(tweak.get("risk", "low"), TEXT_SECONDARY)

        risk_lbl = ctk.CTkLabel(
            self,
            text=f" {tweak['risk'].upper()} ",
            font=("Consolas", 9, "bold"),
            text_color=BG_DARK,
            fg_color=risk_col,
            corner_radius=3,
            width=52,
            height=18,
        )
        risk_lbl.grid(row=0, column=0, padx=(12, 6), pady=(12, 0), sticky="w")

        # Name
        name_lbl = ctk.CTkLabel(
            self,
            text=tweak["name"],
            font=("Consolas", 13, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        name_lbl.grid(row=0, column=1, padx=4, pady=(12, 0), sticky="w")

        # Description
        desc_lbl = ctk.CTkLabel(
            self,
            text=tweak["description"],
            font=("Consolas", 11),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        desc_lbl.grid(row=1, column=0, columnspan=2, padx=(12, 4), pady=(0, 10), sticky="w")

        # Toggle switch
        self.switch_var = ctk.BooleanVar(value=is_applied)
        self.switch = ctk.CTkSwitch(
            self,
            text="",
            variable=self.switch_var,
            onvalue=True,
            offvalue=False,
            command=self._on_switch,
            progress_color=CYAN,
            button_color=CYAN,
            button_hover_color=CYAN_DIM,
            fg_color=TEXT_MUTED,
            width=48,
        )
        self.switch.grid(row=0, column=2, rowspan=2, padx=(4, 16), pady=10, sticky="e")

        # Status label
        self.status_lbl = ctk.CTkLabel(
            self,
            text="ACTIVE" if is_applied else "",
            font=("Consolas", 9),
            text_color=GREEN if is_applied else TEXT_MUTED,
            width=50,
        )
        self.status_lbl.grid(row=0, column=3, rowspan=2, padx=(0, 12), pady=10, sticky="e")

    def _on_switch(self):
        self.on_toggle(self.tweak, self.switch_var.get(), self)

    def set_status(self, applied: bool, msg: str = ""):
        if applied:
            self.status_lbl.configure(text="ACTIVE", text_color=GREEN)
        else:
            self.status_lbl.configure(text=msg if msg else "", text_color=RED if msg else TEXT_MUTED)


# ── Login Window ─────────────────────────────────────────────────
class LoginWindow(ctk.CTkToplevel):
    """KeyAuth login / register window with HUD styling."""

    def __init__(self, master, keyauth: KeyAuth, on_success):
        super().__init__(master)
        self.title("UNDETECTED — Authentication")
        self.geometry("480x620")
        self.configure(fg_color=BG_DARK)
        self.resizable(False, False)
        self.keyauth = keyauth
        self.on_success = on_success

        # Center
        self.transient(master)
        self.grab_set()

        # Logo
        try:
            logo_path = os.path.join(ASSET_DIR, "logo.png")
            logo_img = Image.open(logo_path).resize((120, 120))
            self.logo_photo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(120, 120))
            logo_label = ctk.CTkLabel(self, image=self.logo_photo, text="")
            logo_label.pack(pady=(24, 4))
        except Exception:
            pass

        ctk.CTkLabel(
            self, text="UNDETECTED", font=("Consolas", 28, "bold"), text_color=CYAN
        ).pack(pady=(0, 2))
        ctk.CTkLabel(
            self, text="PC TWEAKS", font=("Consolas", 12), text_color=TEXT_SECONDARY
        ).pack(pady=(0, 20))

        # Tab view
        self.tabs = ctk.CTkTabview(
            self, fg_color=BG_PANEL, segmented_button_fg_color=BG_CARD,
            segmented_button_selected_color=CYAN_DARK,
            segmented_button_selected_hover_color=CYAN_DARK,
            segmented_button_unselected_color=BG_CARD,
            segmented_button_unselected_hover_color=BG_HOVER,
            text_color=CYAN,
            width=400, height=320,
        )
        self.tabs.pack(padx=20, pady=0, fill="x")

        # Login tab
        login_tab = self.tabs.add("LOGIN")
        self._build_login_tab(login_tab)

        # Register tab
        reg_tab = self.tabs.add("REGISTER")
        self._build_register_tab(reg_tab)

        # License tab
        lic_tab = self.tabs.add("LICENSE")
        self._build_license_tab(lic_tab)

        # Status
        self.status_label = ctk.CTkLabel(
            self, text="", font=("Consolas", 11), text_color=TEXT_SECONDARY
        )
        self.status_label.pack(pady=(10, 4))

    def _entry(self, parent, placeholder, show=""):
        e = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            show=show,
            font=("Consolas", 13),
            fg_color=BG_CARD,
            border_color=CYAN_DARK,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            corner_radius=4,
            height=38,
        )
        e.pack(fill="x", padx=20, pady=6)
        return e

    def _build_login_tab(self, tab):
        ctk.CTkLabel(tab, text="", height=8).pack()
        self.login_user = self._entry(tab, "Username")
        self.login_pass = self._entry(tab, "Password", show="•")
        HUDButton(tab, text="▸  LOGIN", command=self._do_login).pack(
            fill="x", padx=20, pady=(16, 4)
        )

    def _build_register_tab(self, tab):
        ctk.CTkLabel(tab, text="", height=8).pack()
        self.reg_user = self._entry(tab, "Username")
        self.reg_pass = self._entry(tab, "Password", show="•")
        self.reg_key = self._entry(tab, "License Key")
        HUDButton(tab, text="▸  REGISTER", command=self._do_register).pack(
            fill="x", padx=20, pady=(16, 4)
        )

    def _build_license_tab(self, tab):
        ctk.CTkLabel(tab, text="", height=8).pack()
        self.lic_key = self._entry(tab, "License Key")
        HUDButton(tab, text="▸  ACTIVATE", command=self._do_license).pack(
            fill="x", padx=20, pady=(16, 4)
        )

    def _set_status(self, msg, color=TEXT_SECONDARY):
        self.status_label.configure(text=msg, text_color=color)

    def _do_login(self):
        self._set_status("Authenticating...", CYAN)
        threading.Thread(target=self._login_thread, daemon=True).start()

    def _login_thread(self):
        ok = self.keyauth.login(self.login_user.get(), self.login_pass.get())
        self.after(0, lambda: self._auth_result(ok))

    def _do_register(self):
        self._set_status("Registering...", CYAN)
        threading.Thread(target=self._register_thread, daemon=True).start()

    def _register_thread(self):
        ok = self.keyauth.register(
            self.reg_user.get(), self.reg_pass.get(), self.reg_key.get()
        )
        self.after(0, lambda: self._auth_result(ok))

    def _do_license(self):
        self._set_status("Validating license...", CYAN)
        threading.Thread(target=self._license_thread, daemon=True).start()

    def _license_thread(self):
        ok = self.keyauth.license_only(self.lic_key.get())
        self.after(0, lambda: self._auth_result(ok))

    def _auth_result(self, success):
        if success:
            self._set_status("Access granted!", GREEN)
            self.after(600, self._close_success)
        else:
            self._set_status(self.keyauth.response_message, RED)

    def _close_success(self):
        self.grab_release()
        self.destroy()
        self.on_success()


# ── Main Application ─────────────────────────────────────────────
class UndetectedApp(ctk.CTk):
    """Main HUD-style application window."""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("UNDETECTED — PC Tweaks")
        self.geometry("1100x720")
        self.minsize(960, 640)
        self.configure(fg_color=BG_DARK)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Try setting icon
        try:
            ico_path = os.path.join(ASSET_DIR, "icon.ico")
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
        except Exception:
            pass

        # KeyAuth
        self.keyauth = KeyAuth(
            name=APP_NAME,
            owner_id=OWNER_ID,
            secret=APP_SECRET,
            version=APP_VERSION,
        )

        # State
        self.tweak_state = load_tweaks_state()
        self.toggle_widgets: dict[str, HUDToggle] = {}
        self.authenticated = False
        self.current_category = "performance"

        # Build UI skeleton (hidden until auth)
        self._build_ui()

        # Start KeyAuth init + login flow
        self.after(300, self._init_keyauth)

    def _init_keyauth(self):
        """Initialize KeyAuth and show login window."""
        threading.Thread(target=self._keyauth_init_thread, daemon=True).start()

    def _keyauth_init_thread(self):
        self.keyauth.initialize()
        self.after(0, self._show_login)

    def _show_login(self):
        LoginWindow(self, self.keyauth, self._on_auth_success)

    def _on_auth_success(self):
        self.authenticated = True
        self._update_user_info()
        self.main_frame.pack(fill="both", expand=True)

    # ── UI Construction ──────────────────────────────────────────
    def _build_ui(self):
        # Main container (hidden until authenticated)
        self.main_frame = ctk.CTkFrame(self, fg_color=BG_DARK)

        # ── Top bar ──
        top_bar = ctk.CTkFrame(self.main_frame, fg_color=BG_PANEL, height=56, corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        # Logo text
        ctk.CTkLabel(
            top_bar, text="⟐  UNDETECTED", font=("Consolas", 18, "bold"), text_color=CYAN
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            top_bar, text="PC TWEAKS  v1.0", font=("Consolas", 11), text_color=TEXT_MUTED
        ).pack(side="left", padx=(0, 20))

        # User info (right side)
        self.user_info_label = ctk.CTkLabel(
            top_bar, text="Not logged in", font=("Consolas", 11), text_color=TEXT_SECONDARY
        )
        self.user_info_label.pack(side="right", padx=20)

        # HUD decorative line
        hud_line = ctk.CTkFrame(self.main_frame, fg_color=CYAN_DARK, height=1)
        hud_line.pack(fill="x")

        # ── Body: sidebar + content ──
        body = ctk.CTkFrame(self.main_frame, fg_color=BG_DARK)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(body, fg_color=BG_PANEL, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="─── CATEGORIES ───", font=("Consolas", 10), text_color=TEXT_MUTED
        ).pack(pady=(16, 8))

        self.cat_buttons: dict[str, ctk.CTkButton] = {}
        for cat_id, cat_info in TWEAK_CATEGORIES.items():
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {cat_info['icon']}  {cat_info['label']}",
                font=("Consolas", 13),
                fg_color="transparent",
                hover_color=BG_HOVER,
                text_color=TEXT_PRIMARY,
                anchor="w",
                height=40,
                corner_radius=4,
                command=lambda c=cat_id: self._switch_category(c),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.cat_buttons[cat_id] = btn

        # Bottom sidebar buttons
        spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        HUDButton(
            sidebar,
            text="⟳  Apply All",
            command=self._apply_all,
            fg_color=CYAN_DARK,
            text_color=BG_DARK,
            font=("Consolas", 12, "bold"),
        ).pack(fill="x", padx=12, pady=4)

        HUDButton(
            sidebar,
            text="↩  Revert All",
            command=self._revert_all,
            border_color=RED,
            text_color=RED,
            hover_color="#3A1020",
        ).pack(fill="x", padx=12, pady=(4, 8))

        # Sidebar accent line
        ctk.CTkFrame(body, fg_color=CYAN_DARK, width=1).grid(row=0, column=0, sticky="nse")

        # ── Content area ──
        self.content_frame = ctk.CTkFrame(body, fg_color=BG_DARK)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Category header
        self.cat_header = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=("Consolas", 20, "bold"),
            text_color=CYAN,
            anchor="w",
        )
        self.cat_header.grid(row=0, column=0, sticky="w", padx=24, pady=(20, 4))

        self.cat_desc = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=("Consolas", 12),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.cat_desc.grid(row=0, column=0, sticky="sw", padx=24, pady=(48, 12))

        # Scrollable tweak list
        self.tweak_scroll = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=BG_DARK,
            scrollbar_button_color=CYAN_DARK,
            scrollbar_button_hover_color=CYAN,
        )
        self.tweak_scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        self.tweak_scroll.grid_columnconfigure(0, weight=1)

        # Status bar
        self.status_bar = ctk.CTkFrame(self.main_frame, fg_color=BG_PANEL, height=32, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)

        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="◉  SYSTEM READY",
            font=("Consolas", 10),
            text_color=GREEN,
        )
        self.status_text.pack(side="left", padx=16)

        self.tweak_count_label = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=("Consolas", 10),
            text_color=TEXT_MUTED,
        )
        self.tweak_count_label.pack(side="right", padx=16)

        # Default category
        self._switch_category("performance")

    # ── Category switching ───────────────────────────────────────
    def _switch_category(self, cat_id: str):
        self.current_category = cat_id
        cat = TWEAK_CATEGORIES[cat_id]

        # Update header
        self.cat_header.configure(text=f"{cat['icon']}  {cat['label']}")
        self.cat_desc.configure(text=cat["description"])

        # Highlight sidebar
        for cid, btn in self.cat_buttons.items():
            if cid == cat_id:
                btn.configure(fg_color=CYAN_DARK, text_color=BG_DARK)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY)

        # Rebuild tweak list
        for widget in self.tweak_scroll.winfo_children():
            widget.destroy()

        self.tweak_state = load_tweaks_state()
        tweaks = get_tweaks_by_category(cat_id)

        for i, tweak in enumerate(tweaks):
            is_on = self.tweak_state.get(tweak["id"], False)
            toggle = HUDToggle(
                self.tweak_scroll,
                tweak=tweak,
                is_applied=is_on,
                on_toggle=self._on_tweak_toggle,
            )
            toggle.grid(row=i, column=0, sticky="ew", padx=4, pady=4)
            self.toggle_widgets[tweak["id"]] = toggle

        self._update_tweak_count()

    # ── Tweak operations ─────────────────────────────────────────
    def _on_tweak_toggle(self, tweak: dict, enabled: bool, widget: HUDToggle):
        """Handle a tweak toggle switch."""
        self._set_status(f"{'Applying' if enabled else 'Reverting'}: {tweak['name']}...", CYAN)

        def worker():
            if enabled:
                ok, msg = apply_tweak(tweak)
            else:
                ok, msg = revert_tweak(tweak)
            self.after(0, lambda: self._tweak_done(tweak, enabled, ok, msg, widget))

        threading.Thread(target=worker, daemon=True).start()

    def _tweak_done(self, tweak, enabled, ok, msg, widget: HUDToggle):
        if ok:
            widget.set_status(enabled)
            self._set_status(
                f"{'Applied' if enabled else 'Reverted'}: {tweak['name']}", GREEN
            )
        else:
            widget.switch_var.set(not enabled)
            widget.set_status(False, "FAIL")
            self._set_status(f"Failed: {msg}", RED)
        self._update_tweak_count()

    def _apply_all(self):
        """Apply all tweaks in the current category."""
        tweaks = get_tweaks_by_category(self.current_category)
        self._set_status(f"Applying all {TWEAK_CATEGORIES[self.current_category]['label']} tweaks...", CYAN)

        def worker():
            for t in tweaks:
                ok, _ = apply_tweak(t)
            self.after(0, lambda: self._switch_category(self.current_category))
            self.after(0, lambda: self._set_status("All tweaks applied!", GREEN))

        threading.Thread(target=worker, daemon=True).start()

    def _revert_all(self):
        """Revert all tweaks in the current category."""
        tweaks = get_tweaks_by_category(self.current_category)
        self._set_status(f"Reverting all {TWEAK_CATEGORIES[self.current_category]['label']} tweaks...", CYAN)

        def worker():
            for t in tweaks:
                revert_tweak(t)
            self.after(0, lambda: self._switch_category(self.current_category))
            self.after(0, lambda: self._set_status("All tweaks reverted.", YELLOW))

        threading.Thread(target=worker, daemon=True).start()

    # ── Status helpers ───────────────────────────────────────────
    def _set_status(self, msg: str, color: str = TEXT_SECONDARY):
        self.status_text.configure(text=f"◉  {msg}", text_color=color)

    def _update_tweak_count(self):
        self.tweak_state = load_tweaks_state()
        active = sum(1 for v in self.tweak_state.values() if v)
        total = len(ALL_TWEAKS)
        self.tweak_count_label.configure(text=f"Active: {active}/{total}")

    def _update_user_info(self):
        info = self.keyauth.get_subscription_info()
        self.user_info_label.configure(text=info)


def main():
    app = UndetectedApp()
    app.mainloop()


if __name__ == "__main__":
    main()
