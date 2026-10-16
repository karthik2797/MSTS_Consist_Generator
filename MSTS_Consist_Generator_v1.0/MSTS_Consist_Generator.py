import os
import random
import re
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "MSTS Consist Generator"
COFFEE_URL = "https://buymeacoffee.com/irtsfan"
YOUTUBE_URL = "https://www.youtube.com/@IRTSFAN"
EMAIL_ADDRESS = "irtslover@gmail.com"


def safe_name(value):
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value.strip()).rstrip(". ")
    return value or "Random_Consist"


def msts_token(value):
    value = value.replace('"', '')
    return '"' + value + '"' if any(ch.isspace() for ch in value) else value


def matches(item, keywords):
    """Match special tail stock using its filename and containing folder."""
    haystack = f"{item.get('stem', '')} {item.get('folder', '')}".casefold()
    compact = re.sub(r"[^a-z0-9]+", "", haystack)
    for keyword in keywords:
        key = keyword.casefold()
        if key in haystack or re.sub(r"[^a-z0-9]+", "", key) in compact:
            return True
    return False


class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("980x760")
        self.root.minsize(820, 620)
        self.root.configure(bg="#f3f0e7")
        self.trainset = None
        self.stock = []
        self.output = None
        self.configure_style()
        self.make_ui()

    def configure_style(self):
        # Simple Indian Railways-inspired palette: railway blue, green, and saffron.
        self.bg = "#f3f0e7"
        self.blue = "#17324d"
        self.green = "#176b45"
        self.saffron = "#e58a2b"
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.root.option_add("*Font", ("Segoe UI", 9))
        style.configure("TFrame", background=self.bg)
        style.configure("Panel.TFrame", background="#fffdf8")
        style.configure("Header.TFrame", background=self.blue)
        style.configure("TLabel", background=self.bg, foreground="#202a32")
        style.configure("Muted.TLabel", background="#fffdf8", foreground="#56616a")
        style.configure("PanelTitle.TLabel", background="#fffdf8", foreground=self.blue, font=("Segoe UI", 10, "bold"))
        style.configure("Hero.TLabel", background=self.blue, foreground="#ffffff", font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel", background=self.blue, foreground="#e3eaf0", font=("Segoe UI", 9))
        style.configure("TLabelframe", background="#fffdf8", foreground=self.blue, bordercolor="#c9c6bb")
        style.configure("TLabelframe.Label", background="#fffdf8", foreground=self.blue, font=("Segoe UI", 9, "bold"))
        style.configure("TEntry", padding=4, fieldbackground="#ffffff")
        style.configure("TCombobox", padding=3, fieldbackground="#ffffff")
        style.configure("TCheckbutton", background="#fffdf8", foreground="#202a32")
        style.map("TCheckbutton", background=[("active", "#fffdf8")])
        style.configure("TButton", padding=(8, 5), background="#e7e5dc", foreground=self.blue)
        style.map("TButton", background=[("active", "#d8ded8")])
        style.configure("Accent.TButton", padding=(10, 6), font=("Segoe UI", 9, "bold"), background=self.green, foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#105536")], foreground=[("active", "#ffffff")])
        style.configure("Treeview", rowheight=23, background="#ffffff", fieldbackground="#ffffff", foreground="#202a32")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), padding=4, background="#e4e8e2", foreground=self.blue)

    def make_ui(self):
        outer = ttk.Frame(self.root, padding=(18, 14))
        outer.pack(fill="both", expand=True)
        hero = ttk.Frame(outer, style="Header.TFrame", padding=(12, 10))
        hero.pack(fill="x", pady=(0, 3))
        title_area = ttk.Frame(hero, style="Header.TFrame")
        title_area.pack(side="left", fill="x", expand=True)
        ttk.Label(title_area, text="MSTS Consist Generator", style="Hero.TLabel").pack(anchor="w")
        ttk.Label(title_area, text="Indian Railways-inspired consist builder  |  Create MSTS .con files", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))
        ttk.Button(hero, text="Buy Me a Coffee", command=lambda: webbrowser.open(COFFEE_URL)).pack(side="right", padx=(8, 0), pady=3)
        stripe = tk.Frame(outer, height=4, bg=self.saffron)
        stripe.pack(fill="x", pady=(0, 10))

        folder_box = ttk.LabelFrame(outer, text="  1  /  TRAINSET LIBRARY  ", padding=10)
        folder_box.pack(fill="x", pady=(0, 9))
        folder_line = ttk.Frame(folder_box, style="Panel.TFrame")
        folder_line.pack(fill="x")
        self.folder_var = tk.StringVar(value="No folder selected — select your MSTS TRAINS\\TRAINSET folder")
        ttk.Label(folder_line, textvariable=self.folder_var, style="Muted.TLabel").pack(side="left", fill="x", expand=True)
        ttk.Button(folder_line, text="Browse & Scan…", command=self.scan_trainset, style="Accent.TButton").pack(side="right")
        self.scan_var = tk.StringVar(value="Waiting for Trainset scan")
        ttk.Label(folder_box, textvariable=self.scan_var, style="Muted.TLabel").pack(anchor="w", pady=(6, 0))

        settings = ttk.LabelFrame(outer, text="  2  /  CONSIST SETTINGS  ", padding=10)
        settings.pack(fill="x", pady=(0, 9))
        fields = [
            ("count", "Consists to create", "10"), ("name", "Base filename / name", "Custom_Consist"),
            ("locos", "Locomotives per consist", "1"), ("coaches", "Passenger / coach count (.wag)", "8"),
            ("wagons", "Freight / extra count (.wag)", "0"), ("max", "Maximum vehicles", "40"),
            ("seed", "Random seed (optional)", ""), ("speed1", "MaxVelocity value 1", "36.11111"),
            ("speed2", "MaxVelocity value 2", "0.26445"),
        ]
        grid = ttk.Frame(settings, style="Panel.TFrame")
        grid.pack(fill="x")
        self.vars = {}
        for i, (key, label, default) in enumerate(fields):
            r, c = divmod(i, 3)
            cell = ttk.Frame(grid, style="Panel.TFrame", padding=4)
            cell.grid(row=r, column=c, sticky="ew")
            ttk.Label(cell, text=label, style="Muted.TLabel").pack(anchor="w")
            self.vars[key] = tk.StringVar(value=default)
            ttk.Entry(cell, textvariable=self.vars[key]).pack(fill="x", pady=(3, 0))
            grid.columnconfigure(c, weight=1)
        options = ttk.Frame(settings, style="Panel.TFrame")
        options.pack(fill="x", pady=(8, 0))
        ttk.Label(options, text="Stock mix:", style="Muted.TLabel").pack(side="left")
        self.mode = tk.StringVar(value="Mixed")
        ttk.Combobox(options, textvariable=self.mode, state="readonly", width=17, values=["Mixed", "Passenger", "Freight", "Rolling stock only"]).pack(side="left", padx=(6, 14))
        self.random_counts = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text="Randomize counts", variable=self.random_counts).pack(side="left", padx=(0, 12))
        self.no_repeat = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text="Avoid repeats where possible", variable=self.no_repeat).pack(side="left", padx=(0, 12))
        self.flip = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text="Random wagon Flip ( )", variable=self.flip).pack(side="left")

        advanced = ttk.LabelFrame(outer, text="  3  /  FORMATION LOGIC  ", padding=10)
        advanced.pack(fill="x", pady=(0, 9))
        row1 = ttk.Frame(advanced, style="Panel.TFrame")
        row1.pack(fill="x", pady=2)
        ttk.Label(row1, text="Locomotive policy:", style="Muted.TLabel").pack(side="left")
        self.loco_policy = tk.StringVar(value="Every consist")
        ttk.Combobox(row1, textvariable=self.loco_policy, state="readonly", width=24,
                     values=["Every consist", "Some consists (50%)", "Random (0 to maximum)", "No locomotives"]).pack(side="left", padx=7)
        ttk.Label(row1, text="Tail stock:", style="Muted.TLabel").pack(side="left", padx=(15, 4))
        self.tail_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(row1, text="Append SLR / BVZI / caboose / guard van at end", variable=self.tail_enabled).pack(side="left")
        row2 = ttk.Frame(advanced, style="Panel.TFrame")
        row2.pack(fill="x", pady=(5, 0))
        ttk.Label(row2, text="Tail policy:", style="Muted.TLabel").pack(side="left")
        self.tail_policy = tk.StringVar(value="Every eligible consist")
        ttk.Combobox(row2, textvariable=self.tail_policy, state="readonly", width=24,
                     values=["Every eligible consist", "Some consists (50%)", "Random"]).pack(side="left", padx=7)
        ttk.Label(advanced, text="Tail-stock detection uses filenames and folder names. Review generated consists before use.", style="Muted.TLabel", wraplength=900).pack(anchor="w", pady=(6, 0))

        action_row = ttk.Frame(outer)
        action_row.pack(fill="x", pady=(0, 7))
        ttk.Button(action_row, text="▶  GENERATE CONSISTS", style="Accent.TButton", command=self.generate).pack(side="left")
        ttk.Button(action_row, text="Clear Results", command=self.clear_results).pack(side="left", padx=7)
        ttk.Button(action_row, text="Open Output Folder", command=self.open_output).pack(side="left")
        self.status = tk.StringVar(value="Scan your Trainset, review settings, then generate.")
        ttk.Label(action_row, textvariable=self.status, wraplength=500).pack(side="right", padx=8)

        result = ttk.LabelFrame(outer, text="  4  /  GENERATED FILES  ", padding=7)
        result.pack(fill="both", expand=True)
        columns = ("file", "engines", "wagons", "path")
        self.tree = ttk.Treeview(result, columns=columns, show="headings", height=7)
        for col, label, width in [("file", "Consist filename", 220), ("engines", "Locos", 65), ("wagons", "Coaches / wagons", 130), ("path", "Output path", 500)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        scroll_y = ttk.Scrollbar(result, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(result, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        result.rowconfigure(0, weight=1)
        result.columnconfigure(0, weight=1)
        footer = tk.Frame(outer, bg=self.blue, padx=10, pady=8)
        footer.pack(fill="x", pady=(8, 0))
        ttk.Label(footer, text="Designed and developed by Karthik Iyer - IRTS FAN.",
                  background=self.blue, foreground="#ffffff", font=("Segoe UI", 9, "bold")).pack(side="left", anchor="w")
        links = tk.Frame(footer, bg=self.blue)
        links.pack(side="right")
        youtube_link = tk.Label(links, text="▶ YouTube: IRTS FAN", bg=self.blue, fg="#ffcf70",
                                cursor="hand2", font=("Segoe UI", 9, "underline"))
        youtube_link.pack(side="left", padx=(8, 12))
        youtube_link.bind("<Button-1>", lambda _event: webbrowser.open(YOUTUBE_URL))
        email_link = tk.Label(links, text="✉ irtslover@gmail.com", bg=self.blue, fg="#ffffff",
                              cursor="hand2", font=("Segoe UI", 9, "underline"))
        email_link.pack(side="left", padx=(0, 12))
        email_link.bind("<Button-1>", lambda _event: webbrowser.open("mailto:" + EMAIL_ADDRESS))
        tk.Label(links, text="Output: MSTS_Generated_Consists", bg=self.blue, fg="#dbe5ed",
                 font=("Segoe UI", 8)).pack(side="left")

    def scan_trainset(self):
        folder = filedialog.askdirectory(title="Select MSTS TRAINS\\TRAINSET folder")
        if not folder:
            return
        self.trainset = Path(folder)
        self.folder_var.set(folder)
        self.stock = []
        try:
            for path in self.trainset.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in (".eng", ".wag"):
                    continue
                rel = path.relative_to(self.trainset)
                # MSTS EngineData/WagonData expects the immediate Trainset folder token.
                # Skip deeply nested files because their paths cannot be represented reliably
                # by the standard two-token stock reference.
                if len(rel.parts) > 2:
                    continue
                folder_name = rel.parts[0] if len(rel.parts) == 2 else self.trainset.name
                self.stock.append({"type": path.suffix.lower()[1:], "stem": path.stem, "folder": folder_name})
        except OSError as exc:
            messagebox.showerror("Trainset scan failed", f"Could not read the selected folder.\n\n{exc}")
            self.stock = []
            return
        n_eng = sum(x["type"] == "eng" for x in self.stock)
        n_wag = sum(x["type"] == "wag" for x in self.stock)
        self.scan_var.set(f"Scanned {n_eng} locomotive (.eng) file(s)  |  {n_wag} wagon (.wag) file(s)")
        if not self.stock:
            self.status.set("No .eng/.wag files found. Select the actual TRAINSET folder.")
            messagebox.showwarning("No MSTS stock found", "No .eng or .wag files were found in the Trainset root or its immediate subfolders.\n\nSelect the actual TRAINS\\TRAINSET folder.")
        else:
            self.status.set("Scan complete — ready to generate.")

    def get_int(self, key, default, low, high):
        try:
            value = int(self.vars[key].get().strip())
        except (ValueError, AttributeError):
            value = default
        return max(low, min(high, value))

    def generate(self):
        if not self.trainset or not self.stock:
            messagebox.showwarning("Trainset not scanned", "Select a Trainset folder containing .eng and/or .wag files first.")
            return
        engines_all = [x for x in self.stock if x["type"] == "eng"]
        wagons_all = [x for x in self.stock if x["type"] == "wag"]
        count = self.get_int("count", 10, 1, 500)
        loco_max = self.get_int("locos", 1, 0, 20)
        coach_max = self.get_int("coaches", 8, 0, 100)
        wagon_max = self.get_int("wagons", 0, 0, 200)
        max_total = self.get_int("max", 40, 1, 250)
        mode = self.mode.get()
        if mode == "Passenger":
            wagon_max = 0
        elif mode == "Freight":
            coach_max = 0
        elif mode == "Rolling stock only":
            loco_max = 0
        if self.loco_policy.get() == "No locomotives":
            loco_max = 0

        engines = engines_all
        wagons = wagons_all

        if loco_max and not engines:
            messagebox.showerror("No locomotives", "No .eng files found. Set locomotive count to 0 or choose a folder containing locomotive files.")
            return
        if (coach_max + wagon_max) and not wagons:
            messagebox.showerror("No wagons", "No .wag files found for this formation. Set coach/wagon counts to 0 or choose the correct folder.")
            return
        try:
            speed1 = float(self.vars["speed1"].get())
            speed2 = float(self.vars["speed2"].get())
        except ValueError:
            messagebox.showerror("Invalid MaxVelocity", "Both MaxVelocity values must be numeric.")
            return

        seed = self.vars["seed"].get().strip()
        rng = random.Random(seed if seed else None)
        base = safe_name(self.vars["name"].get())
        outdir = self.trainset.parent / "MSTS_Generated_Consists"
        try:
            outdir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Output folder error", f"Cannot create output folder:\n{outdir}\n\n{exc}")
            return
        generated = []

        def choose(pool, n):
            if n <= 0 or not pool:
                return []
            if not self.no_repeat.get():
                return [rng.choice(pool) for _ in range(n)]
            shuffled = pool[:]
            rng.shuffle(shuffled)
            return [shuffled[i % len(shuffled)] for i in range(n)]

        width = max(2, len(str(count)))
        tail_keywords = ("slr", "bvzi", "caboose", "guardvan", "guard_van", "guard van", "brakevan", "brake_van", "brake van", "tail van")
        tail_stock = [x for x in wagons_all if matches(x, tail_keywords)]
        for idx in range(1, count + 1):
            n_eng, n_coach, n_wagon = loco_max, coach_max, wagon_max
            policy = self.loco_policy.get()
            if policy == "Some consists (50%)":
                n_eng = loco_max if rng.random() < 0.5 else 0
            elif policy == "Random (0 to maximum)":
                n_eng = rng.randint(0, loco_max) if loco_max else 0
            if self.random_counts.get():
                n_eng = rng.randint(0, n_eng) if n_eng else 0
                n_coach = rng.randint(0, coach_max) if coach_max else 0
                n_wagon = rng.randint(0, wagon_max) if wagon_max else 0
            add_tail = False
            if self.tail_enabled.get() and tail_stock:
                tp = self.tail_policy.get()
                add_tail = tp == "Every eligible consist" or (tp == "Some consists (50%)" and rng.random() < 0.5) or (tp == "Random" and rng.choice([True, False]))
            while n_eng + n_coach + n_wagon + (1 if add_tail else 0) > max_total:
                if n_wagon:
                    n_wagon -= 1
                elif n_coach:
                    n_coach -= 1
                elif n_eng:
                    n_eng -= 1
                else:
                    add_tail = False
            vehicles = [("Engine", x) for x in choose(engines, n_eng)]
            vehicles += [("Wagon", x) for x in choose(wagons, n_coach + n_wagon)]
            if add_tail:
                vehicles.append(("Wagon", rng.choice(tail_stock)))
            # Random counts can otherwise produce an empty consist; keep every output useful.
            if not vehicles:
                if engines and loco_max and self.loco_policy.get() != "No locomotives":
                    vehicles = [("Engine", rng.choice(engines))]
                elif wagons:
                    vehicles = [("Wagon", rng.choice(wagons))]
                else:
                    messagebox.showerror("No usable stock", "The current settings cannot create a consist with any vehicles.")
                    return
            filename_stem = f"{base}_{idx:0{width}d}"
            target = outdir / f"{filename_stem}.con"
            suffix = 1
            while target.exists():
                target = outdir / f"{filename_stem}_{suffix}.con"
                suffix += 1
            lines = ["SIMISA@@@@@@@@@@JINX0D0t______", "", "Train (", f'    TrainCfg ( "{target.stem}"',
                     f'        Name ( "{target.stem}" )', f"        Serial ( {idx} )",
                     f"        MaxVelocity ( {speed1:.5f} {speed2:.5f} )", f"        NextWagonUID ( {len(vehicles)} )", "        Durability ( 1.00000 )"]
            for uid, (kind, item) in enumerate(vehicles):
                folder_token = msts_token(item["folder"])
                if kind == "Engine":
                    lines += ["        Engine (", f"            UiD ( {uid} )", f"            EngineData ( {item['stem']} {folder_token} )", "        )"]
                else:
                    lines += ["        Wagon (", f"            WagonData ( {item['stem']} {folder_token} )"]
                    if self.flip.get() and rng.choice([True, False]):
                        lines.append("            Flip ( )")
                    lines += [f"            UiD ( {uid} )", "        )"]
            lines += ["    )", ")", ""]
            try:
                target.write_bytes("\r\n".join(lines).encode("cp1252", errors="replace"))
            except OSError as exc:
                messagebox.showerror("Write failed", f"Could not write this consist file:\n{target}\n\n{exc}")
                self.status.set("Generation stopped because a file could not be written.")
                return
            engine_count = sum(1 for kind, _ in vehicles if kind == "Engine")
            wagon_count = len(vehicles) - engine_count
            generated.append((target, engine_count, wagon_count))

        for item in self.tree.get_children():
            self.tree.delete(item)
        for target, n_eng, n_wag in generated:
            self.tree.insert("", "end", values=(target.name, n_eng, n_wag, str(target)))
        self.output = outdir
        self.status.set(f"Created {len(generated)} consist(s) successfully.")
        tail_note = f"\nDetected tail stock: {len(tail_stock)} file(s)." if self.tail_enabled.get() else ""
        if self.tail_enabled.get() and not tail_stock:
            tail_note = "\nNo SLR/BVZI/caboose/guard-van matches detected by filename/folder keywords."
        messagebox.showinfo("Consists generated", f"Created {len(generated)} .con file(s).\n\nOutput: {outdir}{tail_note}\n\nPlease test in MSTS before use.")

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status.set("Results cleared.")

    def open_output(self):
        if not self.trainset:
            messagebox.showinfo("Output folder", "Select the Trainset folder first.")
            return
        folder = self.output or (self.trainset.parent / "MSTS_Generated_Consists")
        folder.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(folder))
        except Exception:
            messagebox.showinfo("Output folder", str(folder))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
