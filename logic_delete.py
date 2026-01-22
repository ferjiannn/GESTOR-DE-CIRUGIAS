import json
from datetime import datetime, timedelta
from resources_validation import guardar_recursos_operativos

RUTA_CIRUGIAS = "cirugias.json"


def obtener_lunes(fecha_str):
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    return (fecha - timedelta(days=fecha.weekday())).isoformat()


def eliminar_cirugia_por_nombre(nombre_cirugia):
    # 1. Cargar cirugías
    with open(RUTA_CIRUGIAS, "r") as f:
        cirugias = json.load(f)

    if nombre_cirugia not in cirugias:
        return False, "La cirugía no existe"

    cirugia = cirugias[nombre_cirugia]

    fecha = cirugia["fecha"]
    lunes = obtener_lunes(fecha)
    recursos = cirugia["recursos"]

    # 2. Liberar recursos (restar consumo semanal)
    with open("APP/recursos.json", "r") as f:
        recursos_operativos = json.load(f)["recursos_operativos"]

    for recurso, cantidad in recursos.items():
        consumo = recursos_operativos[recurso]["consumo_semanal"]
        if lunes in consumo:
            consumo[lunes] -= cantidad
            if consumo[lunes] <= 0:
                del consumo[lunes]

    guardar_recursos_operativos(recursos_operativos)

    # 3. Eliminar cirugía
    del cirugias[nombre_cirugia]

    with open(RUTA_CIRUGIAS, "w") as f:
        json.dump(cirugias, f, indent=4)

    return True, "Cirugía eliminada correctamente"