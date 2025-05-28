import os
import cv2
import numpy as np
import datetime
import mysql.connector
from PIL import Image
import face_recognition
from Conexion import CConexion
import tkinter as tk
from tkinter import filedialog, messagebox

class IngresoPrincipal:
    def __init__(self, fotos_dir="fotografias"):
        self.fotos_dir = fotos_dir
        self.rostros_codificados = []
        self.carnets = []
        self.cargar_rostros()
        self.entries = {}

    def cargar_rostros(self):
        for filename in os.listdir(self.fotos_dir):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(self.fotos_dir, filename)
                try:
                    if os.path.getsize(path) == 0:
                        print(f"[ADVERTENCIA] Imagen vacía: {filename}")
                        continue

                    img = Image.open(path).convert('RGB')
                    img_np = np.array(img)

                    # Detectar ubicaciones de rostro
                    locs = face_recognition.face_locations(img_np)
                    if not locs:
                        print(f"[ADVERTENCIA] No se detectó rostro en: {filename}")
                        continue

                    # Codificar el rostro encontrado
                    encoding = face_recognition.face_encodings(img_np, known_face_locations=locs)
                    if encoding:
                        self.rostros_codificados.append(encoding[0])
                        self.carnets.append(os.path.splitext(filename)[0])
                        print(f"[OK] Rostro cargado: {filename}")
                    else:
                        print(f"[ADVERTENCIA] Falló la codificación del rostro en: {filename}")
                except Exception as e:
                    print(f"[ERROR] No se pudo procesar {filename}: {str(e)}")

    def registrar_ingreso(self, carnet):
        conexion = None
        cursor = None

        try:
            conexion = CConexion.ConexionDB()
            cursor = conexion.cursor()
            ahora = datetime.datetime.now()
            hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

            consulta = """
                SELECT COUNT(*) FROM asistencias 
                WHERE carnet = %s AND fecha_hora BETWEEN %s AND %s
            """
            cursor.execute(consulta, (carnet, hoy_inicio, hoy_fin))
            cantidad = cursor.fetchone()[0]

            if cantidad == 0:
                sql = "INSERT INTO asistencias (carnet, fecha_hora) VALUES (%s, %s)"
                cursor.execute(sql, (carnet, ahora))
                conexion.commit()
                print(f"[OK] Asistencia registrada para {carnet} a las {ahora}")
            else:
                print(f"[INFO] {carnet} ya tiene asistencia registrada hoy.")

        except Exception as e:
            print(f"[ERROR] No se pudo registrar asistencia: {e}")

        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def seleccionar_foto(self):
        archivo = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png *.jpeg")])
        if archivo:
            img_check = cv2.imread(archivo)
            if img_check is None:
                messagebox.showerror("Error", "La imagen seleccionada no se puede leer. Verifica el archivo.")
                return
            self.entries['foto'].delete(0, tk.END)
            self.entries['foto'].insert(0, archivo)

    def iniciar_video(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error al acceder a la cámara")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = frame[:, :, ::-1]
            caras_actuales = face_recognition.face_locations(rgb_frame)
            codificaciones_actuales = face_recognition.face_encodings(rgb_frame, caras_actuales)

            for codificacion, ubicacion in zip(codificaciones_actuales, caras_actuales):
                matches = face_recognition.compare_faces(self.rostros_codificados, codificacion)
                face_distances = face_recognition.face_distance(self.rostros_codificados, codificacion)

                if True in matches:
                    mejor_match = np.argmin(face_distances)
                    carnet_reconocido = self.carnets[mejor_match]
                    self.registrar_ingreso(carnet_reconocido)

                    y1, x2, y2, x1 = ubicacion
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, carnet_reconocido, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow("Registro de Asistencia", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # Presionar ESC para salir
                break

        cap.release()
        cv2.destroyAllWindows()
