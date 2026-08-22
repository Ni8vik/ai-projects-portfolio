"""Cluster Canvas: a native Python dataset maker.

Run with: python clustering_data_maker.py
"""

import csv
import json
import math
import random
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

COLORS = ("#ef735f", "#5775d8", "#f1be4b", "#9278d4", "#63b6a2", "#e58fbd")
PAPER = "#f2f0e9"
CARD = "#faf9f4"
INK = "#17211e"
MUTED = "#77807b"
LINE = "#dcded5"
CORAL = "#ef735f"


class ClusterCanvas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cluster Canvas | Dataset maker")
        self.geometry("1180x760")
        self.minsize(860, 620)
        self.configure(bg=PAPER)

        self.mode = tk.StringVar(value="spiral")
        self.point_count = tk.IntVar(value=420)
        self.seed = tk.IntVar(value=42)
        self.turns = tk.DoubleVar(value=2.4)
        self.noise = tk.DoubleVar(value=0.12)
        self.label_count = tk.IntVar(value=3)
        self.ring_spacing = tk.DoubleVar(value=0.12)
        self.brush_size = tk.IntVar(value=14)
        self.noise_width = tk.IntVar(value=0)
        self.data = []
        self.strokes = []
        self.active_stroke = None
        self.active_path_point = None
        self.gaussian_centers = []
        self.active_center_index = None

        self._build_ui()
        self._set_mode("spiral")
        self.after(100, self.generate)

    def _build_ui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg=PAPER, height=70)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=38)
        header.grid_propagate(False)
        tk.Label(header, text="●  clustercanvas", bg=PAPER, fg=INK, font=("Segoe UI", 18, "bold")).pack(side="left", pady=20)
        tk.Label(header, text="LOCAL DATA LAB", bg=PAPER, fg=MUTED, font=("Consolas", 9)).pack(side="right", pady=25)

        panel = tk.Frame(self, bg=CARD, highlightbackground=LINE, highlightthickness=1, width=300)
        panel.grid(row=1, column=0, sticky="ns", padx=(38, 0), pady=(0, 35))
        panel.grid_propagate(False)
        panel.columnconfigure(0, weight=1)
        tk.Label(panel, text="01 / SOURCE", bg=CARD, fg=CORAL, font=("Consolas", 9, "bold")).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 5))
        tk.Label(panel, text="Choose a starting point", bg=CARD, fg=INK, font=("Segoe UI", 14, "bold")).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 18))

        mode_frame = tk.Frame(panel, bg=CARD)
        mode_frame.grid(row=2, column=0, sticky="ew", padx=18)
        for name, value in (("Spiral", "spiral"), ("Gaussian blobs", "blobs"), ("Rings", "rings"), ("Two moons", "moons"), ("Paint", "paint")):
            tk.Radiobutton(mode_frame, text=name, variable=self.mode, value=value, command=lambda v=value: self._set_mode(v), indicatoron=False, anchor="w", padx=10, pady=8, bg=CARD, fg=MUTED, selectcolor=INK, activebackground="#f0eee7", activeforeground=INK, font=("Segoe UI", 10)).pack(fill="x", pady=2)

        self.generated_frame = tk.Frame(panel, bg=CARD)
        self.generated_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(20, 0))
        self._slider(self.generated_frame, "Points", self.point_count, 40, 1000, 10, "points_value")
        seed_frame = tk.Frame(self.generated_frame, bg=CARD)
        seed_frame.pack(fill="x", pady=(0, 13))
        tk.Label(seed_frame, text="Seed", bg=CARD, fg="#55605a", font=("Segoe UI", 9)).pack(side="left")
        tk.Spinbox(seed_frame, textvariable=self.seed, from_=0, to=999999, width=8, relief="flat", bg="#eef4e8", fg=INK, buttonbackground="#d8e8d0", font=("Consolas", 9, "bold")).pack(side="right")
        self._slider(self.generated_frame, "Turns", self.turns, 1, 4, .1, "turns_value")
        self._slider(self.generated_frame, "Noise", self.noise, 0, .35, .01, "noise_value")
        self.label_control = self._slider(self.generated_frame, "Labels", self.label_count, 2, 6, 1, "labels_value")
        self.rings_frame = tk.Frame(self.generated_frame, bg=CARD)
        self._slider(self.rings_frame, "Ring spacing", self.ring_spacing, .05, .22, .01, "ring_spacing_value")

        self.gaussian_help = tk.Label(panel, text="◉  Drag colored handles on the canvas\n    to move cluster centers.", justify="left", bg="#eef4fb", fg="#657ca6", font=("Segoe UI", 9), padx=10, pady=9)
        self.gaussian_reset = tk.Button(panel, text="↺  Reset center positions", command=self.reset_centers, bg=CARD, fg=MUTED, relief="flat", anchor="w", font=("Segoe UI", 9))

        self.paint_frame = tk.Frame(panel, bg=CARD)
        self._slider(self.paint_frame, "Brush size", self.brush_size, 4, 34, 1, "brush_value")
        self._slider(self.paint_frame, "Noise width", self.noise_width, 0, 60, 1, "noise_width_value", suffix=" px")
        tk.Button(self.paint_frame, text="↶  Undo last stroke", command=self.undo, bg=CARD, fg=MUTED, relief="flat", anchor="w", font=("Segoe UI", 9)).pack(fill="x", pady=(0, 6))

        action_frame = tk.Frame(panel, bg=CARD)
        action_frame.grid(row=6, column=0, sticky="ews", padx=24, pady=(18, 18))
        panel.rowconfigure(6, weight=1)
        tk.Button(action_frame, text="✦  Generate dataset", command=self.generate, bg=CORAL, fg="white", relief="flat", anchor="w", padx=12, pady=10, font=("Segoe UI", 10, "bold")).pack(fill="x")
        tk.Button(action_frame, text="Clear board", command=self.clear, bg=CARD, fg=MUTED, relief="flat", anchor="w", padx=0, pady=8, font=("Segoe UI", 9)).pack(fill="x")
        tk.Label(panel, text="Output: points.csv                 2 dimensions", bg=CARD, fg=MUTED, font=("Consolas", 8)).grid(row=7, column=0, sticky="sw", padx=24, pady=(0, 20))

        right = tk.Frame(self, bg=CARD, highlightbackground=LINE, highlightthickness=1)
        right.grid(row=1, column=1, sticky="nsew", padx=(0, 38), pady=(0, 35))
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        heading = tk.Frame(right, bg=CARD)
        heading.grid(row=0, column=0, sticky="ew", padx=24, pady=24)
        self.canvas_title = tk.Label(heading, text="Spiral field", bg=CARD, fg=INK, font=("Segoe UI", 18, "bold"))
        self.canvas_title.pack(side="left")
        tk.Button(heading, text="↓  Export CSV", command=self.export_csv, bg=INK, fg="white", relief="flat", padx=12, pady=7, font=("Segoe UI", 9, "bold")).pack(side="right")
        tk.Button(heading, text="{ }", command=self.export_json, bg="#f0eee7", fg=MUTED, relief="flat", padx=9, pady=7, font=("Consolas", 9)).pack(side="right", padx=(0, 7))

        self.canvas = tk.Canvas(right, bg="#f7f6f1", highlightbackground=LINE, highlightthickness=1, cursor="crosshair")
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=24)
        self.canvas.bind("<Configure>", lambda _: self.draw())
        self.canvas.bind("<ButtonPress-1>", self.pointer_down)
        self.canvas.bind("<B1-Motion>", self.pointer_move)
        self.canvas.bind("<ButtonRelease-1>", self.pointer_up)

        footer = tk.Frame(right, bg=CARD)
        footer.grid(row=2, column=0, sticky="ew", padx=24, pady=15)
        self.legend = tk.Label(footer, text="", bg=CARD, fg=MUTED, font=("Consolas", 9), anchor="w")
        self.legend.pack(side="left")
        self.stats = tk.Label(footer, text="", bg=CARD, fg=INK, font=("Consolas", 9))
        self.stats.pack(side="right")

    def _slider(self, parent, label, variable, minimum, maximum, step, value_name, suffix=""):
        frame = tk.Frame(parent, bg=CARD)
        frame.pack(fill="x", pady=(0, 13))
        top = tk.Frame(frame, bg=CARD)
        top.pack(fill="x")
        tk.Label(top, text=label, bg=CARD, fg="#55605a", font=("Segoe UI", 9)).pack(side="left")
        value_label = tk.Label(top, bg="#eef4e8", fg=INK, padx=6, font=("Consolas", 9, "bold"))
        value_label.pack(side="right")
        def update(*_):
            value = variable.get()
            value_label.config(text=f"{value:g}{suffix}")
            if label in ("Brush size", "Noise width") and hasattr(self, "canvas"):
                self.draw()
        variable.trace_add("write", update)
        update()
        tk.Scale(
            frame,
            variable=variable,
            from_=minimum,
            to=maximum,
            resolution=step,
            orient="horizontal",
            showvalue=False,
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=CORAL,
            bd=0,
            bg="#eef1ea",
            troughcolor="#cbd5c8",
            activebackground=CORAL,
            sliderrelief="raised",
            sliderlength=18,
            width=13,
            command=lambda _: update(),
        ).pack(fill="x", pady=(4, 0))
        return frame

    @staticmethod
    def _normal():
        return random.gauss(0, 1)

    @staticmethod
    def _clamp(value, minimum=0, maximum=1):
        return max(minimum, min(maximum, value))

    def default_centers(self):
        count = self.label_count.get()
        return [{"x": .5 + math.cos(index / count * math.tau - math.pi / 2) * .27, "y": .5 + math.sin(index / count * math.tau - math.pi / 2) * .27} for index in range(count)]

    def make_spiral(self):
        count = self.point_count.get()
        labels = self.label_count.get()
        per_label = math.ceil(count / labels)
        points = []
        for index in range(count):
            label = index % labels
            progress = (index // labels) / max(1, per_label - 1)
            angle = progress * math.tau * self.turns.get() + label * math.tau / labels
            radius = .05 + progress * .41
            points.append({"x": .5 + math.cos(angle) * radius + self._normal() * self.noise.get() * .16, "y": .5 + math.sin(angle) * radius + self._normal() * self.noise.get() * .16, "label": label})
        return points

    def make_blobs(self):
        if len(self.gaussian_centers) != self.label_count.get():
            self.gaussian_centers = self.default_centers()
        points = []
        for index in range(self.point_count.get()):
            label = index % self.label_count.get()
            center = self.gaussian_centers[label]
            points.append({"x": center["x"] + self._normal() * self.noise.get() * .58, "y": center["y"] + self._normal() * self.noise.get() * .58, "label": label})
        return points

    def make_rings(self):
        points = []
        ring_count = self.label_count.get()
        for index in range(self.point_count.get()):
            label = index % ring_count
            angle = random.random() * math.tau
            radius = .08 + label * self.ring_spacing.get()
            radius += self._normal() * self.noise.get() * .2
            points.append({"x": .5 + math.cos(angle) * radius, "y": .5 + math.sin(angle) * radius, "label": label})
        return points

    def make_moons(self):
        points = []
        for index in range(self.point_count.get()):
            label = index % 2
            angle = random.random() * math.pi
            x = .32 + math.cos(angle) * .22 if label == 0 else .68 - math.cos(angle) * .22
            y = .48 + math.sin(angle) * .2 if label == 0 else .52 - math.sin(angle) * .2
            points.append({"x": x + self._normal() * self.noise.get() * .45, "y": y + self._normal() * self.noise.get() * .45, "label": label})
        return points

    def generate(self):
        if self.mode.get() == "paint":
            return
        random.seed(self.seed.get())
        self.data = self.make_spiral() if self.mode.get() == "spiral" else self.make_blobs() if self.mode.get() == "blobs" else self.make_rings() if self.mode.get() == "rings" else self.make_moons()
        self.strokes = []
        self.draw()
        self.update_stats()

    def _set_mode(self, mode):
        self.mode.set(mode)
        self.generated_frame.grid() if mode != "paint" else self.generated_frame.grid_remove()
        self.label_control.grid_remove() if mode == "moons" else self.label_control.grid()
        self.rings_frame.grid() if mode == "rings" else self.rings_frame.grid_remove()
        self.paint_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(20, 0)) if mode == "paint" else self.paint_frame.grid_remove()
        if mode == "blobs":
            self.gaussian_help.grid(row=4, column=0, sticky="ew", padx=24, pady=(12, 0))
            self.gaussian_reset.grid(row=5, column=0, sticky="ew", padx=24, pady=(6, 0))
        else:
            self.gaussian_help.grid_remove()
            self.gaussian_reset.grid_remove()
        self.canvas_title.config(text="Freeform field" if mode == "paint" else "Gaussian field" if mode == "blobs" else "Concentric field" if mode == "rings" else "Two moons field" if mode == "moons" else "Spiral field")
        if mode == "paint":
            self.data, self.strokes = [], []
            self.draw()
            self.update_stats()
        else:
            self.generate()

    def point_from_event(self, event):
        width, height = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        return {"x": float(self._clamp(event.x / width)), "y": float(self._clamp(event.y / height))}

    def center_at(self, position):
        width, height = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        for index, center in enumerate(self.gaussian_centers):
            if math.hypot((center["x"] - position["x"]) * width, (center["y"] - position["y"]) * height) < 18:
                return index
        return None

    def paint_dab(self, position, label):
        points = [{**position, "label": label}]
        width = self.noise_width.get()
        if width:
            canvas_width = max(1, self.canvas.winfo_width())
            canvas_height = max(1, self.canvas.winfo_height())
            for _ in range(8):
                points.append({"x": self._clamp(position["x"] + self._normal() * width / canvas_width / 2.5), "y": self._clamp(position["y"] + self._normal() * width / canvas_height / 2.5), "label": label})
        self.data.extend(points)
        return points

    def pointer_down(self, event):
        position = self.point_from_event(event)
        if self.mode.get() == "blobs":
            self.active_center_index = self.center_at(position)
            return
        if self.mode.get() != "paint":
            return
        self.active_stroke = []
        self.active_path_point = position
        self.active_stroke.extend(self.paint_dab(position, len(self.strokes)))
        self.draw()
        self.update_stats()

    def pointer_move(self, event):
        position = self.point_from_event(event)
        if self.mode.get() == "blobs" and self.active_center_index is not None:
            self.gaussian_centers[self.active_center_index] = position
            self.data = self.make_blobs()
            self.draw()
            return
        if self.mode.get() != "paint" or self.active_stroke is None or self.active_path_point is None:
            return
        if math.hypot(position["x"] - self.active_path_point["x"], position["y"] - self.active_path_point["y"]) < .006:
            return
        self.active_path_point = position
        self.active_stroke.extend(self.paint_dab(position, len(self.strokes)))
        self.draw()
        self.update_stats()

    def pointer_up(self, _event):
        if self.active_stroke:
            self.strokes.append(self.active_stroke)
        self.active_stroke = None
        self.active_path_point = None
        self.active_center_index = None

    def draw(self):
        self.canvas.delete("all")
        width, height = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        for x in range(0, width, 32):
            self.canvas.create_line(x, 0, x, height, fill="#e8ebe2")
        for y in range(0, height, 32):
            self.canvas.create_line(0, y, width, y, fill="#e8ebe2")
        radius = self.brush_size.get() / 2 if self.mode.get() == "paint" else 3.5
        for point in self.data:
            x, y = point["x"] * width, point["y"] * height
            color = COLORS[point["label"] % len(COLORS)]
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="")
        if self.mode.get() == "blobs":
            for index, center in enumerate(self.gaussian_centers):
                x, y = center["x"] * width, center["y"] * height
                color = COLORS[index % len(COLORS)]
                self.canvas.create_oval(x - 9, y - 9, x + 9, y + 9, fill=color, outline="")
                self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=CARD, outline="")

    def update_stats(self):
        labels = sorted({point["label"] for point in self.data})
        self.stats.config(text=f"{len(self.data)} points    {len(labels)} labels")
        self.legend.config(text="   ".join(f"● label {label}" for label in labels), fg=COLORS[labels[0] % len(COLORS)] if labels else MUTED)

    def reset_centers(self):
        self.gaussian_centers = self.default_centers()
        self.generate()

    def clear(self):
        self.data, self.strokes = [], []
        self.draw()
        self.update_stats()

    def undo(self):
        if self.strokes:
            removed = self.strokes.pop()
            del self.data[-len(removed):]
            self.draw()
            self.update_stats()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="points.csv", filetypes=(("CSV files", "*.csv"),))
        if not path:
            return
        with Path(path).open("w", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(("x1", "x2", "label"))
            writer.writerows((f"{point['x']:.5f}", f"{point['y']:.5f}", point["label"]) for point in self.data)
        messagebox.showinfo("Export complete", f"Saved {len(self.data)} points.")

    def export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", initialfile="points.json", filetypes=(("JSON files", "*.json"),))
        if not path:
            return
        Path(path).write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        messagebox.showinfo("Export complete", f"Saved {len(self.data)} points.")


if __name__ == "__main__":
    ClusterCanvas().mainloop()
