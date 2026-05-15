# 180DC PUCP — Portal de Transparencia Financiera

Sitio web estático que publica mes a mes el estado de las finanzas del ciclo.
Pensado para subir a **GitHub Pages** y mantener con esfuerzo mínimo.

> **Demo de cómo se ve:** sitio responsive con una página por mes que muestra
> ingresos, egresos detallados (con "¿en qué se usó?" y "¿a quién benefició?"),
> distinción clara entre **gasto operativo** e **inversión IME**, y dos
> gráficos limpios por mes (distribución por categoría + comparativo).

---

## Estructura del repo

```
sitio_180dc/
├── data/                          # archivos fuente (no se publican)
│   ├── transacciones_marzo.xlsx
│   └── transacciones_abril.xlsx
├── scripts/
│   ├── helpers.py                 # carga / clasifica el xlsx
│   ├── config_mes.py              # NARRATIVA por mes (qué, para qué, beneficio)
│   └── build.py                   # genera el sitio
├── site/                          # salida publicable (lo que sirve GitHub Pages)
│   ├── index.html
│   ├── assets/style.css
│   ├── meses/marzo.html, abril.html
│   └── downloads/                 # copia descargable de los xlsx fuente
├── .github/workflows/deploy.yml   # auto-deploy en cada push
├── requirements.txt
└── README.md
```

---


---

## Cómo agregar un mes nuevo (ej. Mayo)

Tres pasos, **sin tocar el código de gráficos**.

### 1. Subir el archivo de transacciones
Copia el nuevo `REGISTRO_DE_TRANSACCIONES__MAYO__.xlsx` a
`data/transacciones_mayo.xlsx`.

### 2. Agregar la narrativa
Abre `scripts/config_mes.py` y agrega un bloque siguiendo el patrón de
`MARZO`/`ABRIL`. Por cada egreso describe **en qué se usó**, **a quién
benefició** y el **comprobante** (Yape/Plin a quién, etc.):

```python
MAYO = {
    "fuentes_ingresos": [
        {"nombre": "Membresías", "monto": 50.0,
         "detalle": "5 aportes en mayo.", "icono": "👥"},
    ],
    "egresos": [
        {"titulo": "Pago de RUC",
         "monto": 800.0, "fecha": "06/05/2026",
         "para_que": "Trámite y pago del RUC de la agrupación...",
         "beneficio": "Toda la agrupación (formalización tributaria).",
         "comprobante": "Pago BCP",
         "categoria_ui": "Operación legal",
         "es_inversion": False, "icono": "📋"},
    ],
    "nota_cierre": "En mayo la agrupación obtuvo su RUC...",
}
NARRATIVA["Mayo"] = MAYO
```

Luego añade el mes al final de la lista `MESES_CONFIG` en
`scripts/build.py`:

```python
MESES_CONFIG = [
    {"mes": "Marzo", "slug": "marzo", "xlsx": "transacciones_marzo.xlsx"},
    {"mes": "Abril", "slug": "abril", "xlsx": "transacciones_abril.xlsx"},
    {"mes": "Mayo",  "slug": "mayo",  "xlsx": "transacciones_mayo.xlsx"},  # nuevo
]
```

### 3. Push
```bash
git add .
git commit -m "Mayo 2026-1"
git push
```
El workflow regenera el sitio y publica la nueva página.

---

## Probar el sitio localmente

```bash
pip install -r requirements.txt
python scripts/build.py

# servir local
cd site && python -m http.server 8000
# abrir http://localhost:8000
```

---

## Decisiones contables aplicadas

- **Ingresos**: lo que entra a la caja en el mes (membresías, donaciones,
  recaudaciones de eventos, patrocinios).
- **Egresos operativos**: consumibles del mes (bocaditos, transporte, ITF,
  capacitaciones, integración).
- **Inversión IME** (Inventario / Material reutilizable): bienes que se
  quedan con la agrupación y se reutilizan en ciclos futuros (polos,
  photochecks, equipamiento). Se descuentan del saldo de caja pero **se
  muestran separados** para que un mes con compra de polos no parezca
  deficitario.
- **Saldo final** = Saldo inicial + Ingresos − Egresos operativos − Inversión.

La clasificación entre operativo e inversión se controla en
`scripts/config_mes.py` con el flag `es_inversion: True/False` por egreso.

---

## Verificación

Cada `python scripts/build.py` imprime el cuadre del mes:

```
Marzo   Ingresos: S/ 640.00  Egresos op.: S/ 193.17  Inv: S/ 290.00  Saldo final: S/ 1,077.88
Abril   Ingresos: S/ 110.00  Egresos op.: S/  74.88  Inv: S/   0.00  Saldo final: S/ 1,113.00
```

El **saldo final** debe coincidir exactamente con la celda "SALDO FINAL (en
efectivo)" de la hoja "Ingresos y Egresos" del xlsx fuente.
