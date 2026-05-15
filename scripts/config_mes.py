"""
config_mes.py — Diccionario por mes con la NARRATIVA de cada egreso e ingreso.

Esto es lo único que se edita cuando llega un mes nuevo. Cada egreso lleva:
  - titulo:        nombre legible corto
  - para_que:      en qué se usó el dinero
  - beneficio:     a quién/qué benefició
  - comprobante:   referencia opcional (Yape/Plin a quién, etc.)
  - categoria_ui:  cómo se agrupa en la torta
  - es_inversion:  True si es activo (no consumo del mes)
  - icono:         emoji opcional

Si falta una entrada, el sistema usa los datos del xlsx tal cual y marca
"info pendiente" en la página.
"""

# Marzo 2026-1 ----------------------------------------------------------------
MARZO = {
    "fuentes_ingresos": [
        {
            "nombre": "Membresías (fees mensuales)",
            "monto": 640.0,
            "detalle": "64 aportes de S/10 entre el 23 y 30 de marzo (semana 1 del ciclo).",
            "beneficiarios": "Aporte de los miembros activos de 180DC PUCP.",
            "icono": "👥",
        },
    ],
    "egresos": [
        {
            "titulo": "Bocaditos para la bienvenida",
            "monto": 62.0,
            "fecha": "24/03/2026",
            "para_que": "Snacks y bebidas para la actividad de bienvenida del ciclo (S0).",
            "beneficio": "Miembros nuevos y antiguos que asistieron a la bienvenida.",
            "comprobante": "2 pagos por Plin a colaboradoras internas que cubrieron la compra.",
            "categoria_ui": "Bienvenida — Insumos",
            "es_inversion": False,
            "icono": "🥨",
        },
        {
            "titulo": "Materiales",
            "monto": 131.17,
            "fecha": "24/03/2026",
            "para_que": "Papelotes, plumones e insumos para dinámicas de la bienvenida.",
            "beneficio": "Actividades de la semana de bienvenida.",
            "comprobante": "2 pagos por Plin a colaboradores internos que adelantaron la compra.",
            "categoria_ui": "Bienvenida — Insumos",
            "es_inversion": False,
            "icono": "🖍️",
        },
        {
            "titulo": "Photochecks",
            "monto": 50.0,
            "fecha": "13/03/2026",
            "para_que": "Photochecks (credenciales con cordón) para identificar a los miembros.",
            "beneficio": "Todo el equipo del ciclo 2026-1 (reutilizable).",
            "comprobante": "Plin a proveedor de impresión.",
            "categoria_ui": "Inversión — Photochecks",
            "es_inversion": True,
            "icono": "🪪",
        },
        {
            "titulo": "Polos institucionales",
            "monto": 120.0,
            "fecha": "13/03/2026 - 18/03/2026",
            "para_que": "Compra de polos con identidad 180DC para miembros del ciclo.",
            "beneficio": "Inventario que se entrega a miembros activos (reutilizable).",
            "comprobante": "Plin a proveedor de polos.",
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
            "beneficiarios": "Aporte de miembros activos pendientes del cobro de marzo + nuevos del mes.",
            "icono": "👥",
        },
    ],
    "egresos": [
        {
            "titulo": "Capacitación BCG en la UP",
            "monto": 54.83,
            "fecha": "16/04/2026",
            "para_que": "Pago de inscripción/insumos para una capacitación dictada por BCG (Boston Consulting Group) realizada en la Universidad del Pacífico.",
            "beneficio": "Miembros que asistieron a la capacitación externa (formación profesional).",
            "comprobante": "Pago por Yape al organizador externo de la capacitación.",
            "categoria_ui": "Capacitación",
            "es_inversion": False,
            "icono": "🎓",
        },
        {
            "titulo": "Reserva local — 1ra Integración",
            "monto": 20.0,
            "fecha": "25/04/2026",
            "para_que": "Reserva de pizzería para la primera actividad de integración del ciclo.",
            "beneficio": "Miembros del equipo (actividad de cohesión).",
            "comprobante": "Yape al local (pizzería).",
            "categoria_ui": "Integración",
            "es_inversion": False,
            "icono": "🍕",
        },
        {
            "titulo": "ITF (Impuesto a Transacciones Financieras)",
            "monto": 0.05,
            "fecha": "14/04/2026",
            "para_que": "Impuesto cobrado por el banco al trasladar fondos de Interbank a BCP (consolidación de cuenta operativa).",
            "beneficio": "N/A — costo bancario obligatorio.",
            "comprobante": "Cargo automático BCP.",
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

# Registro global por mes
NARRATIVA = {
    "Marzo": MARZO,
    "Abril": ABRIL,
}
