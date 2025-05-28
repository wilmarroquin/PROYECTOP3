from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
import os
import qrcode

def crear_carnet(nombre, apellido, carrera, carnet, ruta_foto):
    carpeta_carnets = os.path.join(os.getcwd(), "carnets")
    os.makedirs(carpeta_carnets, exist_ok=True)

    ruta_logo = os.path.join(os.getcwd(), "assets", "logo.jpg")
    nombre_archivo = f"{carnet}.pdf"
    ruta_pdf = os.path.join(carpeta_carnets, nombre_archivo)

    qr_img = qrcode.make(str(carnet))
    qr_temp = os.path.join(carpeta_carnets, f"qr_{carnet}.png")
    qr_img.save(qr_temp)

    c = canvas.Canvas(ruta_pdf, pagesize=(85.60 * mm, 53.98 * mm))

    # Fondo blanco
    c.setFillColorRGB(1, 1, 1)  # Blanco
    c.rect(0, 0, 85.60 * mm, 53.98 * mm, fill=1)

    # Texto negro
    c.setFillColorRGB(0, 0, 0)  # Negro

    # Logo
    if os.path.exists(ruta_logo):
        c.drawImage(ruta_logo, 5 * mm, 37 * mm, width=13 * mm, height=13 * mm, preserveAspectRatio=True)

    # Encabezado
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(31 * mm, 45.5 * mm, "UNIVERSIDAD")
    c.drawString(27 * mm, 41.5 * mm, "MARIANO GÁLVEZ")

    # Año
    c.setFont("Helvetica-Bold", 12)
    c.drawString(70 * mm, 5.5 * mm, "2025")

    # Foto del estudiante
    if os.path.exists(ruta_foto):
        try:
            img = Image.open(ruta_foto)
            img = img.resize((120, 150))  # en píxeles
            foto_temp = os.path.join(carpeta_carnets, f"foto_{carnet}.jpg")
            img.save(foto_temp)
            c.drawImage(foto_temp, 5 * mm, 5 * mm, width=20 * mm, height=25 * mm)
            os.remove(foto_temp)
        except Exception as e:
            print(f"No se pudo agregar la foto: {e}")

    # Datos personales
    c.setFont("Helvetica-Bold", 8)
    c.drawString(28 * mm, 30 * mm, f"{nombre} {apellido}")
    c.setFont("Helvetica", 7)
    c.drawString(28 * mm, 25 * mm, f"ID: {carnet}")
    c.drawString(28 * mm, 20 * mm, f"Carrera: {carrera}")

    # Código QR
    if os.path.exists(qr_temp):
        c.drawImage(qr_temp, 64 * mm, 35 * mm, width=18 * mm, height=18 * mm)
        os.remove(qr_temp)

     # Firma digital
    ruta_firma = os.path.join(os.getcwd(), "firma", f"firma_{carnet}.png")
    if os.path.exists(ruta_firma):
        try:
            c.drawImage(ruta_firma, 28 * mm, 5 * mm, width=30 * mm, height=10 * mm, mask='auto')
        except Exception as e:
            print(f"No se pudo agregar la firma: {e}")

    c.showPage()
    c.save()

    return ruta_pdf
