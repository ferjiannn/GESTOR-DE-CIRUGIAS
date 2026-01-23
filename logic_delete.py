import json
from datetime import datetime, timedelta
import os

# Ruta al JSON de cirugías (nivel superior de Pages)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CIRUGIAS = os.path.join(BASE_DIR, "Pages", "cirugías.json")

# Ruta al JSON de recursos (en APP)
RUTA_RECURSOS = os.path.join(BASE_DIR, "APP", "recursos.json")


def obtener_lunes(fecha_str):
    """
    Dada una fecha 'YYYY-MM-DD', devuelve la fecha del lunes de esa semana.
    """
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    lunes = fecha - timedelta(days=fecha.weekday())
    return lunes.isoformat()


def guardar_recursos_operativos(recursos_operativos):
    """
    Guarda los recursos operativos en recursos.json.
    """
    with open(RUTA_RECURSOS, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["recursos_operativos"] = recursos_operativos
    with open(RUTA_RECURSOS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def eliminar_cirugia_por_nombre(nombre_cirugia):
    """
    Elimina la cirugía por nombre y libera recursos correspondientes.
    """
    # 1️⃣ Cargar cirugías
    if not os.path.exists(RUTA_CIRUGIAS):
        return False, "EL ARCHIVO DE CIRUGÍAS NO EXISTE"

    with open(RUTA_CIRUGIAS, "r", encoding="utf-8") as f:
        cirugias = json.load(f)

    # Buscar la cirugía en todo el JSON
    encontrada = False
    for q_id, q_data in cirugias.items():
        for fecha, lista_cirugias in q_data.get("cirugias", {}).items():
            for c in lista_cirugias:
                if c.get("nombre") == nombre_cirugia:
                    # Guardar datos para liberar recursos
                    recursos = c.get("recursos", {})
                    lunes = obtener_lunes(fecha)

                    # Liberar recursos en recursos_operativos
                    with open(RUTA_RECURSOS, "r", encoding="utf-8") as f:
                        recursos_operativos = json.load(f)["recursos_operativos"]

                    for r, cantidad in recursos.items():
                        consumo = recursos_operativos[r].get("consumo_semanal", {})
                        if lunes in consumo:
                            consumo[lunes] -= cantidad
                            if consumo[lunes] <= 0:
                                del consumo[lunes]

                    guardar_recursos_operativos(recursos_operativos)

                    # Eliminar la cirugía
                    lista_cirugias.remove(c)
                    encontrada = True
                    break
            if encontrada:
                break
        if encontrada:
            break

    if not encontrada:
        return False, "LA CIRUGÍA NO EXISTE"

    # Guardar los cambios en el JSON de cirugías
    with open(RUTA_CIRUGIAS, "w", encoding="utf-8") as f:
        json.dump(cirugias, f, ensure_ascii=False, indent=4)

    return True, "CIRUGÍA ELIMINADA CORRECTAMENTE"