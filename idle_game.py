import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import os
from datetime import datetime
import threading
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

class IdleMiningGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Idle Mining Empire")
        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        self.root.resizable(True, True)
        
        self.gold = 0
        self.gold_per_click = 1
        self.gold_per_second = 0
        self.last_save_time = time.time()
        
        self.volume = 0.5
        self.muted = False
        
        self.buildings = {
            "Pickaxe": {"count": 0, "cost": 10, "gps": 0.1, "cost_multiplier": 1.15},
            "Miner": {"count": 0, "cost": 100, "gps": 1, "cost_multiplier": 1.15},
            "Drill": {"count": 0, "cost": 1000, "gps": 8, "cost_multiplier": 1.15},
            "Mine Shaft": {"count": 0, "cost": 12000, "gps": 47, "cost_multiplier": 1.15},
            "Excavator": {"count": 0, "cost": 130000, "gps": 260, "cost_multiplier": 1.15},
            "Quarry": {"count": 0, "cost": 1400000, "gps": 1400, "cost_multiplier": 1.15},
            "Gold Factory": {"count": 0, "cost": 20000000, "gps": 7800, "cost_multiplier": 1.15},
            "Gem Mine": {"count": 0, "cost": 330000000, "gps": 44000, "cost_multiplier": 1.15},
            "Crystal Cavern": {"count": 0, "cost": 5100000000, "gps": 260000, "cost_multiplier": 1.15},
            "Diamond Forge": {"count": 0, "cost": 75000000000, "gps": 1600000, "cost_multiplier": 1.15},
        }
        
        self.upgrades = {
            "Better Tools": {"purchased": False, "cost": 100, "effect": "click", "multiplier": 2},
            "Sharp Pickaxe": {"purchased": False, "cost": 500, "effect": "click", "multiplier": 2},
            "Efficiency I": {"purchased": False, "cost": 1000, "effect": "gps", "multiplier": 2},
            "Golden Touch": {"purchased": False, "cost": 2500, "effect": "click", "multiplier": 3},
            "Efficiency II": {"purchased": False, "cost": 10000, "effect": "gps", "multiplier": 2},
            "Master Miner": {"purchased": False, "cost": 50000, "effect": "click", "multiplier": 5},
            "Automation I": {"purchased": False, "cost": 100000, "effect": "gps", "multiplier": 2},
            "Diamond Gloves": {"purchased": False, "cost": 250000, "effect": "click", "multiplier": 4},
            "Efficiency III": {"purchased": False, "cost": 500000, "effect": "gps", "multiplier": 3},
            "Mining Mastery": {"purchased": False, "cost": 1000000, "effect": "click", "multiplier": 10},
            "Automation II": {"purchased": False, "cost": 2500000, "effect": "gps", "multiplier": 2},
            "Fortune Finder": {"purchased": False, "cost": 5000000, "effect": "gold", "multiplier": 1.5},
            "Mega Click": {"purchased": False, "cost": 10000000, "effect": "click", "multiplier": 15},
            "Efficiency IV": {"purchased": False, "cost": 25000000, "effect": "gps", "multiplier": 3},
            "Legendary Hammer": {"purchased": False, "cost": 50000000, "effect": "click", "multiplier": 20},
            "Automation III": {"purchased": False, "cost": 100000000, "effect": "gps", "multiplier": 2},
            "Gold Rush I": {"purchased": False, "cost": 250000000, "effect": "gold", "multiplier": 2},
            "Ultra Mining": {"purchased": False, "cost": 500000000, "effect": "click", "multiplier": 25},
            "Efficiency V": {"purchased": False, "cost": 1000000000, "effect": "gps", "multiplier": 4},
            "Titan's Strength": {"purchased": False, "cost": 2500000000, "effect": "click", "multiplier": 50},
            "Automation IV": {"purchased": False, "cost": 5000000000, "effect": "gps", "multiplier": 3},
            "Gold Rush II": {"purchased": False, "cost": 10000000000, "effect": "gold", "multiplier": 2},
            "Divine Pickaxe": {"purchased": False, "cost": 25000000000, "effect": "click", "multiplier": 100},
            "Efficiency VI": {"purchased": False, "cost": 50000000000, "effect": "gps", "multiplier": 5},
            "Ancient Power": {"purchased": False, "cost": 100000000000, "effect": "click", "multiplier": 200},
            "Automation V": {"purchased": False, "cost": 250000000000, "effect": "gps", "multiplier": 4},
            "Midas Touch": {"purchased": False, "cost": 500000000000, "effect": "gold", "multiplier": 3},
            "Godly Strike": {"purchased": False, "cost": 1000000000000, "effect": "click", "multiplier": 500},
            "Efficiency VII": {"purchased": False, "cost": 2500000000000, "effect": "gps", "multiplier": 6},
            "Cosmic Hammer": {"purchased": False, "cost": 5000000000000, "effect": "click", "multiplier": 1000},
            "Automation VI": {"purchased": False, "cost": 10000000000000, "effect": "gps", "multiplier": 5},
            "Gold Magnet": {"purchased": False, "cost": 25000000000000, "effect": "gold", "multiplier": 4},
            "Celestial Mining": {"purchased": False, "cost": 50000000000000, "effect": "click", "multiplier": 2000},
            "Efficiency VIII": {"purchased": False, "cost": 100000000000000, "effect": "gps", "multiplier": 7},
            "Infinity Tools": {"purchased": False, "cost": 250000000000000, "effect": "click", "multiplier": 5000},
            "Automation VII": {"purchased": False, "cost": 500000000000000, "effect": "gps", "multiplier": 6},
            "Golden Aura": {"purchased": False, "cost": 1000000000000000, "effect": "gold", "multiplier": 5},
            "Omnipotent Strike": {"purchased": False, "cost": 2500000000000000, "effect": "click", "multiplier": 10000},
            "Efficiency IX": {"purchased": False, "cost": 5000000000000000, "effect": "gps", "multiplier": 8},
            "Universal Mining": {"purchased": False, "cost": 10000000000000000, "effect": "click", "multiplier": 25000},
            "Automation VIII": {"purchased": False, "cost": 25000000000000000, "effect": "gps", "multiplier": 7},
            "Supreme Fortune": {"purchased": False, "cost": 50000000000000000, "effect": "gold", "multiplier": 6},
            "Reality Breaker": {"purchased": False, "cost": 100000000000000000, "effect": "click", "multiplier": 50000},
            "Efficiency X": {"purchased": False, "cost": 250000000000000000, "effect": "gps", "multiplier": 10},
            "Transcendent Power": {"purchased": False, "cost": 500000000000000000, "effect": "click", "multiplier": 100000},
            "Automation IX": {"purchased": False, "cost": 1000000000000000000, "effect": "gps", "multiplier": 8},
            "Eternal Gold": {"purchased": False, "cost": 2500000000000000000, "effect": "gold", "multiplier": 8},
            "Absolute Dominion": {"purchased": False, "cost": 5000000000000000000, "effect": "click", "multiplier": 250000},
            "Final Efficiency": {"purchased": False, "cost": 10000000000000000000, "effect": "gps", "multiplier": 12},
        }
        
        self.save_file = "idle_game_save.json"
        
        self.setup_ui()
        self.load_game()
        self.update_game()
        
    def setup_ui(self):
        self.root.configure(bg="#0d1117")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        main_frame = tk.Frame(self.root, bg="#0d1117")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=2)

        left_frame = tk.Frame(main_frame, bg="#0d1117")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 12), pady=20)
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)

        right_frame = tk.Frame(main_frame, bg="#0d1117")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(12, 20), pady=20)
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        top_frame = tk.Frame(left_frame, bg="#161b22", relief=tk.FLAT, bd=0)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        top_frame.columnconfigure(0, weight=1)

        gold_icon_frame = tk.Frame(top_frame, bg="#161b22")
        gold_icon_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        
        gold_icon = tk.Label(
            gold_icon_frame,
            text="💰",
            font=("Segoe UI", 36),
            bg="#161b22",
            fg="#f0c674",
        )
        gold_icon.pack(side=tk.LEFT, padx=(0, 12))
        
        self.gold_label = tk.Label(
            gold_icon_frame,
            text="Gold: 0",
            font=("Segoe UI", 32, "bold"),
            bg="#161b22",
            fg="#f0c674",
        )
        self.gold_label.pack(side=tk.LEFT)

        gps_icon_frame = tk.Frame(top_frame, bg="#161b22")
        gps_icon_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 20))
        
        gps_icon = tk.Label(
            gps_icon_frame,
            text="⚡",
            font=("Segoe UI", 20),
            bg="#161b22",
            fg="#ffd700",
        )
        gps_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        self.gps_label = tk.Label(
            gps_icon_frame,
            text="Gold per second: 0.0",
            font=("Segoe UI", 15),
            bg="#161b22",
            fg="#b5b5b5",
        )
        self.gps_label.pack(side=tk.LEFT)

        center_frame = tk.Frame(left_frame, bg="#0d1117")
        center_frame.grid(row=1, column=0, sticky="nsew")
        center_frame.rowconfigure(0, weight=1)
        center_frame.columnconfigure(0, weight=1)

        mine_card = tk.Frame(center_frame, bg="#161b22", relief=tk.FLAT, bd=0)
        mine_card.grid(row=0, column=0, sticky="n", padx=0, pady=20, ipadx=20, ipady=20)
        mine_card.columnconfigure(0, weight=1)
        
        border_frame = tk.Frame(mine_card, bg="#238636", height=3)
        border_frame.pack(fill=tk.X, padx=0, pady=0)

        self.mine_button = tk.Button(
            mine_card,
            text="⛏️ MINE ⛏️",
            font=("Segoe UI", 30, "bold"),
            command=self.click_mine,
            bg="#238636",
            fg="white",
            activebackground="#2ea043",
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=40,
            pady=20,
            cursor="hand2",
        )
        self.mine_button.pack(padx=24, pady=24)

        control_frame = tk.Frame(left_frame, bg="#0d1117")
        control_frame.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        control_frame.columnconfigure(0, weight=1)

        reset_button = tk.Button(
            control_frame,
            text="🔄 Reset",
            command=self.reset_game,
            bg="#da3633",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=18,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#f85149",
            activeforeground="white",
        )
        reset_button.grid(row=0, column=0, sticky="w")
        
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook", background="#0d1117", borderwidth=0)
        style.configure("TNotebook.Tab", 
                       background="#161b22", 
                       foreground="#c9d1d9",
                       padding=(16, 10),
                       font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                 background=[("selected", "#238636")],
                 foreground=[("selected", "white")],
                 padding=[("selected", [16, 10]), ("!selected", [16, 10])])
        
        style.configure("TScrollbar",
                       background="#21262d",
                       troughcolor="#0d1117",
                       borderwidth=0,
                       arrowcolor="#8b949e",
                       darkcolor="#21262d",
                       lightcolor="#21262d")
        style.map("TScrollbar",
                 background=[("active", "#30363d")])

        notebook = ttk.Notebook(right_frame)
        notebook.grid(row=0, column=0, sticky="nsew")
        
        buildings_frame = tk.Frame(notebook, bg="#0d1117")
        notebook.add(buildings_frame, text="Buildings")
        
        canvas = tk.Canvas(buildings_frame, bg="#0d1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(buildings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0d1117")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        buildings_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _sync_buildings_width(e):
            canvas.itemconfigure(buildings_window, width=e.width)
        canvas.bind("<Configure>", _sync_buildings_width)
        
        building_icons = {
            "Pickaxe": "⛏️",
            "Miner": "👷",
            "Drill": "🔩",
            "Mine Shaft": "🕳️",
            "Excavator": "🚜",
            "Quarry": "⛰️",
            "Gold Factory": "🏭",
            "Gem Mine": "💎",
            "Crystal Cavern": "✨",
            "Diamond Forge": "🔥"
        }
        
        self.building_buttons = {}
        for name, data in self.buildings.items():
            container = tk.Frame(scrollable_frame, bg="#0d1117")
            container.pack(fill=tk.X, padx=8, pady=6)
            
            accent_colors = ["#238636", "#1f6feb", "#da3633", "#f85149", "#a5a5a5", 
                           "#f0c674", "#58a6ff", "#f0883e", "#bc8cff", "#ff7b72"]
            color_index = list(self.buildings.keys()).index(name) % len(accent_colors)
            accent_bar = tk.Frame(container, bg=accent_colors[color_index], width=4)
            accent_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0))
            
            frame = tk.Frame(container, bg="#161b22", relief=tk.FLAT, bd=0)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            frame.columnconfigure(0, weight=2)
            frame.columnconfigure(1, weight=2)
            frame.columnconfigure(2, weight=0)

            icon_text = building_icons.get(name, "🏗️")
            icon_label = tk.Label(
                frame,
                text=icon_text,
                font=("Segoe UI", 16),
                bg="#161b22",
                fg=accent_colors[color_index],
                anchor="w",
            )
            icon_label.grid(row=0, column=0, sticky="w", padx=(16, 8), pady=(12, 4))
            
            info_label = tk.Label(
                frame,
                text=f"{name} (0)",
                font=("Segoe UI", 12, "bold"),
                bg="#161b22",
                fg="#c9d1d9",
                anchor="w",
            )
            info_label.grid(row=0, column=0, sticky="w", padx=(48, 10), pady=(12, 4))

            stats_label = tk.Label(
                frame,
                text=f"+{self.format_number(data['gps'])} gold/sec",
                font=("Segoe UI", 10),
                bg="#161b22",
                fg="#8b949e",
                anchor="w",
            )
            stats_label.grid(row=0, column=1, sticky="w", padx=10, pady=(12, 4))
            
            gps_tally_label = tk.Label(
                frame,
                text="",
                font=("Segoe UI", 9),
                bg="#161b22",
                fg="#3fb950",
                anchor="w",
            )
            gps_tally_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=(16, 10), pady=(0, 8))

            buy_button = tk.Button(
                frame,
                text=f"Buy: {self.format_number(data['cost'])}",
                command=lambda n=name: self.buy_building(n),
                bg="#238636",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                padx=14,
                pady=8,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                activebackground="#2ea043",
                activeforeground="white",
            )
            buy_button.grid(row=0, column=2, rowspan=2, sticky="ne", padx=(10, 16), pady=10)
            
            self.building_buttons[name] = {
                "info": info_label,
                "button": buy_button,
                "stats": stats_label,
                "gps_tally": gps_tally_label,
                "frame": frame,
                "container": container,
                "accent": accent_bar
            }
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        upgrades_frame = tk.Frame(notebook, bg="#0d1117")
        notebook.add(upgrades_frame, text="Upgrades")
        
        canvas2 = tk.Canvas(upgrades_frame, bg="#0d1117", highlightthickness=0)
        scrollbar2 = ttk.Scrollbar(upgrades_frame, orient="vertical", command=canvas2.yview)
        scrollable_upgrades = tk.Frame(canvas2, bg="#0d1117")
        
        scrollable_upgrades.bind(
            "<Configure>",
            lambda e: canvas2.configure(scrollregion=canvas2.bbox("all"))
        )
        
        upgrades_window = canvas2.create_window((0, 0), window=scrollable_upgrades, anchor="nw")
        canvas2.configure(yscrollcommand=scrollbar2.set)

        def _sync_upgrades_width(e):
            canvas2.itemconfigure(upgrades_window, width=e.width)
        canvas2.bind("<Configure>", _sync_upgrades_width)
        
        upgrade_icons = {
            "click": "⚡",
            "gps": "📈",
            "gold": "💎"
        }
        
        self.upgrade_buttons = {}
        for name, data in self.upgrades.items():
            container = tk.Frame(scrollable_upgrades, bg="#0d1117")
            container.pack(fill=tk.X, padx=8, pady=6)
            
            effect_type = data['effect']
            effect_colors = {
                "click": "#f0c674",
                "gps": "#58a6ff",
                "gold": "#f0883e"
            }
            accent_color = effect_colors.get(effect_type, "#8b949e")
            
            accent_bar = tk.Frame(container, bg=accent_color, width=4)
            accent_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0))
            
            frame = tk.Frame(container, bg="#161b22", relief=tk.FLAT, bd=0)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            frame.columnconfigure(0, weight=2)
            frame.columnconfigure(1, weight=2)
            frame.columnconfigure(2, weight=0)

            icon_text = upgrade_icons.get(effect_type, "✨")
            icon_label = tk.Label(
                frame,
                text=icon_text,
                font=("Segoe UI", 14),
                bg="#161b22",
                fg=accent_color,
                anchor="w",
            )
            icon_label.grid(row=0, column=0, sticky="w", padx=(16, 8), pady=12)
            
            info_label = tk.Label(
                frame,
                text=name,
                font=("Segoe UI", 11, "bold"),
                bg="#161b22",
                fg="#c9d1d9",
                anchor="w",
            )
            info_label.grid(row=0, column=0, sticky="w", padx=(44, 10), pady=12)

            effect_map = {"click": "clicking power", "gps": "production", "gold": "all gold"}
            effect_text = f"x{data['multiplier']} {effect_map[data['effect']]}"
            effect_label = tk.Label(
                frame,
                text=effect_text,
                font=("Segoe UI", 9),
                bg="#161b22",
                fg="#8b949e",
                anchor="w",
            )
            effect_label.grid(row=0, column=1, sticky="w", padx=10, pady=12)

            buy_button = tk.Button(
                frame,
                text=f"Buy: {self.format_number(data['cost'])}",
                command=lambda n=name: self.buy_upgrade(n),
                bg="#1f6feb",
                fg="white",
                font=("Segoe UI", 9, "bold"),
                padx=14,
                pady=8,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                activebackground="#388bfd",
                activeforeground="white",
            )
            buy_button.grid(row=0, column=2, sticky="e", padx=(10, 16), pady=10)
            
            self.upgrade_buttons[name] = {
                "button": buy_button,
                "frame": frame,
                "info": info_label,
                "effect": effect_label,
                "container": container,
                "accent": accent_bar
            }
        
        canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Settings tab
        settings_frame = tk.Frame(notebook, bg="#0d1117")
        notebook.add(settings_frame, text="⚙️ Settings")
        
        settings_canvas = tk.Canvas(settings_frame, bg="#0d1117", highlightthickness=0)
        settings_scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=settings_canvas.yview)
        settings_scrollable = tk.Frame(settings_canvas, bg="#0d1117")
        
        settings_scrollable.bind(
            "<Configure>",
            lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))
        )
        
        settings_window = settings_canvas.create_window((0, 0), window=settings_scrollable, anchor="nw")
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        
        def _sync_settings_width(e):
            settings_canvas.itemconfigure(settings_window, width=e.width)
        settings_canvas.bind("<Configure>", _sync_settings_width)
        
        title_label = tk.Label(
            settings_scrollable,
            text="⚙️ Settings",
            font=("Segoe UI", 22, "bold"),
            bg="#0d1117",
            fg="#c9d1d9"
        )
        title_label.pack(pady=24)
        
        volume_frame = tk.Frame(settings_scrollable, bg="#161b22", relief=tk.FLAT, bd=0)
        volume_frame.pack(fill=tk.X, padx=20, pady=12)
        
        volume_label = tk.Label(
            volume_frame,
            text="Volume",
            font=("Segoe UI", 13, "bold"),
            bg="#161b22",
            fg="#c9d1d9"
        )
        volume_label.pack(anchor="w", padx=16, pady=(16, 8))
        
        volume_slider_frame = tk.Frame(volume_frame, bg="#161b22")
        volume_slider_frame.pack(fill=tk.X, padx=16, pady=(0, 16))
        
        self.volume_var = tk.DoubleVar(value=self.volume)
        self.volume_slider = tk.Scale(
            volume_slider_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self.update_volume,
            bg="#21262d",
            fg="#c9d1d9",
            troughcolor="#30363d",
            highlightthickness=0,
            length=300,
            sliderrelief=tk.FLAT,
            borderwidth=0
        )
        self.volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.mute_var = tk.BooleanVar(value=self.muted)
        mute_button = tk.Checkbutton(
            volume_slider_frame,
            text="Mute",
            variable=self.mute_var,
            command=self.toggle_mute,
            bg="#161b22",
            fg="#c9d1d9",
            selectcolor="#21262d",
            activebackground="#161b22",
            activeforeground="#c9d1d9",
            font=("Segoe UI", 10),
            relief=tk.FLAT
        )
        mute_button.pack(side=tk.LEFT, padx=(16, 0))
        
        separator = tk.Frame(settings_scrollable, bg="#21262d", height=1)
        separator.pack(fill=tk.X, padx=20, pady=16)
        
        controls_frame = tk.Frame(settings_scrollable, bg="#161b22", relief=tk.FLAT, bd=0)
        controls_frame.pack(fill=tk.X, padx=20, pady=12)
        
        controls_label = tk.Label(
            controls_frame,
            text="Game Controls",
            font=("Segoe UI", 13, "bold"),
            bg="#161b22",
            fg="#c9d1d9"
        )
        controls_label.pack(anchor="w", padx=16, pady=(16, 12))
        
        save_settings_button = tk.Button(
            controls_frame,
            text="💾 Save Game",
            command=self.save_game,
            bg="#1f6feb",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#388bfd",
            activeforeground="white"
        )
        save_settings_button.pack(fill=tk.X, padx=16, pady=(0, 8))
        
        delete_button = tk.Button(
            controls_frame,
            text="🗑️ Delete Data",
            command=self.delete_data,
            bg="#da3633",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#f85149",
            activeforeground="white"
        )
        delete_button.pack(fill=tk.X, padx=16, pady=(0, 16))
        
        settings_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        settings_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def play_click_sound(self):
        if self.muted or self.volume <= 0:
            return
        
        def _play():
            try:
                if HAS_WINSOUND:
                    frequency = 800
                    duration_ms = 50
                    winsound.Beep(frequency, duration_ms)
                elif HAS_PYGAME and HAS_NUMPY:
                    duration = 0.1
                    frequency = 800
                    sample_rate = 44100
                    t = np.linspace(0, duration, int(sample_rate * duration))
                    wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 10) * self.volume
                    wave = (wave * 32767).astype(np.int16)
                    sound_array = np.array([wave, wave])
                    sound = pygame.sndarray.make_sound(sound_array.T)
                    sound.set_volume(min(self.volume, 1.0))
                    sound.play()
            except Exception:
                pass
        
        threading.Thread(target=_play, daemon=True).start()
    
    def click_mine(self):
        self.play_click_sound()
        
        gold_multiplier = 1
        for upgrade in self.upgrades.values():
            if upgrade["purchased"] and upgrade["effect"] == "gold":
                gold_multiplier *= upgrade["multiplier"]
        
        self.gold += self.gold_per_click * gold_multiplier
        self.update_display()
        
    def buy_building(self, name):
        building = self.buildings[name]
        cost = int(building["cost"])
        
        if self.gold >= cost:
            self.gold -= cost
            building["count"] += 1
            building["cost"] = building["cost"] * building["cost_multiplier"]
            self.calculate_gps()
            self.update_display()
        
    def buy_upgrade(self, name):
        upgrade = self.upgrades[name]
        
        if not upgrade["purchased"] and self.gold >= upgrade["cost"]:
            self.gold -= upgrade["cost"]
            upgrade["purchased"] = True
            
            if upgrade["effect"] == "click":
                self.gold_per_click *= upgrade["multiplier"]
            elif upgrade["effect"] == "gps":
                self.calculate_gps()
            
            self.update_display()
    
    def calculate_gps(self):
        base_gps = sum(data["count"] * data["gps"] for data in self.buildings.values())
        
        gps_multiplier = 1
        for upgrade in self.upgrades.values():
            if upgrade["purchased"] and upgrade["effect"] == "gps":
                gps_multiplier *= upgrade["multiplier"]
        
        gold_multiplier = 1
        for upgrade in self.upgrades.values():
            if upgrade["purchased"] and upgrade["effect"] == "gold":
                gold_multiplier *= upgrade["multiplier"]
        
        self.gold_per_second = base_gps * gps_multiplier * gold_multiplier
    
    def update_game(self):
        current_time = time.time()
        time_passed = current_time - self.last_save_time
        self.gold += self.gold_per_second * time_passed
        self.last_save_time = current_time
        
        self.update_display()
        
        self.root.after(100, self.update_game)
    
    def calculate_building_gps(self, building_name):
        building = self.buildings[building_name]
        if building["count"] == 0:
            return 0
        
        base_gps = building["count"] * building["gps"]
        
        gps_multiplier = 1
        for upgrade in self.upgrades.values():
            if upgrade["purchased"] and upgrade["effect"] == "gps":
                gps_multiplier *= upgrade["multiplier"]
        
        gold_multiplier = 1
        for upgrade in self.upgrades.values():
            if upgrade["purchased"] and upgrade["effect"] == "gold":
                gold_multiplier *= upgrade["multiplier"]
        
        return base_gps * gps_multiplier * gold_multiplier
    
    def update_display(self):
        self.gold_label.config(text=f"Gold: {self.format_number(self.gold)}")
        self.gps_label.config(text=f"Gold per second: {self.format_number(self.gold_per_second)}")
        
        if hasattr(self, 'volume_var'):
            self.volume_var.set(self.volume)
        if hasattr(self, 'mute_var'):
            self.mute_var.set(self.muted)
        
        for name, elements in self.building_buttons.items():
            building = self.buildings[name]
            cost = int(building["cost"])
            count = building["count"]
            
            elements["info"].config(text=f"{name} ({count})")
            elements["button"].config(text=f"Buy: {self.format_number(cost)} gold")
            
            if count > 0:
                building_gps = self.calculate_building_gps(name)
                elements["gps_tally"].config(
                    text=f"Total: {self.format_number(building_gps)} gold/sec",
                    fg="#3fb950"
                )
                elements["gps_tally"].grid(row=1, column=0, columnspan=2, sticky="w", padx=(16, 10), pady=(0, 8))
            else:
                elements["gps_tally"].config(text="")
                elements["gps_tally"].grid_remove()
            
            if self.gold >= cost:
                elements["button"].config(state=tk.NORMAL, bg="#238636", cursor="hand2")
            else:
                elements["button"].config(state=tk.DISABLED, bg="#21262d", cursor="")
        
        for name, elements in self.upgrade_buttons.items():
            upgrade = self.upgrades[name]
            
            if upgrade["purchased"]:
                elements["button"].config(text="✓ PURCHASED", state=tk.DISABLED, bg="#238636", fg="white", cursor="")
                elements["frame"].config(bg="#1a472a")
                elements["info"].config(bg="#1a472a", fg="#3fb950")
                elements["effect"].config(bg="#1a472a", fg="#3fb950")
                if "accent" in elements:
                    elements["accent"].config(bg="#3fb950")
            elif self.gold >= upgrade["cost"]:
                elements["button"].config(state=tk.NORMAL, bg="#1f6feb", cursor="hand2")
                elements["frame"].config(bg="#161b22")
                elements["info"].config(bg="#161b22", fg="#c9d1d9")
                elements["effect"].config(bg="#161b22", fg="#8b949e")
            else:
                elements["button"].config(state=tk.DISABLED, bg="#21262d", cursor="")
                elements["frame"].config(bg="#161b22")
                elements["info"].config(bg="#161b22", fg="#c9d1d9")
                elements["effect"].config(bg="#161b22", fg="#8b949e")
    
    def format_number(self, num):
        if num < 1000:
            return f"{int(num)}"
        elif num < 1000000:
            return f"{num/1000:.1f}K"
        elif num < 1000000000:
            return f"{num/1000000:.1f}M"
        elif num < 1000000000000:
            return f"{num/1000000000:.1f}B"
        elif num < 1000000000000000:
            return f"{num/1000000000000:.1f}T"
        elif num < 1000000000000000000:
            return f"{num/1000000000000000:.1f}Q"
        else:
            return f"{num/1000000000000000000:.1f}Qi"
    
    def save_game(self):
        save_data = {
            "gold": self.gold,
            "gold_per_click": self.gold_per_click,
            "buildings": self.buildings,
            "upgrades": self.upgrades,
            "timestamp": time.time(),
            "volume": self.volume,
            "muted": self.muted
        }
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f)
            messagebox.showinfo("Save", "Game saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save game: {e}")
    
    def load_game(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    save_data = json.load(f)
                
                self.gold = save_data.get("gold", 0)
                self.gold_per_click = save_data.get("gold_per_click", 1)
                self.buildings = save_data.get("buildings", self.buildings)
                self.upgrades = save_data.get("upgrades", self.upgrades)
                self.volume = save_data.get("volume", 0.5)
                self.muted = save_data.get("muted", False)
                
                saved_time = save_data.get("timestamp", time.time())
                offline_time = time.time() - saved_time
                
                self.calculate_gps()
                offline_gold = self.gold_per_second * offline_time
                
                if offline_gold > 0:
                    self.gold += offline_gold
                    messagebox.showinfo("Welcome Back!", 
                                      f"You were offline for {int(offline_time)} seconds.\n"
                                      f"You earned {self.format_number(offline_gold)} gold!")
                
                self.last_save_time = time.time()
                self.update_display()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load game: {e}")
    
    def reset_game(self):
        if messagebox.askyesno("Reset Game", "Are you sure you want to reset? All progress will be lost!"):
            self.gold = 0
            self.gold_per_click = 1
            self.gold_per_second = 0
            
            for building in self.buildings.values():
                original_cost = building["cost"] / (building["cost_multiplier"] ** building["count"])
                building["count"] = 0
                building["cost"] = original_cost
            
            for upgrade in self.upgrades.values():
                upgrade["purchased"] = False
            
            if os.path.exists(self.save_file):
                os.remove(self.save_file)
            
            self.calculate_gps()
            self.update_display()
    
    
    def update_volume(self, value):
        self.volume = float(value)
        if self.muted:
            self.muted = False
            self.mute_var.set(False)
    
    def toggle_mute(self):
        self.muted = self.mute_var.get()
    
    def delete_data(self):
        if messagebox.askyesno(
            "Delete Data",
            "Are you absolutely sure you want to delete all game data?\n\n"
            "This will permanently delete your save file and cannot be undone!"
        ):
            if messagebox.askyesno(
                "Final Confirmation",
                "This is your last chance!\n\n"
                "Are you REALLY sure you want to delete everything?"
            ):
                try:
                    if os.path.exists(self.save_file):
                        os.remove(self.save_file)
                    
                    self.gold = 0
                    self.gold_per_click = 1
                    self.gold_per_second = 0
                    
                    for building in self.buildings.values():
                        original_cost = building["cost"] / (building["cost_multiplier"] ** building["count"])
                        building["count"] = 0
                        building["cost"] = original_cost
                    
                    for upgrade in self.upgrades.values():
                        upgrade["purchased"] = False
                    
                    self.calculate_gps()
                    self.update_display()
                    
                    messagebox.showinfo("Success", "All game data has been deleted.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    game = IdleMiningGame(root)
    root.mainloop()
