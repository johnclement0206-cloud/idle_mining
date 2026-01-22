import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import os
from datetime import datetime
import threading
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

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
        self.total_clicks = 0
        
        self.volume = 0.5
        self.muted = False
        self.save_notification_id = None
        self.tooltip = None
        self.auto_save_enabled = False
        self.auto_save_interval = 15
        self.auto_save_task_id = None
        
        self.buildings = {
            "Pickaxe": {"count": 0, "cost": 10, "gps": 1, "cost_multiplier": 1.15},
            "Miner": {"count": 0, "cost": 100, "gps": 10, "cost_multiplier": 1.15},
            "Drill": {"count": 0, "cost": 1200, "gps": 120, "cost_multiplier": 1.15},
            "Mineshaft": {"count": 0, "cost": 15000, "gps": 1300, "cost_multiplier": 1.15},
            "Excavator": {"count": 0, "cost": 200000, "gps": 11000, "cost_multiplier": 1.15},
            "Quarry": {"count": 0, "cost": 2500000, "gps": 85000, "cost_multiplier": 1.15},
            "Gold Factory": {"count": 0, "cost": 35000000, "gps": 600000, "cost_multiplier": 1.15},
            "Gem Mine": {"count": 0, "cost": 550000000, "gps": 4300000, "cost_multiplier": 1.15},
            "Crystal Cavern": {"count": 0, "cost": 8000000000, "gps": 32000000, "cost_multiplier": 1.15},
            "Diamond Forge": {"count": 0, "cost": 120000000000, "gps": 240000000, "cost_multiplier": 1.15},
            "Mythril Deep": {"count": 0, "cost": 1800000000000, "gps": 1800000000, "cost_multiplier": 1.15},
            "Ethereal Vault": {"count": 0, "cost": 27000000000000, "gps": 13000000000, "cost_multiplier": 1.15},
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
            "Mythril Mastery": {"purchased": False, "cost": 25000000000000000000, "effect": "click", "multiplier": 500000},
            "Automation X": {"purchased": False, "cost": 50000000000000000000, "effect": "gps", "multiplier": 10},
            "Ethereal Fortune": {"purchased": False, "cost": 100000000000000000000, "effect": "gold", "multiplier": 10},
            "Quantum Strike": {"purchased": False, "cost": 250000000000000000000, "effect": "click", "multiplier": 1000000},
            "Hyperspace Efficiency": {"purchased": False, "cost": 500000000000000000000, "effect": "gps", "multiplier": 15},
            "Infinity Aura": {"purchased": False, "cost": 1000000000000000000000, "effect": "gold", "multiplier": 15},
        }
        
        self.achievements = {
            "First Click": {"unlocked": False, "icon": "⛏️", "requirement": "Click the mine button once", "condition": lambda: self.gold >= 1},
            "Pocket Change": {"unlocked": False, "icon": "💰", "requirement": "Earn 100 gold total", "condition": lambda: self.total_gold >= 100},
            "Riches": {"unlocked": False, "icon": "💵", "requirement": "Earn 10,000 gold total", "condition": lambda: self.total_gold >= 10000},
            "Wealth": {"unlocked": False, "icon": "💸", "requirement": "Earn 100,000 gold total", "condition": lambda: self.total_gold >= 100000},
            "Millionaire": {"unlocked": False, "icon": "🤑", "requirement": "Earn 1,000,000 gold total", "condition": lambda: self.total_gold >= 1000000},
            "Billionaire": {"unlocked": False, "icon": "💎", "requirement": "Earn 1,000,000,000 gold total", "condition": lambda: self.total_gold >= 1000000000},
            "Trillionaire": {"unlocked": False, "icon": "👑", "requirement": "Earn 1,000,000,000,000 gold total", "condition": lambda: self.total_gold >= 1000000000000},
            "First Building": {"unlocked": False, "icon": "🏗️", "requirement": "Buy your first building", "condition": lambda: sum(b["count"] for b in self.buildings.values()) >= 1},
            "Builder": {"unlocked": False, "icon": "👷", "requirement": "Own 10 buildings total", "condition": lambda: sum(b["count"] for b in self.buildings.values()) >= 10},
            "Architect": {"unlocked": False, "icon": "🏛️", "requirement": "Own 100 buildings total", "condition": lambda: sum(b["count"] for b in self.buildings.values()) >= 100},
            "Master Builder": {"unlocked": False, "icon": "🏰", "requirement": "Own 500 buildings total", "condition": lambda: sum(b["count"] for b in self.buildings.values()) >= 500},
            "First Upgrade": {"unlocked": False, "icon": "⚡", "requirement": "Purchase your first upgrade", "condition": lambda: sum(1 for u in self.upgrades.values() if u["purchased"]) >= 1},
            "Upgraded": {"unlocked": False, "icon": "🔋", "requirement": "Purchase 5 upgrades", "condition": lambda: sum(1 for u in self.upgrades.values() if u["purchased"]) >= 5},
            "Optimizer": {"unlocked": False, "icon": "⚙️", "requirement": "Purchase 15 upgrades", "condition": lambda: sum(1 for u in self.upgrades.values() if u["purchased"]) >= 15},
            "Power User": {"unlocked": False, "icon": "🚀", "requirement": "Purchase 30 upgrades", "condition": lambda: sum(1 for u in self.upgrades.values() if u["purchased"]) >= 30},
            "Ultimate Miner": {"unlocked": False, "icon": "⭐", "requirement": "Purchase 50 upgrades", "condition": lambda: sum(1 for u in self.upgrades.values() if u["purchased"]) >= 50},
            "Golden Touch": {"unlocked": False, "icon": "✨", "requirement": "Have a building producing 1,000 gold/sec", "condition": lambda: max([self.calculate_building_gps(b) for b in self.buildings.keys()], default=0) >= 1000},
            "Million Miner": {"unlocked": False, "icon": "🌟", "requirement": "Have a building producing 1,000,000 gold/sec", "condition": lambda: max([self.calculate_building_gps(b) for b in self.buildings.keys()], default=0) >= 1000000},
            "Billion Builder": {"unlocked": False, "icon": "💫", "requirement": "Have a building producing 1,000,000,000 gold/sec", "condition": lambda: max([self.calculate_building_gps(b) for b in self.buildings.keys()], default=0) >= 1000000000},
            "Diamond Collector": {"unlocked": False, "icon": "💍", "requirement": "Own a Diamond Forge", "condition": lambda: self.buildings["Diamond Forge"]["count"] >= 1},
            "Mythril Master": {"unlocked": False, "icon": "⚔️", "requirement": "Own a Mythril Deep", "condition": lambda: self.buildings["Mythril Deep"]["count"] >= 1},
            "Ethereal Expert": {"unlocked": False, "icon": "🌌", "requirement": "Own an Ethereal Vault", "condition": lambda: self.buildings["Ethereal Vault"]["count"] >= 1},
            "Time Traveler": {"unlocked": False, "icon": "⏰", "requirement": "Earn 1 million gold while offline", "condition": lambda: False},
            "Gold Magnet": {"unlocked": False, "icon": "🧲", "requirement": "Have 10 million gold earned passively per second", "condition": lambda: self.gold_per_second >= 10000000},
            "Passive Income": {"unlocked": False, "icon": "💼", "requirement": "Earn 100 million total gold from buildings", "condition": lambda: self.total_gold >= 100000000},
            "Clicking Master": {"unlocked": False, "icon": "🖱️", "requirement": "Click 1,000 times", "condition": lambda: self.total_clicks >= 1000 if hasattr(self, 'total_clicks') else False},
            "Speed Clicker": {"unlocked": False, "icon": "⚡⚡", "requirement": "Get gold per click above 1,000", "condition": lambda: self.gold_per_click >= 1000},
            "Full Arsenal": {"unlocked": False, "icon": "🎯", "requirement": "Own at least 1 of every building type", "condition": lambda: all(b["count"] >= 1 for b in self.buildings.values())},
            "Infinite Power": {"unlocked": False, "icon": "♾️", "requirement": "Earn 1 quadrillion gold total", "condition": lambda: self.total_gold >= 1000000000000000},
        }
        
        self.total_gold = 0
        self.total_time_online = 0
        self.session_start_time = time.time()
        
        self.save_file = "idle_game_save.json"
        
        self.setup_ui()
        self.load_game()
        self.check_achievements()
        self.update_game()
    
    def _on_mousewheel(self, event, canvas):
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(3, "units")
        elif event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-3, "units")
    
    def _bind_scroll(self, canvas, scrollable_frame):
        def _bind_recursive(widget):
            widget.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))
            widget.bind("<Button-4>", lambda e: self._on_mousewheel(e, canvas))
            widget.bind("<Button-5>", lambda e: self._on_mousewheel(e, canvas))
            for child in widget.winfo_children():
                _bind_recursive(child)
        
        canvas.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, canvas))
        _bind_recursive(scrollable_frame)
    
    def show_building_tooltip(self, event, building_name):
        self.hide_building_tooltip()
        pass
    
    def hide_building_tooltip(self):
        try:
            if hasattr(self, 'tooltip') and self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None
        except:
            pass
    
    def setup_ui(self):
        self.root.configure(bg="#0d1117")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        main_frame = tk.Frame(self.root, bg="#0d1117")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=2)

        self.notification_frame = tk.Frame(self.root, bg="#238636", relief=tk.FLAT, bd=0)
        
        notification_label = tk.Label(
            self.notification_frame,
            text="💾 Game Saved!",
            font=("Segoe UI", 11, "bold"),
            bg="#238636",
            fg="white",
            padx=16,
            pady=10
        )
        notification_label.pack(side=tk.LEFT)

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

        control_frame.columnconfigure(0, weight=1)
        
        save_button = tk.Button(
            control_frame,
            text="💾 Save",
            command=self.save_game,
            bg="#1f6feb",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=18,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#388bfd",
            activeforeground="white",
        )
        save_button.grid(row=0, column=0, sticky="w", padx=(0, 8))
        
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
        reset_button.grid(row=0, column=1, sticky="w")
        
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
        
        notebook = ttk.Notebook(right_frame)
        notebook.grid(row=0, column=0, sticky="nsew")
        
        buildings_frame = tk.Frame(notebook, bg="#0d1117")
        notebook.add(buildings_frame, text="🏗️ Buildings")
        
        canvas = tk.Canvas(buildings_frame, bg="#0d1117", highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg="#0d1117")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        buildings_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _sync_buildings_width(e):
            canvas.itemconfigure(buildings_window, width=e.width)
        canvas.bind("<Configure>", _sync_buildings_width)
        canvas.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, canvas))
        
        building_icons = {
            "Pickaxe": "⛏️",
            "Miner": "👷",
            "Drill": "🔩",
            "Mineshaft": "⛏️",
            "Excavator": "🚜",
            "Quarry": "⛰️",
            "Gold Factory": "🏭",
            "Gem Mine": "💎",
            "Crystal Cavern": "✨",
            "Diamond Forge": "🔥",
            "Mythril Deep": "⚔️",
            "Ethereal Vault": "🌌"
        }
        
        self.building_buttons = {}
        for name, data in self.buildings.items():
            container = tk.Frame(scrollable_frame, bg="#0d1117", height=60)
            container.pack(fill=tk.X, padx=8, pady=6)
            container.pack_propagate(False)
            
            accent_colors = ["#238636", "#1f6feb", "#da3633", "#f85149", "#a5a5a5", 
                           "#f0c674", "#58a6ff", "#f0883e", "#bc8cff", "#ff7b72"]
            color_index = list(self.buildings.keys()).index(name) % len(accent_colors)
            
            accent_bar = tk.Frame(container, bg=accent_colors[color_index], width=4)
            accent_bar.pack(side=tk.LEFT, fill=tk.Y)
            
            content_frame = tk.Frame(container, bg="#161b22")
            content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
            
            icon_text = building_icons.get(name, "🏗️")
            icon_label = tk.Label(
                content_frame,
                text=icon_text,
                font=("Segoe UI", 16),
                bg="#161b22",
                fg=accent_colors[color_index],
                padx=16,
                pady=10,
                width=3
            )
            icon_label.pack(side=tk.LEFT, anchor="nw")
            
            info_label = tk.Label(
                content_frame,
                text=f"{name} (0)\nBase: 0/s | Total: 0/s",
                font=("Segoe UI", 11),
                bg="#161b22",
                fg="#c9d1d9",
                anchor="nw",
                justify=tk.LEFT,
                padx=0,
                pady=10
            )
            info_label.pack(side=tk.LEFT, anchor="nw", expand=True, fill=tk.BOTH)
            
            buy_button = tk.Button(
                content_frame,
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
                width=18
            )
            buy_button.pack(side=tk.RIGHT, padx=(10, 16), pady=10, anchor="e")
            
            self.building_buttons[name] = {
                "info": info_label,
                "button": buy_button,
                "frame": content_frame,
                "container": container,
                "accent": accent_bar,
                "base_gps": data['gps']
            }
            
            def _on_enter(event, building_name=name):
                self.show_building_tooltip(event, building_name)
            def _on_leave(event):
                self.hide_building_tooltip()
            
            container.bind("<Enter>", _on_enter)
            container.bind("<Leave>", _on_leave)
            content_frame.bind("<Enter>", _on_enter)
            content_frame.bind("<Leave>", _on_leave)
            icon_label.bind("<Enter>", _on_enter)
            icon_label.bind("<Leave>", _on_leave)
            info_label.bind("<Enter>", _on_enter)
            info_label.bind("<Leave>", _on_leave)
            buy_button.bind("<Enter>", _on_enter)
            buy_button.bind("<Leave>", _on_leave)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._bind_scroll(canvas, scrollable_frame)
        upgrades_frame = tk.Frame(notebook, bg="#0d1117")
        notebook.add(upgrades_frame, text="⚙️ Upgrades")
        
        canvas2 = tk.Canvas(upgrades_frame, bg="#0d1117", highlightthickness=0)
        scrollable_upgrades = tk.Frame(canvas2, bg="#0d1117")
        
        scrollable_upgrades.bind(
            "<Configure>",
            lambda e: canvas2.configure(scrollregion=canvas2.bbox("all"))
        )
        
        upgrades_window = canvas2.create_window((0, 0), window=scrollable_upgrades, anchor="nw")

        def _sync_upgrades_width(e):
            canvas2.itemconfigure(upgrades_window, width=e.width)
        canvas2.bind("<Configure>", _sync_upgrades_width)
        canvas2.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas2))
        canvas2.bind("<Button-4>", lambda e: self._on_mousewheel(e, canvas2))
        canvas2.bind("<Button-5>", lambda e: self._on_mousewheel(e, canvas2))
        
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
            frame.columnconfigure(0, weight=0)
            frame.columnconfigure(1, weight=0)
            frame.columnconfigure(2, weight=1)
            frame.columnconfigure(3, weight=0)

            icon_text = upgrade_icons.get(effect_type, "✨")
            icon_label = tk.Label(
                frame,
                text=icon_text,
                font=("Segoe UI", 14),
                bg="#161b22",
                fg=accent_color,
                anchor="w",
            )
            icon_label.grid(row=0, column=0, sticky="w", padx=(16, 12), pady=12)
            
            info_label = tk.Label(
                frame,
                text=name,
                font=("Segoe UI", 11, "bold"),
                bg="#161b22",
                fg="#c9d1d9",
                anchor="w",
            )
            info_label.grid(row=0, column=1, sticky="w", padx=0, pady=12)

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
            effect_label.grid(row=1, column=1, sticky="w", padx=0, pady=(0, 8))

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
                width=20
            )
            buy_button.grid(row=0, column=3, rowspan=2, sticky="ne", padx=(10, 16), pady=10)
            
            self.upgrade_buttons[name] = {
                "button": buy_button,
                "frame": frame,
                "info": info_label,
                "effect": effect_label,
                "container": container,
                "accent": accent_bar
            }
        
        canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._bind_scroll(canvas2, scrollable_upgrades)
        
        achievements_frame = tk.Frame(notebook, bg="#0d1117")
        notebook.add(achievements_frame, text="🏆 Achievements")
        
        canvas3 = tk.Canvas(achievements_frame, bg="#0d1117", highlightthickness=0)
        scrollable_achievements = tk.Frame(canvas3, bg="#0d1117")
        
        scrollable_achievements.bind(
            "<Configure>",
            lambda e: canvas3.configure(scrollregion=canvas3.bbox("all"))
        )
        
        achievements_window = canvas3.create_window((0, 0), window=scrollable_achievements, anchor="nw")

        def _sync_achievements_width(e):
            canvas3.itemconfigure(achievements_window, width=e.width)
        canvas3.bind("<Configure>", _sync_achievements_width)
        canvas3.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas3))
        canvas3.bind("<Button-4>", lambda e: self._on_mousewheel(e, canvas3))
        canvas3.bind("<Button-5>", lambda e: self._on_mousewheel(e, canvas3))
        
        self.achievement_labels = {}
        for name, data in self.achievements.items():
            container = tk.Frame(scrollable_achievements, bg="#0d1117")
            container.pack(fill=tk.X, padx=8, pady=6)
            
            accent_bar = tk.Frame(container, bg="#f0c674" if data["unlocked"] else "#21262d", width=4)
            accent_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0))
            
            frame = tk.Frame(container, bg="#161b22" if not data["unlocked"] else "#1a472a", relief=tk.FLAT, bd=0)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            frame.columnconfigure(0, weight=0)
            frame.columnconfigure(1, weight=1)
            
            icon_label = tk.Label(
                frame,
                text=data["icon"],
                font=("Segoe UI", 18),
                bg="#161b22" if not data["unlocked"] else "#1a472a",
                fg="#f0c674" if data["unlocked"] else "#8b949e",
                anchor="w",
            )
            icon_label.grid(row=0, column=0, sticky="w", padx=(16, 12), pady=12)
            
            title_label = tk.Label(
                frame,
                text=name,
                font=("Segoe UI", 12, "bold"),
                bg="#161b22" if not data["unlocked"] else "#1a472a",
                fg="#c9d1d9" if not data["unlocked"] else "#3fb950",
                anchor="w",
            )
            title_label.grid(row=0, column=1, sticky="w", padx=0, pady=(12, 2))
            
            req_label = tk.Label(
                frame,
                text=data["requirement"],
                font=("Segoe UI", 9),
                bg="#161b22" if not data["unlocked"] else "#1a472a",
                fg="#8b949e",
                anchor="w",
                wraplength=250,
                justify=tk.LEFT
            )
            req_label.grid(row=1, column=1, sticky="w", padx=0, pady=(0, 10))
            
            self.achievement_labels[name] = {
                "frame": frame,
                "accent": accent_bar,
                "title": title_label,
                "req": req_label
            }
        
        canvas3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._bind_scroll(canvas3, scrollable_achievements)
        
        stats_frame = tk.Frame(notebook, bg="#0d1117")
        notebook.add(stats_frame, text="📊 Statistics")
        
        stats_canvas = tk.Canvas(stats_frame, bg="#0d1117", highlightthickness=0)
        stats_scrollable = tk.Frame(stats_canvas, bg="#0d1117")
        
        stats_scrollable.bind(
            "<Configure>",
            lambda e: stats_canvas.configure(scrollregion=stats_canvas.bbox("all"))
        )
        
        stats_window = stats_canvas.create_window((0, 0), window=stats_scrollable, anchor="nw")

        def _sync_stats_width(e):
            stats_canvas.itemconfigure(stats_window, width=e.width)
        stats_canvas.bind("<Configure>", _sync_stats_width)
        stats_canvas.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, stats_canvas))
        stats_canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, stats_canvas))
        stats_canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, stats_canvas))
        
        stats_title = tk.Label(
            stats_scrollable,
            text="📊 Statistics",
            font=("Segoe UI", 22, "bold"),
            bg="#0d1117",
            fg="#c9d1d9"
        )
        stats_title.pack(pady=24)
        
        self.stats_labels = {}
        
        stats_data = [
            ("Total Gold Produced", "total_gold", "💰"),
            ("Current Gold", "gold", "💎"),
            ("Gold Per Second", "gps", "⚡"),
            ("Total Buildings Owned", "total_buildings", "🏗️"),
            ("Total Upgrades Purchased", "total_upgrades", "⬆️"),
            ("Achievements Unlocked", "achievements_unlocked", "🏆"),
            ("Time Played", "time_played", "⏱️"),
        ]
        
        for label_text, stat_key, icon in stats_data:
            stat_container = tk.Frame(stats_scrollable, bg="#161b22", relief=tk.FLAT, bd=0)
            stat_container.pack(fill=tk.X, padx=20, pady=12)
            
            icon_label = tk.Label(
                stat_container,
                text=icon,
                font=("Segoe UI", 16),
                bg="#161b22",
                fg="#58a6ff",
                anchor="w"
            )
            icon_label.pack(side=tk.LEFT, padx=(16, 12), pady=12)
            
            text_frame = tk.Frame(stat_container, bg="#161b22")
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=12)
            
            title_label = tk.Label(
                text_frame,
                text=label_text,
                font=("Segoe UI", 11, "bold"),
                bg="#161b22",
                fg="#c9d1d9",
                anchor="w"
            )
            title_label.pack(anchor="w")
            
            value_label = tk.Label(
                text_frame,
                text="0",
                font=("Segoe UI", 13, "bold"),
                bg="#161b22",
                fg="#3fb950",
                anchor="w"
            )
            value_label.pack(anchor="w", pady=(2, 0))
            
            self.stats_labels[stat_key] = value_label
        
        stats_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._bind_scroll(stats_canvas, stats_scrollable)
        
        settings_frame = tk.Frame(notebook, bg="#0d1117")
        notebook.add(settings_frame, text="⚙️ Settings")
        
        settings_canvas = tk.Canvas(settings_frame, bg="#0d1117", highlightthickness=0)
        settings_scrollable = tk.Frame(settings_canvas, bg="#0d1117")
        
        settings_scrollable.bind(
            "<Configure>",
            lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))
        )
        
        settings_window = settings_canvas.create_window((0, 0), window=settings_scrollable, anchor="nw")

        def _sync_settings_width(e):
            settings_canvas.itemconfigure(settings_window, width=e.width)
        settings_canvas.bind("<Configure>", _sync_settings_width)
        settings_canvas.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, settings_canvas))
        settings_canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, settings_canvas))
        settings_canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, settings_canvas))
        
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
        
        auto_save_frame = tk.Frame(settings_scrollable, bg="#161b22", relief=tk.FLAT, bd=0)
        auto_save_frame.pack(fill=tk.X, padx=20, pady=12)
        
        auto_save_label = tk.Label(
            auto_save_frame,
            text="Auto Save",
            font=("Segoe UI", 13, "bold"),
            bg="#161b22",
            fg="#c9d1d9"
        )
        auto_save_label.pack(anchor="w", padx=16, pady=(16, 12))
        
        auto_save_toggle_frame = tk.Frame(auto_save_frame, bg="#161b22")
        auto_save_toggle_frame.pack(fill=tk.X, padx=16, pady=(0, 12))
        
        self.auto_save_var = tk.BooleanVar(value=self.auto_save_enabled)
        auto_save_check = tk.Checkbutton(
            auto_save_toggle_frame,
            text="Enable Auto Save",
            variable=self.auto_save_var,
            command=self.toggle_auto_save,
            bg="#161b22",
            fg="#c9d1d9",
            selectcolor="#21262d",
            activebackground="#161b22",
            activeforeground="#c9d1d9",
            font=("Segoe UI", 10),
            relief=tk.FLAT
        )
        auto_save_check.pack(side=tk.LEFT)
        
        auto_save_interval_frame = tk.Frame(auto_save_frame, bg="#161b22")
        auto_save_interval_frame.pack(fill=tk.X, padx=16, pady=(0, 12))
        
        interval_label = tk.Label(
            auto_save_interval_frame,
            text="Interval:",
            font=("Segoe UI", 10),
            bg="#161b22",
            fg="#c9d1d9"
        )
        interval_label.pack(side=tk.LEFT, padx=(0, 12))
        
        self.auto_save_interval_var = tk.StringVar(value=str(self.auto_save_interval))
        interval_combo = ttk.Combobox(
            auto_save_interval_frame,
            values=["15", "30", "60"],
            textvariable=self.auto_save_interval_var,
            state="readonly",
            width=10,
            font=("Segoe UI", 10)
        )
        interval_combo.pack(side=tk.LEFT)
        interval_combo.bind("<<ComboboxSelected>>", self.on_interval_changed)
        
        seconds_label = tk.Label(
            auto_save_interval_frame,
            text="seconds",
            font=("Segoe UI", 10),
            bg="#161b22",
            fg="#c9d1d9"
        )
        seconds_label.pack(side=tk.LEFT, padx=(8, 0))
        
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
        self._bind_scroll(settings_canvas, settings_scrollable)
        
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
        self.total_clicks += 1
        
        gold_multiplier = 1
        for upgrade in self.upgrades.values():
            if upgrade["purchased"] and upgrade["effect"] == "gold":
                gold_multiplier *= upgrade["multiplier"]
        
        self.gold += self.gold_per_click * gold_multiplier
        self.total_gold += self.gold_per_click * gold_multiplier
        self.check_achievements()
        self.update_display()
        
    def buy_building(self, name):
        building = self.buildings[name]
        cost = int(building["cost"])
        
        if self.gold >= cost:
            self.gold -= cost
            building["count"] += 1
            building["cost"] = building["cost"] * building["cost_multiplier"]
            self.calculate_gps()
            self.check_achievements()
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
            
            self.check_achievements()
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
    
    def check_achievements(self):
        unlocked_new = False
        for name, data in self.achievements.items():
            if not data["unlocked"]:
                try:
                    if data["condition"]():
                        data["unlocked"] = True
                        unlocked_new = True
                        self.show_achievement_notification(name, data["icon"])
                        if hasattr(self, 'achievement_labels') and name in self.achievement_labels:
                            labels = self.achievement_labels[name]
                            labels["frame"].config(bg="#1a472a")
                            labels["accent"].config(bg="#f0c674")
                            labels["title"].config(bg="#1a472a", fg="#3fb950")
                            labels["req"].config(bg="#1a472a")
                except:
                    pass
    
    def refresh_achievement_display(self):
        if not hasattr(self, 'achievement_labels'):
            return
        for name, data in self.achievements.items():
            if name in self.achievement_labels:
                labels = self.achievement_labels[name]
                if data["unlocked"]:
                    labels["frame"].config(bg="#1a472a")
                    labels["accent"].config(bg="#f0c674")
                    labels["title"].config(bg="#1a472a", fg="#3fb950")
                    labels["req"].config(bg="#1a472a")
                else:
                    labels["frame"].config(bg="#161b22")
                    labels["accent"].config(bg="#21262d")
                    labels["title"].config(bg="#161b22", fg="#c9d1d9")
                    labels["req"].config(bg="#161b22")
    
    def update_game(self):
        current_time = time.time()
        time_passed = current_time - self.last_save_time
        self.gold += self.gold_per_second * time_passed
        self.total_gold += self.gold_per_second * time_passed
        self.last_save_time = current_time
        
        self.update_display()
        self.check_achievements()
        
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
            base_gps = building["gps"]
            current_gps = self.calculate_building_gps(name)
            
            elements["info"].config(text=f"{name} ({count})\nBase: {self.format_number(base_gps)}/s | Total: {self.format_number(current_gps)}/s")
            elements["button"].config(text=f"Buy: {self.format_number(cost)} gold")
            
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
        
        self.update_statistics()
    
    def update_statistics(self):
        if not hasattr(self, 'stats_labels'):
            return
        
        total_buildings = sum(b["count"] for b in self.buildings.values())
        total_upgrades = sum(1 for u in self.upgrades.values() if u["purchased"])
        achievements_unlocked = sum(1 for a in self.achievements.values() if a["unlocked"])
        
        current_time = time.time()
        time_played = current_time - self.session_start_time
        hours = int(time_played // 3600)
        minutes = int((time_played % 3600) // 60)
        seconds = int(time_played % 60)
        
        if hours > 0:
            time_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            time_str = f"{minutes}m {seconds}s"
        else:
            time_str = f"{seconds}s"
        
        self.stats_labels["total_gold"].config(text=f"{self.format_number(self.total_gold)}")
        self.stats_labels["gold"].config(text=f"{self.format_number(self.gold)}")
        self.stats_labels["gps"].config(text=f"{self.format_number(self.gold_per_second)}")
        self.stats_labels["total_buildings"].config(text=f"{total_buildings}")
        self.stats_labels["total_upgrades"].config(text=f"{total_upgrades}")
        self.stats_labels["achievements_unlocked"].config(text=f"{achievements_unlocked}/16")
        self.stats_labels["time_played"].config(text=time_str)
    
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
        buildings_to_save = {}
        for name, building in self.buildings.items():
            buildings_to_save[name] = {
                "count": building["count"],
                "cost": building["cost"],
                "gps": building["gps"],
                "cost_multiplier": building["cost_multiplier"]
            }
        
        achievements_to_save = {}
        for name, achievement in self.achievements.items():
            achievements_to_save[name] = {
                "unlocked": achievement["unlocked"],
                "icon": achievement["icon"],
                "requirement": achievement["requirement"]
            }
        
        current_time = time.time()
        session_time = current_time - self.session_start_time
        
        save_data = {
            "gold": self.gold,
            "total_gold": self.total_gold,
            "total_clicks": self.total_clicks,
            "gold_per_click": self.gold_per_click,
            "buildings": buildings_to_save,
            "upgrades": self.upgrades,
            "achievements": achievements_to_save,
            "total_time_online": self.total_time_online + session_time,
            "timestamp": current_time,
            "volume": self.volume,
            "muted": self.muted,
            "auto_save_enabled": self.auto_save_enabled,
            "auto_save_interval": self.auto_save_interval
        }
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f)
            self.show_save_notification()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save game: {e}")
    
    def show_save_notification(self):
        if self.save_notification_id:
            self.root.after_cancel(self.save_notification_id)
        
        y_offset = 10
        if hasattr(self, 'achievement_frames') and self.achievement_frames:
            y_offset += len([f for f in self.achievement_frames if f.winfo_exists()]) * 75
        
        self.notification_frame.place(in_=self.root, relx=1.0, rely=0.0, anchor="ne", x=-10, y=y_offset)
        
        self.save_notification_id = self.root.after(1800, self.fade_save_notification)
    
    def fade_save_notification(self):
        self.notification_frame.place_forget()
        self.save_notification_id = None
    
    def hide_save_notification(self):
        self.notification_frame.place_forget()
        self.save_notification_id = None
    
    def show_achievement_notification(self, achievement_name, achievement_icon):
        if not hasattr(self, 'achievement_frames'):
            self.achievement_frames = []
        
        achievement_frame = tk.Frame(self.root, bg="#238636", relief=tk.FLAT, bd=0)
        self.achievement_frames.append(achievement_frame)
        
        notification_label = tk.Label(
            achievement_frame,
            text=f"{achievement_icon} Achievement Unlocked!\n{achievement_name}",
            font=("Segoe UI", 11, "bold"),
            bg="#238636",
            fg="white",
            padx=16,
            pady=10,
            justify=tk.CENTER
        )
        notification_label.pack()
        
        y_offset = 10 + (len(self.achievement_frames) - 1) * 75
        achievement_frame.place(in_=self.root, relx=1.0, rely=0.0, anchor="ne", x=-10, y=y_offset)
        
        alpha = [1.0]
        
        def fade_achievement():
            alpha[0] -= 0.1
            if alpha[0] <= 0:
                try:
                    achievement_frame.destroy()
                    if achievement_frame in self.achievement_frames:
                        self.achievement_frames.remove(achievement_frame)
                except:
                    pass
            else:
                try:
                    r = int(0x23 * alpha[0])
                    g = int(0x86 * alpha[0])
                    b = int(0x36 * alpha[0])
                    notification_label.config(bg=f"#{r:02x}{g:02x}{b:02x}")
                    achievement_frame.config(bg=f"#{r:02x}{g:02x}{b:02x}")
                except:
                    pass
                self.root.after(30, fade_achievement)
        
        self.root.after(2500, fade_achievement)
    
    def toggle_auto_save(self):
        self.auto_save_enabled = self.auto_save_var.get()
        if self.auto_save_enabled:
            self.schedule_auto_save()
        else:
            self.cancel_auto_save()
    
    def on_interval_changed(self, event):
        self.auto_save_interval = int(self.auto_save_interval_var.get())
        if self.auto_save_enabled:
            self.cancel_auto_save()
            self.schedule_auto_save()
    
    def schedule_auto_save(self):
        self.auto_save_task_id = self.root.after(self.auto_save_interval * 1000, self.perform_auto_save)
    
    def perform_auto_save(self):
        self.save_game()
        self.schedule_auto_save()
    
    def cancel_auto_save(self):
        if self.auto_save_task_id:
            self.root.after_cancel(self.auto_save_task_id)
            self.auto_save_task_id = None
    
    def load_game(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    save_data = json.load(f)
                
                self.gold = save_data.get("gold", 0)
                self.total_gold = save_data.get("total_gold", 0)
                self.total_clicks = save_data.get("total_clicks", 0)
                self.gold_per_click = save_data.get("gold_per_click", 1)
                self.total_time_online = save_data.get("total_time_online", 0)
                
                loaded_buildings = save_data.get("buildings", {})
                for name in self.buildings.keys():
                    if name in loaded_buildings:
                        self.buildings[name] = loaded_buildings[name]
                    else:
                        self.buildings[name]["count"] = 0
                        self.buildings[name]["cost"] = self.buildings[name].get("cost", 0)
                
                self.upgrades = save_data.get("upgrades", self.upgrades)
                
                loaded_achievements = save_data.get("achievements", {})
                for name in self.achievements.keys():
                    if name in loaded_achievements:
                        self.achievements[name]["unlocked"] = loaded_achievements[name].get("unlocked", False)
                
                self.volume = save_data.get("volume", 0.5)
                self.muted = save_data.get("muted", False)
                
                self.auto_save_enabled = save_data.get("auto_save_enabled", False)
                self.auto_save_interval = save_data.get("auto_save_interval", 15)
                self.auto_save_var.set(self.auto_save_enabled)
                self.auto_save_interval_var.set(str(self.auto_save_interval))
                
                if self.auto_save_enabled:
                    self.schedule_auto_save()
                
                saved_time = save_data.get("timestamp", time.time())
                offline_time = time.time() - saved_time
                
                self.calculate_gps()
                offline_gold = self.gold_per_second * offline_time
                
                if offline_gold > 0:
                    self.gold += offline_gold
                    self.total_gold += offline_gold
                    messagebox.showinfo("Welcome Back!", 
                                      f"You were offline for {int(offline_time)} seconds.\n"
                                      f"You earned {self.format_number(offline_gold)} gold!")
                
                self.session_start_time = time.time()
                self.last_save_time = time.time()
                self.refresh_achievement_display()
                self.update_display()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load game: {e}")
    
    def reset_game(self):
        if messagebox.askyesno("Reset Game", "Are you sure you want to reset? All progress will be lost!"):
            self.gold = 0
            self.total_gold = 0
            self.total_clicks = 0
            self.total_time_online = 0
            self.gold_per_click = 1
            self.gold_per_second = 0
            self.session_start_time = time.time()
            self.auto_save_enabled = False
            self.auto_save_interval = 15
            self.auto_save_var.set(False)
            self.auto_save_interval_var.set("15")
            self.cancel_auto_save()
            
            for building in self.buildings.values():
                original_cost = building["cost"] / (building["cost_multiplier"] ** building["count"])
                building["count"] = 0
                building["cost"] = original_cost
            
            for upgrade in self.upgrades.values():
                upgrade["purchased"] = False
            
            for achievement in self.achievements.values():
                achievement["unlocked"] = False
            
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
                    self.total_gold = 0
                    self.total_clicks = 0
                    self.total_time_online = 0
                    self.gold_per_click = 1
                    self.gold_per_second = 0
                    self.session_start_time = time.time()
                    self.auto_save_enabled = False
                    self.auto_save_interval = 15
                    self.auto_save_var.set(False)
                    self.auto_save_interval_var.set("15")
                    self.cancel_auto_save()
                    
                    for building in self.buildings.values():
                        original_cost = building["cost"] / (building["cost_multiplier"] ** building["count"])
                        building["count"] = 0
                        building["cost"] = original_cost
                    
                    for upgrade in self.upgrades.values():
                        upgrade["purchased"] = False
                    
                    for achievement in self.achievements.values():
                        achievement["unlocked"] = False
                    
                    self.calculate_gps()
                    self.update_display()
                    
                    messagebox.showinfo("Success", "All game data has been deleted.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    game = IdleMiningGame(root)
    root.mainloop()
