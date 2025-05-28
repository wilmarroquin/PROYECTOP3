import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font
import re
import cv2  # Importar OpenCV
import os   # Para manejar rutas
import time # Para generar nombres únicos
import threading
from PIL import Image, ImageTk  # Para mostrar la vista previa
from Registro import *
from Conexion import *
from Carnet import crear_carnet
from Correo import enviar_correo
from whatsapp import enviar_whatsapp
from IngresoPuerta import IngresoPrincipal

class Formulario:

    def __init__(self):
        self.base = tk.Tk()
        self.base.geometry("1080x520")
        self.base.title("Sistema de Registro UMG")
        self.base.configure(bg="#60bb5d")
        
        
        
        # Crear carpeta para fotografías si no existe
        self.fotos_dir = os.path.join(os.getcwd(), 'fotografias')
        os.makedirs(self.fotos_dir, exist_ok=True)
        
        self.crear_estilos()
        self.crear_widgets()
        self.base.mainloop()

    def crear_estilos(self):
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')
        
        self.fuente_titulo = Font(family="Arial", size=14, weight="bold")
        self.fuente_normal = Font(family="Arial", size=11)
        
        self.estilo.configure('TFrame', background='#f0f0f0')
        self.estilo.configure('TLabel', font=self.fuente_normal, background='#f0f0f0')
        self.estilo.configure('TButton', font=self.fuente_normal, padding=5)
        self.estilo.configure('TCombobox', font=self.fuente_normal, padding=5)

    def crear_widgets(self):
        group_box = ttk.LabelFrame(self.base, text="Datos del Estudiante", padding=(20, 10))
        group_box.pack(padx=30, pady=30, fill='both', expand=True)

        # Sección izquierda
        frame_izq = ttk.Frame(group_box)
        frame_izq.grid(row=0, column=0, padx=20, pady=10, sticky='nsew')

        campos = [
            ("Carnet:", 0),
            ("Nombres:", 1),
            ("Apellidos:", 2),
            ("Teléfono:", 3)
        ]
        
        self.entries = {}
        for texto, fila in campos:
            lbl = ttk.Label(frame_izq, text=texto)
            lbl.grid(row=fila, column=0, pady=5, sticky='w')
            entry = ttk.Entry(frame_izq, width=30)
            entry.grid(row=fila, column=1, pady=5, padx=10)
            self.entries[texto.strip(':')] = entry

        # Sección derecha
        frame_der = ttk.Frame(group_box)
        frame_der.grid(row=0, column=1, padx=20, pady=10, sticky='nsew')

        opciones = [
            ("Correo:", "correo", 0),
            ("Fotografía:", "foto", 1),
            ("Tipo de persona:", "tipo_persona", 2, ["Estudiante", "Catedrático", "Administrativo", "No aplica"]),
            ("Carreras:", "carrera", 3, ["Ingeniería en Sistemas", "Administración", "Psicología", "No aplica"]),
            ("Sección:", "seccion", 4, ["A", "B", "C", "No aplica"])
        ]


        self.comboboxes = {}
        for item in opciones:
            lbl = ttk.Label(frame_der, text=item[0])
            lbl.grid(row=item[2], column=0, pady=5, sticky='w')
            
            if len(item) > 3:
                var = tk.StringVar()
                combo = ttk.Combobox(frame_der, textvariable=var, values=item[3], width=27)
                combo.grid(row=item[2], column=1, pady=5, padx=10)
                self.comboboxes[item[1]] = combo
            else:
                entry = ttk.Entry(frame_der, width=30)
                entry.grid(row=item[2], column=1, pady=5, padx=10)
                self.entries[item[1]] = entry

        # Botones para fotografía

        boton_frame = ttk.Frame(frame_der)
        boton_frame.grid(row=5, column=1, columnspan=2, pady=5, sticky='w')

        ttk.Button(boton_frame, text="Tomar Foto", command=self.capturar_foto).pack(side='left', padx=5)
        ttk.Button(boton_frame, text="Firmar", command=self.abrir_ventana_firma).pack(side='left', padx=5)

        # Botones inferiores
        frame_botones = ttk.Frame(group_box)
        frame_botones.grid(row=1, column=0, columnspan=2, pady=20)
        
        ttk.Button(frame_botones, text="Guardar", command=self.guardar_datos).pack(side='left', padx=10)
        ttk.Button(frame_botones, text="Limpiar", command=self.limpiar_formulario).pack(side='left', padx=10)
        ttk.Button(frame_botones, text="Tomar Asistencia", command=self.iniciar_asistencia).pack(side='left', padx=10)


        group_box.grid_columnconfigure(0, weight=1)
        group_box.grid_columnconfigure(1, weight=1)

    def seleccionar_foto(self):
        archivo = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png *.jpeg")])
        if archivo:
            self.entries['foto'].delete(0, tk.END)
            self.entries['foto'].insert(0, archivo)

    def capturar_foto(self):
        self.preview_window = tk.Toplevel(self.base)
        self.preview_window.title("Tomar Foto")
        
        self.video_label = ttk.Label(self.preview_window)
        self.video_label.pack()
        
        btn_frame = ttk.Frame(self.preview_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Capturar", command=self.capturar_imagen).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.cerrar_preview).pack(side='left', padx=10)
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se puede acceder a la cámara")
            self.preview_window.destroy()
            return
        
        self.actualizar_preview()

    def actualizar_preview(self):
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.preview_window.after(10, self.actualizar_preview)

    def capturar_imagen(self):
        ret, frame = self.cap.read()
        if ret:
            carnet = self.entries['Carnet'].get().strip()
            if carnet:
                filename = f"{carnet}.jpg"
            else:
                filename = f"foto_{int(time.time())}.jpg"
            
            # Guardar en la carpeta fotografias
            save_path = os.path.join(self.fotos_dir, filename)
            
            cv2.imwrite(save_path, frame)
            self.entries['foto'].delete(0, tk.END)
            self.entries['foto'].insert(0, save_path)
            messagebox.showinfo("Éxito", f"Foto guardada en:\n{save_path}")
            self.cerrar_preview()

    def cerrar_preview(self):
        if hasattr(self, 'cap'):
            self.cap.release()
        if hasattr(self, 'preview_window'):
            self.preview_window.destroy()

    def guardar_datos(self):
        try:
            datos = {
            'carnet': int(self.entries['Carnet'].get().strip()),
            'nombres': self.entries['Nombres'].get().strip(),
            'apellidos': self.entries['Apellidos'].get().strip(),
            'telefono': self.entries['Teléfono'].get().strip(),
            'correo': self.entries['correo'].get().strip(),
            'foto': self.entries['foto'].get().strip(),
            'tipo_persona': self.comboboxes['tipo_persona'].get(),
            'carrera': self.comboboxes['carrera'].get(),
            'seccion': self.comboboxes['seccion'].get()
            }

            if not all([datos['carnet'], datos['nombres'], datos['apellidos']]):
                messagebox.showerror("Error", "Carnet, Nombres y Apellidos son obligatorios")
                return
        
            if not datos['foto']:
                messagebox.showerror("Error", "Debe seleccionar o tomar una fotografía")
                return
        
            id_tipo_persona = self.obtener_id_tipo_persona(datos['tipo_persona'])
            id_carrera = self.obtener_id_carrera(datos['carrera'])
            id_seccion = self.obtener_id_seccion(datos['seccion'])

            exito = Registro.registrousuarios(
                carnet=datos['carnet'],
                nombre=datos['nombres'],
                apellido=datos['apellidos'],
                telefono=datos['telefono'],
                correo_umg=datos['correo'],
                fotografia=datos['foto'],
                id_tipo_persona=id_tipo_persona,
                id_carrera=id_carrera,
                id_seccion=id_seccion
            )

            if exito:
                messagebox.showinfo("Éxito", "Datos guardados en la base de datos")

                ruta_carnet_pdf = crear_carnet(
                    datos['nombres'],
                    datos['apellidos'],
                    datos['carrera'],
                    datos['carnet'],
                    datos['foto']
                    )
                self.limpiar_formulario()
                enviar_correo(datos['correo'], f"{datos['nombres']} {datos['apellidos']}", str(datos['carnet']), ruta_carnet_pdf)
                enviar_whatsapp(datos['telefono'], f"{datos['nombres']} {datos['apellidos']}", ruta_carnet_pdf)

            else:
                messagebox.showerror("Error", "No se pudo guardar en la base de datos")
        except Exception as e:
                messagebox.showerror("Error crítico", f"Error inesperado: {str(e)}")

    def limpiar_formulario(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for combo in self.comboboxes.values():
            combo.set('')

    def obtener_id_tipo_persona(self, tipo):
        tipos = {
            "Estudiante": 1,
            "Catedrático": 2,
            "Administrativo": 3,
            "No aplica": 4
            }
        return tipos.get(tipo, 1)

    def obtener_id_carrera(self, carrera):
        carreras = {
        "Ingeniería en Sistemas": 1,
        "Administración": 2,
        "Psicología": 3,
        "No aplica": 4,
        }
        return carreras.get(carrera, 1)
    
    def obtener_id_seccion(self, seccion):
        secciones = {
            "A": 1,
            "B": 2,
            "C": 3,
            "No Aplica": 4,
        }
        return secciones.get(seccion, 1)
    
    def iniciar_asistencia(self):
        hilo = threading.Thread(target=self.ejecutar_asistencia)
        hilo.daemon = True
        hilo.start()

    def ejecutar_asistencia(self):
        try:
            from IngresoPuerta import IngresoPrincipal
            ingreso = IngresoPrincipal(fotos_dir=self.fotos_dir)
            ingreso.iniciar_video()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la toma de asistencia:\n{str(e)}")
    
    def abrir_ventana_firma(self):
        from Firma import VentanaFirma
        carnet = self.entries['Carnet'].get().strip()
        if not carnet:
            messagebox.showerror("Error", "Debe ingresar el número de carnet antes de firmar.")
            return
        VentanaFirma(carnet)

if __name__ == "__main__":
    app = Formulario()