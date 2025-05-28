import pywhatkit
import pyautogui
import time
import re

def enviar_whatsapp(numero_telefono, nombre, ruta_pdf):
    try:
        # Limpiar número: eliminar todo excepto dígitos
        numero_limpio = re.sub(r'\D', '', numero_telefono)

        # Validar y formatear para Guatemala
        if len(numero_limpio) == 8:
            numero_formateado = f"+502{numero_limpio}"
        elif len(numero_limpio) == 11 and numero_limpio.startswith("502"):
            numero_formateado = f"+{numero_limpio}"
        else:
            raise ValueError("Número no válido para Guatemala (8 dígitos o 502+8 dígitos).")

        # Mensaje personalizado
        mensaje = (
            f"Hola {nombre}, aquí está tu carnet digital. "
            f"Puedes encontrarlo en el siguiente archivo:\n{ruta_pdf}"
        )

        # Enviar inmediatamente
        pywhatkit.sendwhatmsg_instantly(numero_formateado, mensaje, wait_time=10, tab_close=True)

        # Esperar carga de WhatsApp Web y presionar Enter automáticamente
        time.sleep(20)
        pyautogui.click(300, 300)
        time.sleep(1)
        pyautogui.press("enter")

        print("Mensaje de WhatsApp enviado automáticamente.")
    except Exception as e:
        print(f"Error al enviar WhatsApp: {str(e)}")
