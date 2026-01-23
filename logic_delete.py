import json
from datetime import datetime, timedelta
import os

# Ruta al JSON de cirugías
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CIRUGIAS = os.path.join(BASE_DIR, "cirugías.json")
RUTA_RECURSOS = os.path.join(BASE_DIR, "APP", "recursos.json")  # Ajusta según tu estructura

def obtener_lunes(fecha_str):
    """
    Devuelve la fecha del lunes de la semana de la fecha dada.
    """
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    lunes = fecha - timedelta(days=fecha.weekday())
    return lunes.isoformat()

def guardar_recursos_operativos(recursos_operativos):
    """
    Guarda el JSON de recursos operativos actualizado.
    """
    with open(RUTA_RECURSOS, "w", encoding="utf-8") as f:
        json.dump({"recursos_operativos": recursos_operativos}, f, indent=4, ensure_ascii=False)

def eliminar_cirugia_por_nombre(nombre_cirugia):
    """
    Elimina una cirugía por su nombre, libera recursos y actualiza los JSON.
    """
    # 1️⃣ Cargar cirugías
    if not os.path.exists(RUTA_CIRUGIAS):
        return False, "EL ARCHIVO DE CIRUGÍAS NO EXISTE."

    with open(RUTA_CIRUGIAS, "r", encoding="utf-8") as f:
        quirofanos = json.load(f)

    # Buscar cirugía
    encontrada = None
    q_id_encontrado = None
    fecha_encontrada = None

    for q_id, q_data in quirofanos.items():
        for fecha, cirugias_dia in q_data.get("cirugias", {}).items():
            for c in cirugias_dia:
                if c.get("nombre") == nombre_cirugia:
                    encontrada = c
                    q_id_encontrado = q_id
                    fecha_encontrada = fecha
                    break
            if encontrada:
                break
        if encontrada:
            break

    if not encontrada:
        return False, "LA CIRUGÍA NO EXISTE."

    # 2️⃣ Liberar recursos
    if not os.path.exists(RUTA_RECURSOS):
        return False, "EL ARCHIVO DE RECURSOS NO EXISTE."

    with open(RUTA_RECURSOS, "r", encoding="utf-8") as f:
        recursos_operativos = json.load(f).get("recursos_operativos", {})

    lunes = obtener_lunes(fecha_encontrada)
    recursos = encontrada.get("recursos", {})

    for recurso, cantidad in recursos.items():
        if recurso in recursos_operativos:
            consumo = recursos_operativos[recurso].get("consumo_semanal", {})
            consumo[lunes] = consumo.get(lunes, 0) - cantidad
            if consumo[lunes] <= 0:
                del consumo[lunes]

    # Guardar recursos actualizados
    guardar_recursos_operativos(recursos_operativos)

    # 3️⃣ Eliminar cirugía del JSON
    cirugias_dia = quirofanos[q_id_encontrado]["cirugias"].get(fecha_encontrada, [])
    cirugias_dia = [c for c in cirugias_dia if c.get("nombre") != nombre_cirugia]
    quirofanos[q_id_encontrado]["cirugias"][fecha_encontrada] = cirugias_dia

    # Si la fecha queda vacía, se puede eliminar la clave
    if not quirofanos[q_id_encontrado]["cirugias"][fecha_encontrada]:
        del quirofanos[q_id_encontrado]["cirugias"][fecha_encontrada]

    # Guardar cirugías actualizadas
    with open(RUTA_CIRUGIAS, "w", encoding="utf-8") as f:
        json.dump(quirofanos, f, indent=4, ensure_ascii=False)

    return True, "CIRUGÍA ELIMINADA CORRECTAMENTE"