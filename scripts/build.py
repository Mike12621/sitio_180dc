"""
build.py — Genera el sitio estático del Portal de Transparencia 180DC PUCP.

Uso:
    python scripts/build.py

Lee:
  - data/transacciones_*.xlsx
  - scripts/config_mes.py (narrativa por mes)

Escribe:
  - site/index.html
  - site/meses/<mes>.html
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from helpers import cargar_mes, fmt_soles, InformeMes  # noqa: E402
from config_mes import NARRATIVA  # noqa: E402

OUT_DIR = ROOT / "site"
DATA_DIR = ROOT / "data"

MESES_CONFIG = [
    {"mes": "Marzo", "slug": "marzo", "xlsx": "transacciones_marzo.xlsx"},
    {"mes": "Abril", "slug": "abril", "xlsx": "transacciones_abril.xlsx"},
]

# =============================================================================
# Helpers de HTML
# =============================================================================
def esc(s):
    if s is None:
        return ""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))

import re
import math

_MD_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)

def md(s):
    """Escape + convierte **bold** Markdown a <strong>."""
    return _MD_BOLD.sub(r"<strong>\1</strong>", esc(s))

def svg_donut(labels, values, colores, total_label, size=260):
    """Donut SVG inline. Devuelve string SVG completo."""
    if not values or sum(values) == 0:
        return f'<div class="chart-wrap" style="display:flex;align-items:center;justify-content:center;color:var(--plomo)">Sin datos</div>'
    total = sum(values)
    cx, cy = size/2, size/2
    r_out, r_in = size*0.42, size*0.42*0.62
    paths = []
    start = -math.pi/2
    for v, c in zip(values, colores):
        frac = v/total
        end = start + frac * 2*math.pi
        # arc points
        x1, y1 = cx + r_out*math.cos(start), cy + r_out*math.sin(start)
        x2, y2 = cx + r_out*math.cos(end),   cy + r_out*math.sin(end)
        x3, y3 = cx + r_in*math.cos(end),    cy + r_in*math.sin(end)
        x4, y4 = cx + r_in*math.cos(start),  cy + r_in*math.sin(start)
        large = 1 if frac > 0.5 else 0
        d = (f"M {x1:.2f} {y1:.2f} "
             f"A {r_out:.2f} {r_out:.2f} 0 {large} 1 {x2:.2f} {y2:.2f} "
             f"L {x3:.2f} {y3:.2f} "
             f"A {r_in:.2f} {r_in:.2f} 0 {large} 0 {x4:.2f} {y4:.2f} Z")
        paths.append(f'<path d="{d}" fill="{c}" stroke="white" stroke-width="2"/>')
        start = end
    legend_rows = []
    for lbl, v, c in zip(labels, values, colores):
        pct = v/total*100
        legend_rows.append(
            f'<li><span class="dot" style="background:{c}"></span>'
            f'<span class="lbl">{esc(lbl)}</span>'
            f'<span class="val">{fmt_soles(v)} <em>· {pct:.0f}%</em></span></li>'
        )
    return (
        f'<div class="donut-block">'
        f'<svg viewBox="0 0 {size} {size}" width="100%" height="{size}" preserveAspectRatio="xMidYMid meet">'
        f'{"".join(paths)}'
        f'<text x="{cx}" y="{cy-4}" text-anchor="middle" font-size="11" fill="#6C757D">Total</text>'
        f'<text x="{cx}" y="{cy+14}" text-anchor="middle" font-size="16" font-weight="700" fill="#003C71">{total_label}</text>'
        f'</svg>'
        f'<ul class="donut-legend">{"".join(legend_rows)}</ul>'
        f'</div>'
    )


def svg_barras(labels, values, colores, width=420, height=260):
    """Barras verticales SVG inline."""
    pad_l, pad_r, pad_t, pad_b = 40, 16, 16, 36
    w = width - pad_l - pad_r
    h = height - pad_t - pad_b
    max_v = max(values) if values else 1
    if max_v == 0:
        max_v = 1
    # nice max (siguiente múltiplo "redondo")
    step_candidates = [10, 20, 50, 100, 200, 500, 1000, 2000]
    step = next((s for s in step_candidates if max_v/s <= 5), max_v)
    nice = math.ceil(max_v / step) * step
    n = len(values)
    bw = w / n * 0.55
    gap = w / n
    bars = []
    labels_x = []
    for i, (lbl, v, c) in enumerate(zip(labels, values, colores)):
        x = pad_l + gap*i + (gap - bw)/2
        bh = (v / nice) * h if nice > 0 else 0
        y = pad_t + h - bh
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" fill="{c}"/>'
            f'<text x="{x + bw/2:.1f}" y="{y - 6:.1f}" text-anchor="middle" '
            f'font-size="11" font-weight="600" fill="#1F2937">{fmt_soles(v)}</text>'
        )
        labels_x.append(
            f'<text x="{x + bw/2:.1f}" y="{pad_t + h + 18:.1f}" text-anchor="middle" '
            f'font-size="11" fill="#4B5563">{esc(lbl)}</text>'
        )
    # eje y (4 ticks)
    yticks = []
    for k in range(5):
        val = nice * k / 4
        y = pad_t + h - (val/nice)*h
        yticks.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l+w}" y2="{y:.1f}" '
            f'stroke="#E5E7EB" stroke-dasharray="2,3"/>'
            f'<text x="{pad_l-6}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#6C757D">S/ {val:.0f}</text>'
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" preserveAspectRatio="xMidYMid meet">'
        f'{"".join(yticks)}{"".join(bars)}{"".join(labels_x)}'
        f'</svg>'
    )

def nav_html(slug_actual=None):
    items = ['<a href="../index.html"' + (' class="active"' if slug_actual is None else '') + '>Inicio</a>']
    for m in MESES_CONFIG:
        cls = ' class="active"' if m["slug"] == slug_actual else ""
        items.append(f'<a href="{m["slug"]}.html"{cls}>{m["mes"]} 2026-1</a>')
    return f'<nav>{"".join(items)}</nav>'

def nav_home():
    items = ['<a class="active" href="index.html">Inicio</a>']
    for m in MESES_CONFIG:
        items.append(f'<a href="meses/{m["slug"]}.html">{m["mes"]} 2026-1</a>')
    return f'<nav>{"".join(items)}</nav>'

def layout(titulo, body, slug_actual=None, asset_prefix="."):
    nav = nav_home() if slug_actual is None else nav_html(slug_actual)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(titulo)}</title>
<link rel="stylesheet" href="{asset_prefix}/assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="wrap">
      <h1>180DC PUCP · Portal de Transparencia Financiera</h1>
      <p>Ciclo académico 2026-1 · Rendición de cuentas mensual</p>
      {nav}
    </div>
  </header>
  <main class="wrap">
    {body}
  </main>
  <footer>
    Portal de transparencia 180DC PUCP · Fuente: Registro de Transacciones mensual ·
    Generado automáticamente a partir de los archivos contables del ciclo.
  </footer>
</body>
</html>
"""

# =============================================================================
# Página mes
# =============================================================================
def render_mes(info: InformeMes, slug: str, narrativa: dict, xlsx_filename: str) -> str:
    # ---- KPIs
    kpis_html = f"""
    <div class="kpis">
      <div class="kpi"><div class="label">Saldo inicial</div><div class="value">{fmt_soles(info.saldo_inicial)}</div></div>
      <div class="kpi verde"><div class="label">Ingresos</div><div class="value">{fmt_soles(info.ingresos)}</div></div>
      <div class="kpi rojo"><div class="label">Egresos operativos</div><div class="value">{fmt_soles(info.egresos_op)}</div></div>
      <div class="kpi ambar"><div class="label">Inversión IME</div><div class="value">{fmt_soles(info.inversion)}</div></div>
      <div class="kpi azul"><div class="label">Saldo final</div><div class="value">{fmt_soles(info.saldo_final)}</div></div>
    </div>
    """

    # ---- Ecuación
    ecuacion_html = f"""
    <div class="ecuacion">
      <p><strong>Cómo se llegó al saldo final del mes</strong></p>
      <div class="form">
        {fmt_soles(info.saldo_inicial)}
        &nbsp;<span style="color:var(--verde)">+ {fmt_soles(info.ingresos)}</span>
        &nbsp;<span style="color:var(--rojo)">− {fmt_soles(info.egresos_op)}</span>
        &nbsp;<span style="color:var(--ambar)">− {fmt_soles(info.inversion)}</span>
        &nbsp;= <strong>{fmt_soles(info.saldo_final)}</strong>
      </div>
      <p class="muted" style="margin-top:10px">
        Saldo inicial + Ingresos − Egresos operativos − Inversión = Saldo final
      </p>
    </div>
    """

    # ---- Caja informativa sobre inversión (solo si hay inversión > 0)
    info_box = ""
    if info.inversion > 0:
        info_box = """
        <div class="info-box">
          <strong>¿Qué es "Inversión"?</strong>
          A diferencia de un gasto operativo (bocaditos, transporte, impuestos
          que se consumen el mismo mes), una <strong>inversión</strong> compra
          bienes que se quedan con la agrupación y se siguen usando en ciclos
          futuros (por ejemplo: polos institucionales y photochecks que se
          entregan a miembros año a año). Por eso se muestra por separado.
        </div>
        """

    # ---- Ingresos
    fuentes = narrativa.get("fuentes_ingresos", [])
    cards_ingreso = []
    for f in fuentes:
        cards_ingreso.append(f"""
        <article class="card ingreso">
          <div class="top">
            <h3><span class="icono">{f.get('icono','💰')}</span> {esc(f['nombre'])}</h3>
            <div class="monto">+ {fmt_soles(f['monto'])}</div>
          </div>
          <dl>
            <div><dt>Detalle</dt><dd>{esc(f.get('detalle',''))}</dd></div>
            <div><dt>Origen</dt><dd>{esc(f.get('beneficiarios',''))}</dd></div>
          </dl>
        </article>
        """)
    if not cards_ingreso:
        cards_ingreso.append('<p class="muted">No se registran fuentes de ingreso descritas para este mes.</p>')

    # ---- Egresos (operativos + inversión, ordenados por monto desc.)
    egresos_cfg = narrativa.get("egresos", [])
    egresos_cfg = sorted(egresos_cfg, key=lambda e: e["monto"], reverse=True)
    cards_eg = []
    for e in egresos_cfg:
        cls = "inversion" if e.get("es_inversion") else ""
        badge_cls = "inv" if e.get("es_inversion") else "op"
        badge_txt = "Inversión" if e.get("es_inversion") else "Gasto operativo"
        cards_eg.append(f"""
        <article class="card {cls}">
          <div class="top">
            <div>
              <h3><span class="icono">{e.get('icono','💸')}</span> {esc(e['titulo'])}
                  <span class="badge {badge_cls}">{badge_txt}</span></h3>
              <div class="meta">
                <span>{esc(e.get('fecha',''))}</span>
                <span>{esc(e.get('categoria_ui',''))}</span>
              </div>
            </div>
            <div class="monto">− {fmt_soles(e['monto'])}</div>
          </div>
          <dl>
            <div><dt>¿En qué se usó?</dt><dd>{esc(e.get('para_que',''))}</dd></div>
            <div><dt>¿A quién benefició?</dt><dd>{esc(e.get('beneficio',''))}</dd></div>
            <div><dt>Comprobante</dt><dd>{esc(e.get('comprobante','—'))}</dd></div>
          </dl>
        </article>
        """)
    if not cards_eg:
        cards_eg.append('<p class="muted">No hubo egresos descritos en el mes.</p>')

    # ---- Distribución (SVG donut)
    dist = {}
    for e in egresos_cfg:
        c = e.get("categoria_ui", "Otros")
        dist[c] = dist.get(c, 0) + e["monto"]
    dist_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)
    dist_labels = [k for k,_ in dist_items]
    dist_data = [v for _,v in dist_items]
    colores = ["#003C71", "#0072CE", "#F6AE2D", "#F26419", "#2BA84A", "#6C757D", "#9D4EDD"]
    color_list = [colores[i % len(colores)] for i in range(len(dist_labels))]
    donut_svg = svg_donut(dist_labels, dist_data, color_list,
                          fmt_soles(sum(dist_data)) if dist_data else "S/ 0")

    # ---- Barras comparativo (SVG)
    cmp_labels = ["Ingresos", "Egresos op.", "Inversión"]
    cmp_values = [info.ingresos, info.egresos_op, info.inversion]
    cmp_colors = ["#2BA84A", "#D7263D", "#F6AE2D"]
    barras_svg = svg_barras(cmp_labels, cmp_values, cmp_colors)

    nota = narrativa.get("nota_cierre", "")
    cierre_html = f'<div class="cierre"><strong>En resumen.</strong> {md(nota)}</div>' if nota else ""

    # ---- Bloque de descarga del archivo fuente
    descarga_html = f"""
    <div class="descarga">
      <div class="descarga-info">
        <strong>Archivo fuente del mes</strong>
        <p>Toda la información de este informe proviene del Registro de
           Transacciones contable. Puedes descargarlo para verificar línea
           por línea.</p>
      </div>
      <a class="btn-descarga" href="../downloads/{esc(xlsx_filename)}" download>
        ⬇ Descargar Excel ({esc(xlsx_filename)})
      </a>
    </div>
    """

    # ---- Body
    body = f"""
    <p class="muted">Mes contable: <strong>{info.mes} {info.ciclo}</strong> ·
       Responsable de actualización: <strong>{esc(info.responsable)}</strong> ·
       Última actualización: <strong>{esc(info.actualizacion)}</strong></p>

    <h2>Resumen del mes</h2>
    {kpis_html}
    {ecuacion_html}

    <h2>¿De dónde vino el dinero?</h2>
    <div class="cards">{''.join(cards_ingreso)}</div>

    <h2>¿En qué se usó el dinero?</h2>
    {info_box}
    <div class="cards">{''.join(cards_eg)}</div>

    <h2>Cómo se distribuyó</h2>
    <div class="chart-grid">
      <div class="chart-block">
        <h3>Distribución de egresos por categoría</h3>
        {donut_svg}
      </div>
      <div class="chart-block">
        <h3>Comparativo del mes</h3>
        {barras_svg}
      </div>
    </div>

    {cierre_html}

    <h2>Verificación y datos abiertos</h2>
    {descarga_html}
    """
    return layout(f"{info.mes} 2026-1 · 180DC PUCP", body,
                  slug_actual=slug, asset_prefix="..")

# =============================================================================
# Página índice
# =============================================================================
def render_index(infos: list[InformeMes]) -> str:
    total_ing = sum(i.ingresos for i in infos)
    total_eg = sum(i.egresos_op for i in infos)
    total_inv = sum(i.inversion for i in infos)
    saldo_inicio = infos[0].saldo_inicial if infos else 0
    saldo_actual = infos[-1].saldo_final if infos else 0

    kpis = f"""
    <div class="kpis">
      <div class="kpi"><div class="label">Saldo de inicio del ciclo</div><div class="value">{fmt_soles(saldo_inicio)}</div></div>
      <div class="kpi verde"><div class="label">Ingresos acumulados</div><div class="value">{fmt_soles(total_ing)}</div></div>
      <div class="kpi rojo"><div class="label">Egresos operativos</div><div class="value">{fmt_soles(total_eg)}</div></div>
      <div class="kpi ambar"><div class="label">Inversión acumulada</div><div class="value">{fmt_soles(total_inv)}</div></div>
      <div class="kpi azul"><div class="label">Saldo actual</div><div class="value">{fmt_soles(saldo_actual)}</div></div>
    </div>
    """

    cards = []
    for info, cfg in zip(infos, MESES_CONFIG):
        nota_resumen = NARRATIVA.get(info.mes, {}).get('nota_cierre', '')
        # mostrar resumen sin **markdown** y truncado
        resumen_plano = re.sub(r"\*\*(.+?)\*\*", r"\1", nota_resumen)
        if len(resumen_plano) > 140:
            resumen_plano = resumen_plano[:140].rstrip() + "…"
        cards.append(f"""
        <a class="mes-card" href="meses/{cfg['slug']}.html">
          <div class="mes">{info.mes} 2026-1</div>
          <h3>Estado de cuenta del mes</h3>
          <p class="resumen">{esc(resumen_plano)}</p>
          <div class="stats">
            <div><span>Ingresos</span><b>{fmt_soles(info.ingresos)}</b></div>
            <div><span>Egresos</span><b>{fmt_soles(info.egresos_op + info.inversion)}</b></div>
            <div><span>Saldo final</span><b>{fmt_soles(info.saldo_final)}</b></div>
          </div>
        </a>
        """)

    body = f"""
    <p class="lead">
      Este portal muestra de manera <strong>abierta y verificable</strong> cómo
      ingresa y sale el dinero de la agrupación durante el ciclo 2026-1.
      Cada egreso indica <strong>en qué se usó</strong> y <strong>a quién benefició</strong>.
    </p>

    <h2>Visión del ciclo</h2>
    {kpis}

    <div class="info-box">
      <strong>Sobre la "Inversión":</strong> separamos del gasto regular las
      compras de bienes que <em>no se consumen</em> en el mes y se quedan con
      la agrupación para ciclos futuros (polos institucionales, photochecks,
      eventualmente equipamiento). Esto evita inflar los egresos del mes en que
      se compraron.
    </div>

    <h2>Informes mensuales</h2>
    <div class="meses-grid">{''.join(cards)}</div>

    <h2>Sobre la información publicada</h2>
    <p>
      Los montos se toman directamente del <em>Registro de Transacciones</em>
      mensual que mantiene el área financiera. Cada movimiento del archivo
      contable original tiene su correlativo en el portal, y el
      <strong>archivo fuente de cada mes está disponible para descarga</strong>
      desde su página correspondiente, para que cualquiera pueda verificar la
      información línea por línea. Para preguntas o detalle adicional puedes
      contactar al área financiera.
    </p>
    """
    return layout("180DC PUCP · Portal de Transparencia Financiera", body,
                  slug_actual=None, asset_prefix=".")

# =============================================================================
# Main
# =============================================================================
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "meses").mkdir(exist_ok=True)
    downloads_dir = OUT_DIR / "downloads"
    downloads_dir.mkdir(exist_ok=True)

    import shutil
    infos = []
    for cfg in MESES_CONFIG:
        xlsx_path = DATA_DIR / cfg["xlsx"]
        # copiar xlsx fuente a site/downloads para que sea descargable
        shutil.copy2(xlsx_path, downloads_dir / cfg["xlsx"])
        info = cargar_mes(str(xlsx_path), cfg["mes"])
        infos.append(info)
        html = render_mes(info, cfg["slug"], NARRATIVA.get(cfg["mes"], {}), cfg["xlsx"])
        out = OUT_DIR / "meses" / f"{cfg['slug']}.html"
        out.write_text(html, encoding="utf-8")
        print(f"OK -> {out.relative_to(ROOT)}")

    index_html = render_index(infos)
    (OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"OK -> site/index.html")
    print(f"OK -> site/downloads/  ({len(MESES_CONFIG)} archivos)")

    # Cuadre
    print("\n=== Cuadre ===")
    for info in infos:
        print(f"{info.mes:6s}  Ingresos: {fmt_soles(info.ingresos)}  "
              f"Egresos op.: {fmt_soles(info.egresos_op)}  "
              f"Inv: {fmt_soles(info.inversion)}  "
              f"Saldo final: {fmt_soles(info.saldo_final)}")

if __name__ == "__main__":
    main()
