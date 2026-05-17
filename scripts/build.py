"""
build.py — Genera el sitio estático del Portal de Transparencia 180DC PUCP.
"""
from __future__ import annotations
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

import re
import math

_MD_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)

def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def md(s):
    return _MD_BOLD.sub(r"<strong>\1</strong>", esc(s))

def svg_donut(labels, values, colores, total_label, size=260):
    if not values or sum(values) == 0:
        return '<div class="chart-empty">Sin datos</div>'
    total = sum(values)
    cx, cy = size/2, size/2
    r_out, r_in = size*0.42, size*0.42*0.62
    paths = []
    start = -math.pi/2
    for v, c in zip(values, colores):
        frac = v/total
        end = start + frac * 2*math.pi
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
        f'<text x="{cx}" y="{cy-4}" text-anchor="middle" font-size="11" fill="#6B7280">Total</text>'
        f'<text x="{cx}" y="{cy+14}" text-anchor="middle" font-size="16" font-weight="700" fill="#1F2937">{total_label}</text>'
        f'</svg>'
        f'<ul class="donut-legend">{"".join(legend_rows)}</ul>'
        f'</div>'
    )


def svg_barras(labels, values, colores, width=420, height=260):
    pad_l, pad_r, pad_t, pad_b = 44, 16, 20, 40
    w = width - pad_l - pad_r
    h = height - pad_t - pad_b
    max_v = max(values) if values else 1
    if max_v == 0:
        max_v = 1
    step_candidates = [10, 20, 50, 100, 200, 500, 1000, 2000]
    step = next((s for s in step_candidates if max_v/s <= 5), max_v)
    nice = math.ceil(max_v / step) * step
    n = len(values)
    bw = w / n * 0.5
    gap = w / n
    bars = []
    labels_x = []
    for i, (lbl, v, c) in enumerate(zip(labels, values, colores)):
        x = pad_l + gap*i + (gap - bw)/2
        bh = (v / nice) * h if nice > 0 else 0
        y = pad_t + h - bh
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="6" fill="{c}"/>'
            f'<text x="{x + bw/2:.1f}" y="{y - 8:.1f}" text-anchor="middle" '
            f'font-size="12" font-weight="700" fill="#1F2937">{fmt_soles(v)}</text>'
        )
        labels_x.append(
            f'<text x="{x + bw/2:.1f}" y="{pad_t + h + 22:.1f}" text-anchor="middle" '
            f'font-size="12" fill="#4B5563" font-weight="500">{esc(lbl)}</text>'
        )
    yticks = []
    for k in range(5):
        val = nice * k / 4
        y = pad_t + h - (val/nice)*h
        yticks.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l+w}" y2="{y:.1f}" '
            f'stroke="#E5E7EB" stroke-dasharray="2,3"/>'
            f'<text x="{pad_l-8}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#9CA3AF">S/ {val:.0f}</text>'
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset_prefix}/assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="wrap">
      <div class="brand">
        <div class="brand-text">
          <h1>Portal de Transparencia Financiera</h1>
          <p>180 Degrees Consulting PUCP · Ciclo 2026-1</p>
        </div>
      </div>
      {nav}
    </div>
  </header>
  <main class="wrap">
    {body}
  </main>
  <footer>
    <div class="wrap">
      <p><strong>180 Degrees Consulting PUCP</strong> · Portal de Transparencia Financiera</p>
      <p class="footer-muted">Generado a partir del Registro de Transacciones mensual del área financiera.</p>
    </div>
  </footer>
</body>
</html>
"""

# =============================================================================
# Página mes
# =============================================================================
def render_mes(info: InformeMes, slug: str, narrativa: dict, xlsx_filename: str) -> str:
    kpis_html = f"""
    <div class="kpis">
      <div class="kpi"><div class="label">Saldo inicial</div><div class="value">{fmt_soles(info.saldo_inicial)}</div></div>
      <div class="kpi verde"><div class="label">Ingresos</div><div class="value">{fmt_soles(info.ingresos)}</div></div>
      <div class="kpi rojo"><div class="label">Egresos operativos</div><div class="value">{fmt_soles(info.egresos_op)}</div></div>
      <div class="kpi ambar"><div class="label">Inversión IME</div><div class="value">{fmt_soles(info.inversion)}</div></div>
      <div class="kpi azul"><div class="label">Saldo final</div><div class="value">{fmt_soles(info.saldo_final)}</div></div>
    </div>
    """

    ecuacion_html = f"""
    <div class="ecuacion">
      <p class="ecuacion-titulo">Cálculo del saldo final</p>
      <div class="form">
        <span class="op-val">{fmt_soles(info.saldo_inicial)}</span>
        <span class="op-sign verde">+</span>
        <span class="op-val">{fmt_soles(info.ingresos)}</span>
        <span class="op-sign rojo">−</span>
        <span class="op-val">{fmt_soles(info.egresos_op)}</span>
        <span class="op-sign ambar">−</span>
        <span class="op-val">{fmt_soles(info.inversion)}</span>
        <span class="op-sign">=</span>
        <span class="op-result">{fmt_soles(info.saldo_final)}</span>
      </div>
      <p class="ecuacion-leyenda">Saldo inicial + Ingresos − Egresos operativos − Inversión</p>
    </div>
    """

    info_box = ""
    if info.inversion > 0:
        info_box = """
        <div class="info-box">
          <strong>Sobre la Inversión IME:</strong>
          A diferencia de un gasto operativo —que se consume durante el mes—
          una inversión corresponde a bienes durables que permanecen como
          activo de la agrupación y se reutilizan en ciclos posteriores
          (polos institucionales, photochecks, equipamiento). Se reporta
          separada para no distorsionar el resultado operativo del mes.
        </div>
        """

    fuentes = narrativa.get("fuentes_ingresos", [])
    cards_ingreso = []
    for f in fuentes:
        cards_ingreso.append(f"""
        <article class="card ingreso">
          <div class="top">
            <h3>{esc(f['nombre'])}</h3>
            <div class="monto">+ {fmt_soles(f['monto'])}</div>
          </div>
          <p class="card-text">{esc(f.get('detalle',''))}</p>
        </article>
        """)
    if not cards_ingreso:
        cards_ingreso.append('<p class="muted">No se registran fuentes de ingreso descritas para este mes.</p>')

    egresos_cfg = narrativa.get("egresos", [])
    egresos_cfg = sorted(egresos_cfg, key=lambda e: e["monto"], reverse=True)
    cards_eg = []
    for e in egresos_cfg:
        cls = "inversion" if e.get("es_inversion") else ""
        badge_cls = "inv" if e.get("es_inversion") else "op"
        badge_txt = "Inversión IME" if e.get("es_inversion") else "Operativo"
        cards_eg.append(f"""
        <article class="card {cls}">
          <div class="top">
            <div class="top-info">
              <h3>{esc(e['titulo'])}</h3>
              <div class="meta">
                <span class="badge {badge_cls}">{badge_txt}</span>
                <span class="meta-sep">·</span>
                <span>{esc(e.get('fecha',''))}</span>
                <span class="meta-sep">·</span>
                <span>{esc(e.get('categoria_ui',''))}</span>
              </div>
            </div>
            <div class="monto">− {fmt_soles(e['monto'])}</div>
          </div>
          <p class="card-text">{esc(e.get('para_que',''))}</p>
        </article>
        """)
    if not cards_eg:
        cards_eg.append('<p class="muted">No hubo egresos descritos en el mes.</p>')

    dist = {}
    for e in egresos_cfg:
        c = e.get("categoria_ui", "Otros")
        dist[c] = dist.get(c, 0) + e["monto"]
    dist_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)
    dist_labels = [k for k,_ in dist_items]
    dist_data = [v for _,v in dist_items]
    colores = ["#7AB929", "#1F2937", "#F59E0B", "#3B82F6", "#EF4444", "#6B7280", "#8B5CF6"]
    color_list = [colores[i % len(colores)] for i in range(len(dist_labels))]
    donut_svg = svg_donut(dist_labels, dist_data, color_list,
                          fmt_soles(sum(dist_data)) if dist_data else "S/ 0")

    cmp_labels = ["Ingresos", "Egresos op.", "Inversión"]
    cmp_values = [info.ingresos, info.egresos_op, info.inversion]
    cmp_colors = ["#7AB929", "#EF4444", "#F59E0B"]
    barras_svg = svg_barras(cmp_labels, cmp_values, cmp_colors)

    nota = narrativa.get("nota_cierre", "")
    cierre_html = f'<section class="cierre"><h3 class="section-title">Análisis del mes</h3><p>{md(nota)}</p></section>' if nota else ""

    descarga_html = f"""
    <div class="descarga">
      <div class="descarga-info">
        <strong>Archivo fuente del mes</strong>
        <p>Toda la información proviene del Registro de Transacciones
           contable. Descárgalo para verificar línea por línea.</p>
      </div>
      <a class="btn-descarga" href="../downloads/{esc(xlsx_filename)}" download>
        Descargar Excel
        <span class="btn-arrow">↓</span>
      </a>
    </div>
    """

    body = f"""
    <section class="page-header">
      <h2>{info.mes} {info.ciclo}</h2>
      <p class="page-meta">Responsable: <strong>{esc(info.responsable)}</strong> · Última actualización: <strong>{esc(info.actualizacion)}</strong></p>
    </section>

    <section>
      <h3 class="section-title">Resumen del mes</h3>
      {kpis_html}
      {ecuacion_html}
    </section>

    <section>
      <h3 class="section-title">Ingresos</h3>
      <div class="cards">{''.join(cards_ingreso)}</div>
    </section>

    <section>
      <h3 class="section-title">Egresos</h3>
      {info_box}
      <div class="cards">{''.join(cards_eg)}</div>
    </section>

    <section>
      <h3 class="section-title">Distribución</h3>
      <div class="chart-grid">
        <div class="chart-block">
          <h4>Egresos por categoría</h4>
          {donut_svg}
        </div>
        <div class="chart-block">
          <h4>Comparativo del mes</h4>
          {barras_svg}
        </div>
      </div>
    </section>

    {cierre_html}

    <section>
      <h3 class="section-title">Datos abiertos</h3>
      {descarga_html}
    </section>
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
      <div class="kpi"><div class="label">Saldo de inicio</div><div class="value">{fmt_soles(saldo_inicio)}</div></div>
      <div class="kpi verde"><div class="label">Ingresos acumulados</div><div class="value">{fmt_soles(total_ing)}</div></div>
      <div class="kpi rojo"><div class="label">Egresos operativos</div><div class="value">{fmt_soles(total_eg)}</div></div>
      <div class="kpi ambar"><div class="label">Inversión acumulada</div><div class="value">{fmt_soles(total_inv)}</div></div>
      <div class="kpi azul"><div class="label">Saldo actual</div><div class="value">{fmt_soles(saldo_actual)}</div></div>
    </div>
    """

    cards = []
    for info, cfg in zip(infos, MESES_CONFIG):
        nota_resumen = NARRATIVA.get(info.mes, {}).get('nota_cierre', '')
        resumen_plano = re.sub(r"\*\*(.+?)\*\*", r"\1", nota_resumen)
        if len(resumen_plano) > 160:
            resumen_plano = resumen_plano[:160].rstrip() + "…"
        cards.append(f"""
        <a class="mes-card" href="meses/{cfg['slug']}.html">
          <div class="mes-card-head">
            <span class="mes-label">{info.mes} 2026-1</span>
            <span class="mes-arrow">→</span>
          </div>
          <p class="resumen">{esc(resumen_plano)}</p>
          <div class="stats">
            <div><span>Ingresos</span><b>{fmt_soles(info.ingresos)}</b></div>
            <div><span>Egresos</span><b>{fmt_soles(info.egresos_op + info.inversion)}</b></div>
            <div><span>Saldo final</span><b>{fmt_soles(info.saldo_final)}</b></div>
          </div>
        </a>
        """)

    body = f"""
    <section class="hero">
      <h2>Información financiera abierta y verificable</h2>
      <p>
        Este portal reporta mes a mes el movimiento financiero de la
        agrupación durante el ciclo 2026-1. Cada movimiento contable cuenta
        con su descripción correspondiente y el archivo fuente está
        disponible para descarga.
      </p>
    </section>

    <section>
      <h3 class="section-title">Indicadores acumulados del ciclo</h3>
      {kpis}
      <div class="info-box">
        <strong>Sobre la Inversión IME:</strong>
        Separamos del gasto regular las compras de bienes durables que se
        mantienen como activo de la agrupación y se reutilizan en ciclos
        posteriores (polos, photochecks, equipamiento). Esto evita que un
        mes con compras de inventario aparezca como deficitario.
      </div>
    </section>

    <section>
      <h3 class="section-title">Informes mensuales</h3>
      <div class="meses-grid">{''.join(cards)}</div>
    </section>

    <section>
      <h3 class="section-title">Metodología</h3>
      <p class="prose">
        Los montos provienen directamente del <em>Registro de Transacciones</em>
        mensual que mantiene el área financiera. Cada movimiento del archivo
        contable original tiene su correlativo en el portal. El archivo fuente
        de cada mes puede descargarse desde su página correspondiente para
        verificación línea por línea. Para consultas adicionales, comunícate
        con el área financiera.
      </p>
    </section>
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

    print("\n=== Cuadre ===")
    for info in infos:
        print(f"{info.mes:6s}  Ingresos: {fmt_soles(info.ingresos)}  "
              f"Egresos op.: {fmt_soles(info.egresos_op)}  "
              f"Inv: {fmt_soles(info.inversion)}  "
              f"Saldo final: {fmt_soles(info.saldo_final)}")

if __name__ == "__main__":
    main()
