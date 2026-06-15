"""
config_mes.py — Textos del informe de cada mes (los NÚMEROS salen del Excel).

Este archivo SOLO describe en palabras cada ingreso y egreso. Los montos,
saldos y totales se calculan automáticamente desde el archivo Excel del mes
(carpeta data/). Lo que escribas aquí debe coincidir, fila por fila, con ese
Excel.

Por cada INGRESO (lista "fuentes_ingresos"):
  - nombre:   título corto (ej. "Membresías")
  - monto:    monto en soles, sin "S/" (ej. 110.0)
  - detalle:  explicación de una línea
  - fecha:    opcional, "DD/MM/AAAA"

Por cada EGRESO (lista "egresos"):
  - titulo:        nombre legible corto
  - monto:         monto en soles, sin "S/" (ej. 54.83)
  - fecha:         "DD/MM/AAAA" (o rango "DD/MM/AAAA - DD/MM/AAAA")
  - para_que:      ¿en qué se usó el dinero? (frase clara)
  - categoria_ui:  etiqueta para agrupar en el gráfico de torta
  - es_inversion:  True solo si es un bien reutilizable (polos, equipos);
                   en la gran mayoría de casos es False

Y "nota_cierre": un párrafo de resumen del mes. Usa **negritas** con dobles
asteriscos si quieres resaltar algo.
"""

# Marzo 2026-1 ----------------------------------------------------------------
MARZO = {
    "fuentes_ingresos": [
        {
            "nombre": "Membresías (fees mensuales)",
            "monto": 640.0,
            "detalle": "64 aportes de S/10 entre el 23 y 30 de marzo (semana 1 del ciclo).",
            "icono": "👥",
        },
    ],
    "egresos": [
        {
            "titulo": "Catering para la bienvenida",
            "monto": 62.0,
            "fecha": "24/03/2026",
            "para_que": "Snacks y bebidas para la actividad de bienvenida del ciclo (S0).",
            "categoria_ui": "Bienvenida — Insumos",
            "es_inversion": False,
            "icono": "🥨",
        },
        {
            "titulo": "Materiales",
            "monto": 131.17,
            "fecha": "24/03/2026",
            "para_que": "Papelotes, plumones e insumos para dinámicas de la bienvenida.",
            "categoria_ui": "Bienvenida — Insumos",
            "es_inversion": False,
            "icono": "🖍️",
        },
        {
            "titulo": "Photochecks",
            "monto": 50.0,
            "fecha": "13/03/2026",
            "para_que": "Photochecks (credenciales con cordón) para identificar a los miembros.",
            "categoria_ui": "Inversión — Photochecks",
            "es_inversion": True,
            "icono": "🪪",
        },
        {
            "titulo": "Polos institucionales",
            "monto": 120.0,
            "fecha": "13/03/2026 - 18/03/2026",
            "para_que": "Compra de polos con identidad 180DC para miembros del ciclo.",
            "categoria_ui": "Inversión — Polos",
            "es_inversion": True,
            "icono": "👕",
        },
    ],
    "nota_cierre": (
        "Marzo concentra los **gastos de arranque** del ciclo: bienvenida e "
        "inventario institucional (polos y photochecks). El saldo creció porque "
        "los fees del ciclo se cobraron casi en su totalidad durante la primera "
        "semana de clases."
    ),
}

# Abril 2026-1 ----------------------------------------------------------------
ABRIL = {
    "fuentes_ingresos": [
        {
            "nombre": "Membresías (fees mensuales)",
            "monto": 110.0,
            "detalle": "11 aportes entre el 1 y 27 de abril (semanas 2–6 del ciclo).",
            "icono": "👥",
        },
    ],
    "egresos": [
        {
            "titulo": "Capacitación BCG en la UP",
            "monto": 54.83,
            "fecha": "16/04/2026",
            "para_que": "Pago de inscripción/insumos para una capacitación dictada por BCG (Boston Consulting Group) realizada en la Universidad del Pacífico.",
            "categoria_ui": "Capacitación",
            "es_inversion": False,
            "icono": "🎓",
        },
        {
            "titulo": "Reserva local — 1ra Integración",
            "monto": 20.0,
            "fecha": "25/04/2026",
            "para_que": "Reserva de pizzería para la primera actividad de integración del ciclo.",
            "categoria_ui": "Integración",
            "es_inversion": False,
            "icono": "🍕",
        },
        {
            "titulo": "ITF (Impuesto a Transacciones Financieras)",
            "monto": 0.05,
            "fecha": "14/04/2026",
            "para_que": "Impuesto cobrado por el banco al trasladar fondos de Interbank a BCP (consolidación de cuenta operativa).",
            "categoria_ui": "Impuestos / Bancario",
            "es_inversion": False,
            "icono": "🏦",
        },
    ],
    "nota_cierre": (
        "Abril fue un mes de **baja actividad**: caen los fees porque la mayoría "
        "se cobró en marzo, y los egresos se limitaron a una capacitación externa "
        "(BCG en UP), la reserva de la primera integración y el ITF del traslado "
        "bancario Interbank→BCP. No hubo nuevas inversiones."
    ),
}

# Mayo 2026-1 -----------------------------------------------------------------
MAYO = {
    "fuentes_ingresos": [],
    "egresos": [
        {
            "titulo": "Premio rifa de febrero (1ro)",
            "monto": 37.00,
            "fecha": "10/05/2026",
            "para_que": "Entrega de primer premio de la rifa pro fondos realizada en febrero.",
            "categoria_ui": "Rifas — Premios",
            "es_inversion": False,
            "icono": "🎟️",
        },
        {
            "titulo": "Premio rifa de febrero (2do)",
            "monto": 17.00,
            "fecha": "10/05/2026",
            "para_que": "Entrega de segundo premio de la rifa pro fondos realizada en febrero.",
            "categoria_ui": "Rifas — Premios",
            "es_inversion": False,
            "icono": "🎟️",
        },
        {
            "titulo": "Premio rifa de febrero (3ro)",
            "monto": 9.50,
            "fecha": "10/05/2026",
            "para_que": "Entrega de tercer premio de la rifa pro fondos realizada en febrero.",
            "categoria_ui": "Rifas — Premios",
            "es_inversion": False,
            "icono": "🎟️",
        },
    ],
    "nota_cierre": (
        "Mayo fue un mes **sin ingresos** y con un único concepto de gasto: "
        "la entrega de los tres premios pendientes de la rifa pro fondos del "
        "mes de febrero (S/ 37 + S/ 17 + S/ 9.50 = S/ 63.50). El saldo baja "
        "ligeramente pero se mantiene sólido."
    ),
}

# Junio 2026-1 ----------------------------------------------------------------
JUNIO = {
    "fuentes_ingresos": [],
    "egresos": [
        {
            "titulo": "Reserva de nombre",
            "monto": 26.40,
            "fecha": "01/06/2026",
            "para_que": "Pago por reserva de nombre ante SUNARP como parte del proceso de constitución de la agrupación.",
            "categoria_ui": "Constitución",
            "es_inversion": False,
            "icono": "📋",
        },
        {
            "titulo": "Costos registrales",
            "monto": 130.00,
            "fecha": "05/06/2026",
            "para_que": "Costos registrales asociados al proceso de constitución formal de la agrupación.",
            "categoria_ui": "Constitución",
            "es_inversion": False,
            "icono": "🏛️",
        },
        {
            "titulo": "Costos notariales",
            "monto": 821.50,
            "fecha": "10/06/2026",
            "para_que": "Honorarios notariales para la escritura pública de constitución de la agrupación.",
            "categoria_ui": "Constitución",
            "es_inversion": False,
            "icono": "⚖️",
        },
    ],
    "nota_cierre": (
        "Junio concentra el **gasto más importante del ciclo**: la constitución "
        "formal de 180DC PUCP como persona jurídica (reserva de nombre, costos "
        "registrales y notariales por un total de S/ 977.90). No hubo ingresos "
        "en el mes, y el saldo baja significativamente. Es un gasto estratégico "
        "y no recurrente que habilita a la agrupación para operar formalmente."
    ),
}

# Registro global por mes
NARRATIVA = {
    "Marzo": MARZO,
    "Abril": ABRIL,
    "Mayo": MAYO,
    "Junio": JUNIO,
}
