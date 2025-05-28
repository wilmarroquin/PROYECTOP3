from Conexion import CConexion
import mysql.connector
import datetime

class Registro:

    @staticmethod
    def registrousuarios(carnet, nombre, apellido, telefono, correo_umg, fotografia, id_tipo_persona, id_carrera, id_seccion):
        conexion = None
        cursor = None

        try:
            conexion = CConexion.ConexionDB()
            cursor = conexion.cursor()

            sql = """INSERT INTO personas (carnet, nombre, apellido, telefono, correo_umg, fotografia, id_tipo_persona, id_carrera, id_seccion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            with open(fotografia, 'rb') as file:
                foto_blob = file.read()
            valores = ( carnet, nombre, apellido, telefono, correo_umg, foto_blob, id_tipo_persona, id_carrera, id_seccion)
            cursor.execute(sql, valores)
            conexion.commit()
            print(f"Registros afectados: {cursor.rowcount}")
            return True
        except mysql.connector.Error as error:
            print(f"Error al ingresar los datos{error}")
            return None
        
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def registrar_ingreso(carnet):
        try:
            conexion = CConexion.ConexionDB()
            cursor = conexion.cursor()

            ahora = datetime.datetime.now()
            hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

            # Verificar si ya se registró un ingreso hoy
            consulta = """
                SELECT COUNT(*) FROM ingresos 
                WHERE carnet = %s AND fecha_hora BETWEEN %s AND %s
            """
            cursor.execute(consulta, (carnet, hoy_inicio, hoy_fin))
            cantidad = cursor.fetchone()[0]

            if cantidad == 0:
                sql = "INSERT INTO ingresos (carnet, fecha_hora) VALUES (%s, %s)"
                cursor.execute(sql, (carnet, ahora))
                conexion.commit()
                print(f"[OK] Ingreso registrado para {carnet} a las {ahora}")
                return True
            else:
                print(f"[INFO] El usuario {carnet} ya registró ingreso hoy.")
                return False

        except Exception as e:
            print(f"[ERROR] Error al registrar ingreso: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()
