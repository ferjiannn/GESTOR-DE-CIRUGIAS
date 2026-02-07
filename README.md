# Sistema de Gestión de Cirugías – JF Bone & Motion Center

Este es mi primer proyecto como estudiante de la carrera Ciencia de la Computación.

## Tema seleccionado

Sistema de gestión para la planificación y administración de cirugías en un salón de ortopedia.

---

## Breve descripción del tema

Este proyecto consiste en una aplicación desarrollada con Python y Streamlit que permite organizar y controlar la programación de cirugías en un centro especializado en ortopedia.

El sistema gestiona quirófanos, personal médico y recursos operativos, asegurando que cada cirugía cumpla con las restricciones establecidas antes de ser agendada. Además, mantiene un control del consumo semanal de recursos para evitar sobreasignaciones.

El objetivo principal es simular un entorno real de administración hospitalaria, aplicando lógica de validación, persistencia de datos en JSON y control estructurado de recursos.

---

## Cosas que se pueden hacer en la aplicación

- Acceder mediante contraseña al sistema.
- Programar cirugías seleccionando:
  - Fecha
  - Quirófano
  - Sesión
  - Recursos necesarios
  - Personal involucrado
- Validar disponibilidad de quirófanos.
- Validar disponibilidad de recursos antes de agendar.
- Controlar consumo semanal de insumos.
- Visualizar cirugías agendadas agrupadas por fecha.
- Eliminar cirugías y devolver automáticamente los recursos utilizados.
- Eliminación automática de cirugías pasadas.
- Persistencia de datos mediante archivos JSON.

---

## Explicación de las restricciones entre los recursos

### • Restricción de Co-requisito

Al programar una cirugía, ciertos recursos deben estar disponibles de manera conjunta.  
Por ejemplo, no se puede completar una cirugía si el quirófano está disponible pero los recursos críticos no lo están.  
Todos los elementos necesarios deben validarse en conjunto antes de confirmar el agendamiento.

---

### • Restricción de Exclusión Mutua

Un quirófano no puede estar ocupado por más de una cirugía en la misma fecha y sesión.  
De igual forma, los recursos no pueden ser utilizados por encima de su stock semanal disponible.

Si una cirugía consume una cantidad específica de recursos, estos quedan bloqueados para otras cirugías durante esa misma semana.

---

### • Otras restricciones

- Límite máximo de consumo por cirugía para cada recurso.
- Control de stock semanal independiente por cada lunes.
- No se permite programar una cirugía si el día o la sesión están ocupados.
- Los recursos descontados se devuelven automáticamente al eliminar una cirugía.

---

## Funcionalidades avanzadas

- Gestión de stock semanal persistente.
- Validación de recursos críticos.
- Devolución automática de recursos al eliminar cirugías.
- Eliminación automática de cirugías pasadas.
- Uso de session_state para mantener coherencia interna.
- Organización modular del proyecto (separación de lógica, validación y utilidades).

---

## Pasos para ejecutar el proyecto

1. Clonar el repositorio:
    git clone

2. Entrar en la carpeta del proyecto:
    cd GESTOR DE CIRUGIAS

3. Instalar dependencias necesarias (están descritas en el archivo requirements.txt)

4. Ejecutar la aplicación:
    streamlit run App.py

5. Ingresar la contraseña configurada en APP/password.json.

---

Cabe aclarar que, por alguna razón que desconozco, en ocasiones en la página de staff_access, luego de ingresar los datos solicitados, es necesario pulsar 2 veces el botón de AGENDAR CIRUGIA para acceder a la página, contratiempo que no afecta en absoluto la funcionalidad del proyecto y es quizás un problema de la propia interfaz de streamlit.


Este proyecto fue desarrollado como simulación académica de un sistema de gestión hospitalaria enfocado en ortopedia, integrando validaciones lógicas, manejo de archivos JSON y control estructurado de recursos.


