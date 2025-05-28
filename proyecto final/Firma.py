import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import os
import time

class VentanaFirma:

    def __init__(self, carnet):
        self.carnet = carnet
        self.carpeta_guardado = os.path.join(os.getcwd(), "firma")
        os.makedirs(self.carpeta_guardado, exist_ok=True)

        self.ancho = 600
        self.alto = 300

        self.ventana = tk.Toplevel()
        self.ventana.title("Firma Digital")
        self.ventana.geometry(f"{self.ancho}x{self.alto + 60}")
        self.ventana.configure(bg="white")

        self.canvas = tk.Canvas(self.ventana, bg="white", width=self.ancho, height=self.alto)
        self.canvas.pack(pady=10)

        self.image = Image.new("RGB", (self.ancho, self.alto), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.canvas.bind("<B1-Motion>", self.dibujar)

        btn_frame = tk.Frame(self.ventana, bg="white")
        btn_frame.pack()

        tk.Button(btn_frame, text="Guardar Firma", command=self.guardar_firma).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Limpiar", command=self.limpiar_canvas).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancelar", command=self.ventana.destroy).pack(side=tk.LEFT, padx=10)

        self.ruta_guardada = None

    def dibujar(self, event):
        x, y = event.x, event.y
        r = 2
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="black")
        self.draw.ellipse((x - r, y - r, x + r, y + r), fill="black")

    def limpiar_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.ancho, self.alto), "white")
        self.draw = ImageDraw.Draw(self.image)

    def guardar_firma(self):
        ruta = os.path.join(self.carpeta_guardado, f"firma_{self.carnet}.png")
        self.image.save(ruta)
        self.ruta_guardada = ruta
        messagebox.showinfo("Firma guardada", f"Firma guardada en:\n{ruta}")
        self.ventana.destroy()
