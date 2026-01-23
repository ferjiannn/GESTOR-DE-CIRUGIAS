import json
from datetime import datetime, timedelta

RUTA_CIRUGIAS = "cirugías.json"
RUTA_RECURSOS = "APP/recursos.json"


def obtener_lunes(fecha_str):
    """Devuelve el lunes de la semana de la fecha dada (ISO format)."""
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    return (fecha - timedelta(days=fecha.weekday())).isoformat()


def eliminar_cirugia_por_nombre(nombre_cirugia, fecha_cirugia):
    """
    Elimina una cirugía específica según su nombre y fecha.
    Libera los recursos asociados y actualiza cirugías.json.
    """

    # 1️⃣ Cargar cirugías
    with open(RUTA_CIRUGIAS, "r", encoding="utf-8") as f:
        cirugias = json.load(f)

    encontrada = False
    # Buscar la cirugía en todos los quirófanos
    for q_id, q_data in cirugias.items():
        cirugias_dia = q_data.get("cirugias", {}).get(fecha_cirugia, [])
        for i, c in enumerate(cirugias_dia):
            if c.get("nombre") == nombre_cirugia:
                encontrada = True
                recursos = c.get("recursos", {})
                # Liberar recursos
                with open(RUTA_RECURSOS, "r", encoding="utf-8") as rf:
                    recursos_operativos = json.load(rf)["recursos_operativos"]

                lunes = obtener_lunes(fecha_cirugia)
                for recurso, cantidad in recursos.items():
                    consumo = recursos_operativos[recurso].get("consumo_semanal", {})
                    if lunes in consumo:
                        consumo[lunes] -= cantidad
                        if consumo[lunes] <= 0:
                            del consumo[lunes]

                # Guardar recursos actualizados
                with open(RUTA_RECURSOS, "w", encoding="utf-8") as wf:
                    json.dump({"recursos_operativos": recursos_operativos}, wf, ensure_ascii=False, indent=4)

                # Eliminar la cirugía
                del cirugias_dia[i]
                # Si la lista del día queda vacía, limpiar
                if not cirugias_dia:
                    del cirugias[q_id]["cirugias"][fecha_cirugia]
                break
        if encontrada:
            break

    if not encontrada:
        return False, "LA CIRUGÍA NO EXISTE PARA ESA FECHA"

    # Guardar cambios en cirugías.json
    with open(RUTA_CIRUGIAS, "w", encoding="utf-8") as f:
        json.dump(cirugias, f, ensure_ascii=False, indent=4)

    return True, "CIRUGÍA ELIMINADA CORRECTAMENTE"