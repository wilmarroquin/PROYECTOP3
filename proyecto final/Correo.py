import smtplib
import os
from email.message import EmailMessage

def enviar_correo(destinatario, nombre, carnet, ruta_carnet_pdf=None):
    try:
        remitente = "wmarroquing5@miumg.edu.gt"
        clave = "iemupcgodtbzbtue"
    

        mensaje = EmailMessage()
        mensaje['Subject'] = "Registro Exitoso en el Sistema Biometrico UMG"
        mensaje['From'] = remitente
        mensaje['To'] = destinatario
        mensaje.set_content(
            f"Hola {nombre},\n\n"
            f"Tu registro con carnet {carnet} ha sido exitoso.\n\n"
        )

        if ruta_carnet_pdf and os.path.exists(ruta_carnet_pdf):
            with open(ruta_carnet_pdf, 'rb') as f:
                mensaje.add_attachment(
                    f.read(),
                    maintype='application',
                    subtype='pdf',
                    filename=os.path.basename(ruta_carnet_pdf)
                )

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(remitente, clave)
            smtp.send_message(mensaje)
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo electronico{str(e)}")