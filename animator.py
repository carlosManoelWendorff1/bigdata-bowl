import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import math

CANVAS_WIDTH = 960
CANVAS_HEIGHT = 400
FIELD_X_YARDS = 120
FIELD_Y_YARDS = 53.3

class NFLTeamBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NFL Team Animation")

        self.frames = {}
        self.create_pages()
        self.show_frame("main")

        self.tracking_data_by_frame = {}
        self.animation_frame_ids = []
        self.current_frame_index = 0
        self.is_playing = False
        self.playback_speed_ms = 100

    def create_pages(self):
        main_frame = tk.Frame(self.root)
        self.frames["main"] = main_frame

        tk.Button(main_frame, text="Load Parquet and Animate", command=self.load_from_parquet).pack(pady=20)
        tk.Button(main_frame, text="Exit", command=self.root.quit).pack()

        output_frame = tk.Frame(self.root)
        self.frames["output"] = output_frame

        self.canvas = tk.Canvas(output_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="darkgreen")
        self.canvas.pack(padx=10, pady=10)

        self.output_label = tk.Label(output_frame, text="", font=("Arial", 12), fg="white", bg="darkgreen")
        self.output_label.pack()

        btn_frame = tk.Frame(output_frame)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="▶ Play", command=self.start_animation).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏸ Pause", command=self.pause_animation).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏮ Prev", command=self.step_back).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏭ Next", command=self.step_forward).pack(side="left", padx=5)
        tk.Button(output_frame, text="Back", command=lambda: self.show_frame("main")).pack()

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    def load_from_parquet(self):
        file_path = filedialog.askopenfilename(
            title="Select Parquet File",
            filetypes=[("Parquet Files", "*.parquet"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            df = pd.read_parquet(file_path)

            required = {'displayName', 'club', 'x', 'y', 'a', 'dir', 'frameId', 'playId', 's'}
            if not required.issubset(df.columns):
                raise ValueError(f"Missing required columns: {required - set(df.columns)}")

            df = df.dropna(subset=['playId', 'frameId', 'x', 'y'])
            df = df.sort_values(by=['playId', 'frameId'])
            df['frameGlobalId'] = df.groupby(['playId', 'frameId']).ngroup()

            self.tracking_data_by_frame = {
                int(fid): group.to_dict('records')
                for fid, group in df.groupby('frameGlobalId')
            }

            self.animation_frame_ids = sorted(self.tracking_data_by_frame.keys())
            self.current_frame_index = 0

            self.show_frame("output")
            self.draw_current_frame()

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load parquet file:\n{e}")

    def start_animation(self):
        if not self.animation_frame_ids:
            return
        self.is_playing = True
        self.animate_next_frame()

    def pause_animation(self):
        self.is_playing = False

    def step_forward(self):
        self.is_playing = False
        if self.current_frame_index < len(self.animation_frame_ids) - 1:
            self.current_frame_index += 1
            self.draw_current_frame()

    def step_back(self):
        self.is_playing = False
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.draw_current_frame()

    def animate_next_frame(self):
        if not self.is_playing:
            return
        if self.current_frame_index >= len(self.animation_frame_ids):
            self.output_label.config(text="Animation finished.")
            self.is_playing = False
            return

        self.draw_current_frame()
        self.current_frame_index += 1
        self.root.after(self.playback_speed_ms, self.animate_next_frame)

    def draw_current_frame(self):
        frame_id = self.animation_frame_ids[self.current_frame_index]
        frame_data = self.tracking_data_by_frame[frame_id]

        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="darkgreen")

        for i in range(0, 121, 10):
            x = i / FIELD_X_YARDS * CANVAS_WIDTH
            self.canvas.create_line(x, 0, x, CANVAS_HEIGHT, fill="white", dash=(4, 2))
            self.canvas.create_text(x + 2, 10, text=str(i), fill="white", anchor="nw")

        first_team = frame_data[0]['club'] if frame_data else ''

        for player in frame_data:
            try:
                name = player['displayName']
                club = player['club']
                x = float(player['x'])
                y = float(player['y'])
                speed = float(player.get('s', 0))
                direction = float(player.get('dir', 0))

                if not (0 <= x <= 120 and 0 <= y <= 53.3):
                    continue

                canvas_x = (x / FIELD_X_YARDS) * CANVAS_WIDTH
                canvas_y = (y / FIELD_Y_YARDS) * CANVAS_HEIGHT

                if name.lower() == 'football':
                    self.canvas.create_oval(canvas_x - 5, canvas_y - 5,
                                            canvas_x + 5, canvas_y + 5,
                                            fill="pink", outline="black")
                    continue

                color = "red" if club == first_team else "blue"

                self.canvas.create_oval(canvas_x - 8, canvas_y - 8,
                                        canvas_x + 8, canvas_y + 8, fill=color)
                self.canvas.create_text(canvas_x, canvas_y - 12, text=name, fill="white", font=("Arial", 7), anchor="s")

                angle_rad = math.radians(direction)
                dx = math.cos(angle_rad) * speed * 0.5
                dy = -math.sin(angle_rad) * speed * 0.5

                self.canvas.create_line(canvas_x, canvas_y, canvas_x + dx, canvas_y + dy,
                                        fill="yellow", arrow=tk.LAST, width=2)
            except Exception as e:
                print(f"Error drawing player: {e}")

        self.output_label.config(text=f"Frame: {frame_id}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NFLTeamBuilderApp(root)
    root.mainloop()
