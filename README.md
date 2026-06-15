# 180DC PUCP — Portal de Transparencia Financiera

Sitio web que publica, mes a mes, en qué se gasta el dinero de la agrupación.
Está hecho para mantenerse **sin saber programar**: editas un Excel, escribes
unas descripciones, ejecutas un comando y subes los cambios con GitHub Desktop.

🔗 **Sitio publicado:** https://av-gomez.github.io/sitio_180dc/

---

## 1. Cómo funciona (en 30 segundos)

El sitio se arma a partir de **dos fuentes**:

| Fuente | Qué aporta | Dónde está |
|--------|-----------|------------|
| 📊 **Excel del mes** | Los **números**: saldos, montos, totales | `data/transacciones_<mes>.xlsx` |
| ✍️ **Descripciones** | Los **textos**: en qué se usó cada gasto | `scripts/config_mes.py` |

Un comando (`python scripts/build.py`) junta ambos y genera las páginas web
dentro de la carpeta `site/`. Al subir los cambios a GitHub, el sitio se
publica solo.

> ⚠️ **Importante:** los números **siempre** salen del Excel. Las descripciones
> que escribes en `config_mes.py` deben coincidir, fila por fila, con ese Excel.
> Así cualquiera puede descargar el Excel y verificar la información.

---

## 2. Requisitos (instalar una sola vez)

1. **Python** → https://www.python.org/downloads/
   Durante la instalación marca la casilla **"Add Python to PATH"**.
2. **GitHub Desktop** → https://desktop.github.com/
   Inicia sesión y abre (clona) el repositorio `sitio_180dc`.
3. Abre **PowerShell** (o la terminal) en la carpeta del proyecto y ejecuta
   una vez, para instalar las librerías necesarias:

   ```powershell
   pip install -r requirements.txt
   ```

---

## 3. Actualizar / corregir un mes que YA existe

1. Abre el Excel del mes en `data/` (ej. `data/transacciones_mayo.xlsx`) y
   corrige lo que haga falta. Guarda.
2. Si cambió alguna descripción, edítala en `scripts/config_mes.py`.
3. Regenera el sitio:

   ```powershell
   python scripts/build.py
   ```

4. Abre **GitHub Desktop**, escribe un mensaje (ej. "Corrige mayo") y haz
   **Commit to main** → **Push origin**. En 1–2 minutos el sitio se actualiza.

---

## 4. Agregar un mes NUEVO

Ejemplo: agregar **Julio**.

### Paso 1 — El Excel del mes
Copia el registro de transacciones de julio a la carpeta `data/` con el nombre
`transacciones_julio.xlsx`.

El Excel debe mantener el **mismo formato** que los meses anteriores (misma hoja
`Transacciones`, misma fila de encabezados con `Ord.`, `Fecha de registro`,
`Monto (S/.)`, `Descripcion`, etc.). Lo más fácil es **duplicar el Excel del mes
anterior** y reemplazar los movimientos.

Reglas del Excel:
- La fila con **`Ord.` = 0** es el **saldo anterior** (el saldo final del mes
  pasado). De ahí arranca el mes.
- Cada movimiento va con su `Ord.` (1, 2, 3…), su fecha en formato
  **DD/MM/AAAA** y su monto.
- Si la descripción contiene la palabra **"ingreso", "fee" o "membresía"**, se
  cuenta como **ingreso**; si no, como **egreso**.

### Paso 2 — Las descripciones
Abre `scripts/config_mes.py` y agrega un bloque para julio copiando el patrón de
un mes existente. Solo usa los campos que se listan al inicio de ese archivo:

```python
JULIO = {
    "fuentes_ingresos": [
        {"nombre": "Membresías", "monto": 80.0,
         "detalle": "8 aportes de S/10 durante julio."},
    ],
    "egresos": [
        {"titulo": "Reserva de local — 2da Integración",
         "monto": 40.0, "fecha": "12/07/2026",
         "para_que": "Reserva del local para la segunda integración del ciclo.",
         "categoria_ui": "Integración",
         "es_inversion": False},
    ],
    "nota_cierre": "En julio la actividad principal fue la 2da integración...",
}
```

Y al final del archivo, agrégalo al registro:

```python
NARRATIVA = {
    "Marzo": MARZO,
    "Abril": ABRIL,
    "Mayo":  MAYO,
    "Junio": JUNIO,
    "Julio": JULIO,   # ← nuevo
}
```

> Si un mes **no tiene ingresos**, deja la lista vacía: `"fuentes_ingresos": []`.
> La sección de ingresos no aparecerá (así el foco queda en lo que se gastó a
> favor de los miembros).

### Paso 3 — Registrar el mes en la lista
Abre `scripts/build.py` y agrega el mes a `MESES_CONFIG` (está cerca del inicio):

```python
MESES_CONFIG = [
    {"mes": "Marzo", "slug": "marzo", "xlsx": "transacciones_marzo.xlsx"},
    {"mes": "Abril", "slug": "abril", "xlsx": "transacciones_abril.xlsx"},
    {"mes": "Mayo",  "slug": "mayo",  "xlsx": "transacciones_mayo.xlsx"},
    {"mes": "Junio", "slug": "junio", "xlsx": "transacciones_junio.xlsx"},
    {"mes": "Julio", "slug": "julio", "xlsx": "transacciones_julio.xlsx"},  # ← nuevo
]
```

- `mes`: nombre con mayúscula (debe coincidir con la clave en `config_mes.py`).
- `slug`: el nombre del archivo web, en minúsculas y sin tildes.
- `xlsx`: el nombre exacto del Excel en `data/`.

### Paso 4 — Generar y subir
```powershell
python scripts/build.py
```
Revisa el **cuadre** que imprime al final (ver sección 7), y sube con
GitHub Desktop (Commit → Push).

---

## 5. Empezar un CICLO nuevo (ej. 2026-2)

Cuando arranca un ciclo nuevo:

1. En `scripts/build.py`, cambia la línea del ciclo:
   ```python
   CICLO = "2026-2"
   ```
2. Reemplaza `MESES_CONFIG` por los meses del ciclo nuevo (borra los del ciclo
   anterior).
3. En `scripts/config_mes.py`, deja solo los bloques de los nuevos meses.
4. En `data/`, agrega los nuevos Excel. El primer mes del ciclo debe traer en su
   fila `Ord. = 0` el **saldo con el que arranca** el ciclo.

> El ciclo se muestra automáticamente en todo el sitio (cabecera, pie, títulos)
> a partir de la variable `CICLO`. No hay que tocarlo en ningún otro lugar.

---

## 6. Reglas contables aplicadas

- **Ingresos:** lo que entra a caja en el mes (membresías, donaciones,
  recaudaciones de eventos, patrocinios).
- **Egresos operativos:** consumibles del mes (bocaditos, transporte, ITF,
  capacitaciones, integraciones, premios de rifa, trámites).
- **Inversión IME** (Inventario / Material reutilizable): bienes que se quedan
  con la agrupación y se reutilizan en ciclos futuros (polos, photochecks,
  equipamiento). Se descuentan del saldo, pero se muestran **separados** para
  que un mes con compra de inventario no parezca deficitario.
- **Saldo final** = Saldo inicial + Ingresos − Egresos operativos − Inversión.

En la práctica, casi todos los gastos son **operativos** (`es_inversion: False`).
Usa `es_inversion: True` solo para bienes reutilizables.

---

## 7. Verificación (el "cuadre")

Cada vez que ejecutas `python scripts/build.py`, imprime un resumen:

```
Marzo   Ingresos: S/ 640.00  Egresos op.: S/ 193.17  Inv: S/ 290.00  Saldo final: S/ 1,077.88
Abril   Ingresos: S/ 110.00  Egresos op.: S/  74.88  Inv: S/   0.00  Saldo final: S/ 1,113.00
```

El **saldo final** de cada mes debe ser igual al **saldo inicial del mes
siguiente** (la fila `Ord. = 0` del Excel siguiente). Si no coincide, revisa los
montos del Excel.

Para ver el sitio en tu computadora antes de subirlo:

```powershell
python -m http.server 8000 --directory site
```
Luego abre http://localhost:8000 en el navegador.

---

## 8. Estructura de carpetas

```
sitio_180dc/
├── data/                      Excel fuente de cada mes (los NÚMEROS)
│   └── transacciones_<mes>.xlsx
├── scripts/
│   ├── build.py               Genera el sitio. Aquí está CICLO y MESES_CONFIG
│   ├── config_mes.py          Las descripciones de cada mes (los TEXTOS)
│   └── helpers.py             Lee y procesa el Excel (no necesitas tocarlo)
├── site/                      Sitio web generado (se sube tal cual a GitHub Pages)
│   ├── index.html
│   ├── meses/<mes>.html
│   ├── downloads/             Copia de los Excel para descargar
│   └── assets/                Estilos (style.css) y logo (180.jpg)
├── requirements.txt           Librerías de Python
└── README.md                  Este archivo
```

> **No edites a mano** los archivos dentro de `site/`: se sobrescriben cada vez
> que corres `build.py`. Edita siempre el Excel (`data/`) y `config_mes.py`.

---

## 9. Problemas comunes

- **"python no se reconoce…"** → Python no quedó en el PATH. Reinstálalo
  marcando "Add Python to PATH".
- **"No module named pandas/openpyxl"** → ejecuta `pip install -r requirements.txt`.
- **Cambié algo pero el sitio no se actualiza** → ¿ejecutaste `python
  scripts/build.py` **antes** de hacer Commit/Push? El sitio publica lo que hay
  en `site/`, y esa carpeta solo cambia cuando corres el comando.
- **El total no coincide con la suma de las filas** → algún monto en
  `config_mes.py` no coincide con el del Excel. Recuerda: los totales salen del
  Excel; tus descripciones deben reflejar esas mismas filas.
