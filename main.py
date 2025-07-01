import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import threading
import math

# Canvas size
CANVAS_WIDTH = 960
CANVAS_HEIGHT = 400

# Field dimensions in yards
FIELD_X_YARDS = 120
FIELD_Y_YARDS = 53.3

class NFLTeamBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NFL Team Builder")
        self.speed_var = tk.StringVar()
        self.dir_var = tk.StringVar()
        self.ball_x_var = tk.StringVar()
        self.ball_y_var = tk.StringVar()
        self.ball_speed_var = tk.StringVar()
        self.ball_dir_var = tk.StringVar()
        self.ball_data = None  # guarda os dados da bola

        self.data = {
            "team_a": [],
            "team_b": [],
            "extra": ""
        }

        self.frames = {}
        self.create_pages()
        self.show_frame("main")

    def create_pages(self):
        # Página principal
        main_frame = tk.Frame(self.root)
        self.frames["main"] = main_frame

        self.name_var = tk.StringVar()
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.extra_info_var = tk.StringVar()

        input_frame = tk.Frame(main_frame)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Player Name:").grid(row=0, column=0)
        tk.Entry(input_frame, textvariable=self.name_var, width=15).grid(row=0, column=1)

        tk.Label(input_frame, text="X:").grid(row=0, column=2)
        tk.Entry(input_frame, textvariable=self.x_var, width=5).grid(row=0, column=3)

        tk.Label(input_frame, text="Y:").grid(row=0, column=4)
        tk.Entry(input_frame, textvariable=self.y_var, width=5).grid(row=0, column=5)

        tk.Label(input_frame, text="Acceleration (yd/s²):").grid(row=1, column=0)
        tk.Entry(input_frame, textvariable=self.speed_var, width=10).grid(row=1, column=1)

        tk.Label(input_frame, text="Orientation (° 0–360):").grid(row=1, column=2)
        tk.Entry(input_frame, textvariable=self.dir_var, width=12).grid(row=1, column=3)

        tk.Button(input_frame, text="Add to Team A", command=self.add_to_team_a).grid(row=0, column=6, padx=5)
        tk.Button(input_frame, text="Add to Team B", command=self.add_to_team_b).grid(row=0, column=7, padx=5)

        # Grids
        grid_frame = tk.Frame(main_frame)
        grid_frame.pack(pady=10)

        team_a_frame, self.team_a_tree = self.create_treeview(grid_frame, "Team A")
        team_a_frame.grid(row=0, column=0, padx=10)

        team_b_frame, self.team_b_tree = self.create_treeview(grid_frame, "Team B")
        team_b_frame.grid(row=0, column=1, padx=10)

        # Extra Info + Ball
        info_frame = tk.Frame(main_frame)
        info_frame.pack(pady=10)

        # Extra Info
        tk.Label(info_frame, text="Extra Information:").grid(row=0, column=0, sticky="w", columnspan=6)
        tk.Entry(info_frame, textvariable=self.extra_info_var, width=50).grid(row=1, column=0, columnspan=6, pady=(0, 10))

        # Ball Info
        tk.Label(info_frame, text="Ball Position and Motion", font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=6, pady=(5, 5))

        tk.Label(info_frame, text="X (0–120 yd):").grid(row=3, column=0)
        tk.Entry(info_frame, textvariable=self.ball_x_var, width=10).grid(row=3, column=1)

        tk.Label(info_frame, text="Y (0–53.3 yd):").grid(row=3, column=2)
        tk.Entry(info_frame, textvariable=self.ball_y_var, width=10).grid(row=3, column=3)

        tk.Label(info_frame, text="Acceleration (yd/s²):").grid(row=4, column=0)
        tk.Entry(info_frame, textvariable=self.ball_speed_var, width=10).grid(row=4, column=1)

        tk.Label(info_frame, text="Orientation (° 0–360):").grid(row=4, column=2)
        tk.Entry(info_frame, textvariable=self.ball_dir_var, width=10).grid(row=4, column=3)

        # Generate Button
        tk.Button(info_frame, text="Generate Output", command=self.generate_output).grid(row=5, column=0, columnspan=6, pady=10)

        # Página de visualização
        output_frame = tk.Frame(self.root)
        self.frames["output"] = output_frame

        self.canvas = tk.Canvas(output_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="darkgreen")
        self.canvas.pack(padx=10, pady=10)

        self.output_label = tk.Label(output_frame, text="", font=("Arial", 12), fg="white", bg="darkgreen")
        self.output_label.pack()

        tk.Button(output_frame, text="Back", command=lambda: self.show_frame("main")).pack()

    def create_treeview(self, parent, team_name):
        frame = tk.Frame(parent)
        tk.Label(frame, text=team_name, font=("Arial", 12, "bold")).pack()

        columns = ("name", "x", "y", "speed", "direction")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)

        tree.heading("name", text="Player Name")
        tree.heading("x", text="X")
        tree.heading("y", text="Y")
        tree.heading("speed", text="Acceleration")
        tree.heading("direction", text="Orientation (°)")

        tree.column("name", width=120)
        tree.column("x", width=50, anchor="center")
        tree.column("y", width=50, anchor="center")
        tree.column("speed", width=60, anchor="center")
        tree.column("direction", width=80, anchor="center")

        tree.pack()
        return frame, tree

    def add_player(self, tree):
        name = self.name_var.get().strip()
        x = self.x_var.get().strip()
        y = self.y_var.get().strip()
        speed = self.speed_var.get().strip()
        direction = self.dir_var.get().strip()

        if not name or not x or not y or not speed or not direction:
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            x_val = float(x)
            y_val = float(y)
            speed_val = float(speed)
            direction_val = float(direction)
        except ValueError:
            messagebox.showerror("Invalid Input", "X, Y, Speed, and Direction must be numbers.")
            return

        tree.insert("", "end", values=(name, x_val, y_val, speed_val, direction_val))

        self.name_var.set("")
        self.x_var.set("")
        self.y_var.set("")
        self.speed_var.set("")
        self.dir_var.set("")

    def add_to_team_a(self):
        self.add_player(self.team_a_tree)

    def add_to_team_b(self):
        self.add_player(self.team_b_tree)

    def get_tree_data(self, tree):
        return [tree.item(child)["values"] for child in tree.get_children()]

    def _generate_with_delay(self):
        time.sleep(1)  # Simula uma operação demorada
        self.root.after(0, self.draw_field)  # Atualiza o campo na thread principal

    def generate_output(self):
        self.data["team_a"] = self.get_tree_data(self.team_a_tree)
        self.data["team_b"] = self.get_tree_data(self.team_b_tree)
        self.data["extra"] = self.extra_info_var.get()

        # Tenta atualizar os dados da bola automaticamente
        try:
            x = float(self.ball_x_var.get())
            y = float(self.ball_y_var.get())
            speed = float(self.ball_speed_var.get())
            direction = float(self.ball_dir_var.get())

            if not (0 <= x <= 120 and 0 <= y <= 53.3 and 0 <= direction <= 360):
                raise ValueError("Ball values out of bounds")

            self.ball_data = (x, y, speed, direction)
        except Exception as e:
            self.ball_data = None  # não desenha bola se der erro
            messagebox.showerror("Ball Input Error", f"Ball data invalid or missing:\n{e}")

        # Mostra tela de carregamento
        self.show_frame("output")
        self.canvas.delete("all")
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                                text="Generating field...", fill="white", font=("Arial", 18))
        self.output_label.config(text="")

        # Simula requisição demorada com delay
        threading.Thread(target=self._generate_with_delay).start()

    def draw_field(self):
        self.canvas.delete("all")

        # Campo
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="darkgreen")

        # Linhas de jarda ao longo do campo
        for i in range(0, 121, 10):  # de 0 a 120 em passos de 10
            x = i / FIELD_X_YARDS * CANVAS_WIDTH
            self.canvas.create_line(x, 0, x, CANVAS_HEIGHT, fill="white", dash=(4, 2))
            self.canvas.create_text(x + 2, 10, text=str(i), fill="white", anchor="nw")

        # Jogadores
        for player in self.data["team_a"]:
            self.draw_player(player, "red")

        for player in self.data["team_b"]:
            self.draw_player(player, "blue")

        if self.ball_data:
            self.draw_ball(*self.ball_data)

        self.output_label.config(text=self.data["extra"] or "[No extra info]")

    
    def draw_ball(self, x, y, speed, direction):
        # Converte coordenadas da bola para canvas
        canvas_x = (x / FIELD_X_YARDS) * CANVAS_WIDTH
        canvas_y = (y / FIELD_Y_YARDS) * CANVAS_HEIGHT

        radius = 6
        self.canvas.create_oval(canvas_x - radius, canvas_y - radius,
                                canvas_x + radius, canvas_y + radius,
                                fill="saddlebrown", outline="black")

        # Desenha direção da bola como uma seta
        angle_rad = math.radians(direction)
        dx = math.cos(angle_rad) * speed * 2
        dy = -math.sin(angle_rad) * speed * 2  # Inverter Y

        end_x = canvas_x + dx
        end_y = canvas_y + dy

        self.canvas.create_line(canvas_x, canvas_y, end_x, end_y,
                                fill="white", arrow=tk.LAST, width=2)

    def draw_player(self, player, color):
        try:
            name, x, y, speed, direction = player
            x = float(x)
            y = float(y)
            speed = float(speed)
            direction = float(direction)

            # Conversão para pixels
            canvas_x = (x / FIELD_X_YARDS) * CANVAS_WIDTH
            canvas_y = (y / FIELD_Y_YARDS) * CANVAS_HEIGHT

            radius = 8
            self.canvas.create_oval(canvas_x - radius, canvas_y - radius,
                                    canvas_x + radius, canvas_y + radius,
                                    fill=color)
            self.canvas.create_text(canvas_x, canvas_y - 12, text=name, fill="white", font=("Arial", 8), anchor="s")

            # Seta de direção
            angle_rad = math.radians(direction)
            dx = math.cos(angle_rad) * speed * 2
            dy = -math.sin(angle_rad) * speed * 2  # inverter Y

            end_x = canvas_x + dx
            end_y = canvas_y + dy

            self.canvas.create_line(canvas_x, canvas_y, end_x, end_y, fill="yellow", arrow=tk.LAST, width=2)
        except Exception as e:
            print(f"Error drawing player: {player} -> {e}")

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = NFLTeamBuilderApp(root)
    root.mainloop()
