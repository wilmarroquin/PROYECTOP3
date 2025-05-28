import mysql.connector

class CConexion:

    @staticmethod
    def ConexionDB():
        try:
            conexion = mysql.connector.connect(
                user="root",
                password="Progra2025",
                host= "localhost",
                database="db_biometrico",
                port= '3306')
            print("conexion correcta")
            return conexion
        except mysql.connector.Error as error:
            print("Error en la conexion{}".format(error))
            return None

    ConexionDB()    