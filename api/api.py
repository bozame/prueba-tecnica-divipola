from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import os
import mysql.connector

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
load_dotenv()
print("HOST:", os.getenv("MYSQLHOST"))
print("USER:", os.getenv("MYSQLUSER"))
print("PASSWORD:", os.getenv("MYSQLPASSWORD"))
print("DATABASE:", os.getenv("MYSQLDATABASE"))
print("PORT:", os.getenv("MYSQLPORT"))


#conectar db
def get_db():
    con = mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=os.getenv("MYSQLPORT")
    )     
    return con 

#get lugares
@app.route("/divipola", methods=["GET"])
def get_lugares():
    con = get_db()
    if con is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"})
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM divipola") 
    lugares = cursor.fetchall()
    con.close()
    return jsonify(lugares)

#post lugares
@app.route("/divipola", methods=["POST"])
@cross_origin()
def post_lugares():
    try:
        datos = request.get_json()
        con = get_db()
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO divipola (cod_pais, cod_departamento, cod_municipio, nom_departamento, nom_municipio, nom_corregimiento) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                datos["cod_pais"],
                datos["cod_departamento"],
                datos["cod_municipio"],
                datos["nom_departamento"],
                datos["nom_municipio"],
                datos["nom_corregimiento"]
            )
        )
        con.commit()
        con.close()
        return "Lugar agregado exitosamente"
    except Exception:
        print(f"Error al insertar")
        return "Error al insertar"

#put lugares
@app.route("/divipola/<cod_departamento>/<cod_municipio>", methods=["PUT"])
def actualizar_lugar(cod_departamento, cod_municipio):
    datos = request.get_json()
    con = get_db()
    cursor = con.cursor() 
    cursor.execute("""
        UPDATE divipola 
        SET nom_departamento = %s, nom_municipio = %s, nom_corregimiento = %s
        WHERE cod_departamento = %s AND cod_municipio = %s
        """, (
        datos["nom_departamento"], 
        datos["nom_municipio"], 
        datos["nom_corregimiento"],
        cod_departamento, 
        cod_municipio
    ))
    con.commit()
    con.close()
    return f"Lugar {cod_municipio} actualizado"


#delete lugares
@app.route("/divipola/<cod_departamento>/<cod_municipio>", methods=["DELETE"])
def borrar_lugar(cod_departamento, cod_municipio):
    con = get_db()
    cursor = con.cursor() 
    cursor.execute("DELETE FROM divipola WHERE cod_departamento = %s AND cod_municipio = %s", (cod_departamento, cod_municipio),)
    con.commit()
    con.close()
    return f"Lugar con departamento {cod_departamento} y municipio {cod_municipio} eliminado exitosamente"

# este get es para verificar la conexión
# funciona como un disparador para leugo llamar la función de sincronizar
@app.route("/ping", methods=["GET"])
def ping():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT"))
    app.run(host="0.0.0.0", port=port)