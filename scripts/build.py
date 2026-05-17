"""
build.py — Genera el sitio estático del Portal de Transparencia 180DC PUCP.
Diseño: editorial financial report.
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

# Mes a abreviatura corta para fechas
_MES_ABREV = {
    "01": "Ene", "02": "Feb", "03": "Mar", "04": "Abr", "05": "May",
    "06": "Jun", "07": "Jul", "08": "Ago", "09": "Set", "10": "Oct",
    "11": "Nov", "12": "Dic",
}

def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def md(s):
    return _MD_BOLD.sub(r"<strong>\1</strong>", esc(s))

def fmt_fecha_corta(fecha_str):
    """'24/03/2026' -> '24 Mar' · '13/03/2026 - 18/03/2026' -> '13–18 Mar'"""
    if not fecha_str:
        return ""
    s = str(fecha_str).strip()
    # rango
    if "-" in s and s.count("/") >= 4:
        parts = [p.strip() for p in s.split("-")]
        try:
            d1, m1, _ = parts[0].split("/")
            d2, m2, _ = parts[1].split("/")
            if m1 == m2:
                return f"{int(d1)}–{int(d2)} {_MES_ABREV.get(m1, m1)}"
            return f"{int(d1)} {_MES_ABREV.get(m1, m1)}–{int(d2)} {_MES_ABREV.get(m2, m2)}"
        except Exception:
            return s
    # individual
    parts = s.split("/")
    if len(parts) == 3:
        d, m, _ = parts
        return f"{int(d)} {_MES_ABREV.get(m, m)}"
    return s


def svg_donut(labels, values, colores, total_label, size=240):
    if not values or sum(values) == 0:
        return '<div class="chart-empty">Sin datos para mostrar</div>'
    total = sum(values)
    cx, cy = size/2, size/2
    r_out, r_in = size*0.42, size*0.42*0.66
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
        paths.append(f'<path d="{d}" fill="{c}"/>')
        start = end
    legend_rows = []
    for lbl, v, c in zip(labels, values, colores):
        pct = v/total*100
        legend_rows.append(
            f'<li>'
            f'<span class="dot" style="background:{c}"></span>'
            f'<span class="lbl">{esc(lbl)}</span>'
            f'<span class="pct">{pct:.0f}%</span>'
            f'<span class="val">{fmt_soles(v)}</span>'
            f'</li>'
        )
    return (
        f'<div class="donut-block">'
        f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet">'
        f'{"".join(paths)}'
        f'<text x="{cx}" y="{cy-6}" text-anchor="middle" font-size="10" letter-spacing="1" fill="#9CA3AF">TOTAL</text>'
        f'<text x="{cx}" y="{cy+14}" text-anchor="middle" font-size="18" font-weight="700" fill="#0A0A0A">{total_label}</text>'
        f'</svg>'
        f'<ul class="donut-legend">{"".join(legend_rows)}</ul>'
        f'</div>'
    )


def svg_barras(labels, values, colores, width=420, height=240):
    pad_l, pad_r, pad_t, pad_b = 48, 12, 24, 44
    w = width - pad_l - pad_r
    h = height - pad_t - pad_b
    max_v = max(values) if values else 1
    if max_v == 0:
        max_v = 1
    step_candidates = [10, 20, 50, 100, 200, 500, 1000, 2000]
    step = next((s for s in step_candidates if max_v/s <= 5), max_v)
    nice = math.ceil(max_v / step) * step
    n = len(values)
    bw = w / n * 0.45
    gap = w / n
    bars = []
    labels_x = []
    for i, (lbl, v, c) in enumerate(zip(labels, values, colores)):
        x = pad_l + gap*i + (gap - bw)/2
        bh = (v / nice) * h if nice > 0 else 0
        y = pad_t + h - bh
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{c}"/>'
            f'<text x="{x + bw/2:.1f}" y="{y - 8:.1f}" text-anchor="middle" '
            f'font-size="11" font-weight="700" fill="#0A0A0A">{fmt_soles(v)}</text>'
        )
        labels_x.append(
            f'<text x="{x + bw/2:.1f}" y="{pad_t + h + 24:.1f}" text-anchor="middle" '
            f'font-size="11" fill="#6B7280" font-weight="500" letter-spacing="0.3">{esc(lbl)}</text>'
        )
    yticks = []
    for k in range(5):
        val = nice * k / 4
        y = pad_t + h - (val/nice)*h
        yticks.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l+w}" y2="{y:.1f}" '
            f'stroke="#F3F4F6"/>'
            f'<text x="{pad_l-8}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#9CA3AF">{val:.0f}</text>'
        )
    # eje base
    yticks.append(f'<line x1="{pad_l}" y1="{pad_t+h:.1f}" x2="{pad_l+w}" y2="{pad_t+h:.1f}" stroke="#D1D5DB"/>')
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" preserveAspectRatio="xMidYMid meet">'
        f'<text x="{pad_l-32}" y="{pad_t-8}" font-size="10" fill="#9CA3AF" letter-spacing="1">S/</text>'
        f'{"".join(yticks)}{"".join(bars)}{"".join(labels_x)}'
        f'</svg>'
    )


def brand_mark():
    """SVG inline del 'globo' rayado de 180DC en verde."""
    return (
        '<svg class="brand-mark" viewBox="0 0 32 32" width="28" height="28" '
        'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        '<circle cx="16" cy="16" r="15" fill="none" stroke="#7AB929" stroke-width="1.5"/>'
        '<path d="M 4 11 Q 16 7 28 11" fill="none" stroke="#7AB929" stroke-width="2.2" stroke-linecap="round"/>'
        '<path d="M 3 16 Q 16 12 29 16" fill="none" stroke="#7AB929" stroke-width="2.2" stroke-linecap="round"/>'
        '<path d="M 4 21 Q 16 25 28 21" fill="none" stroke="#7AB929" stroke-width="2.2" stroke-linecap="round"/>'
        '</svg>'
    )


def nav_html(slug_actual=None):
    items = []
    items.append(
        f'<a href="../index.html"{" class=\"active\"" if slug_actual is None else ""}>Inicio</a>'
    )
    for m in MESES_CONFIG:
        cls = ' class="active"' if m["slug"] == slug_actual else ""
        items.append(f'<a href="{m["slug"]}.html"{cls}>{m["mes"]}</a>')
    return f'<nav class="main-nav">{"".join(items)}</nav>'


def nav_home():
    items = ['<a class="active" href="index.html">Inicio</a>']
    for m in MESES_CONFIG:
        items.append(f'<a href="meses/{m["slug"]}.html">{m["mes"]}</a>')
    return f'<nav class="main-nav">{"".join(items)}</nav>'


def layout(titulo, body, slug_actual=None, asset_prefix="."):
    nav = nav_home() if slug_actual is None else nav_html(slug_actual)
    home_href = "index.html" if slug_actual is None else "../index.html"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(titulo)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset_prefix}/assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner wrap">
      <a class="brand" href="{home_href}">
        {brand_mark()}
        <div class="brand-text">
          <span class="brand-name">180DC PUCP</span>
          <span class="brand-sub">Transparencia financiera</span>
        </div>
      </a>
      {nav}
      <div class="header-status">
        <span class="status-dot"></span>
        <span>Ciclo 2026-1</span>
      </div>
    </div>
  </header>
  <main class="wrap">
    {body}
  </main>
  <footer>
    <div class="wrap footer-inner">
      <div>
        <p class="footer-title">180 Degrees Consulting PUCP</p>
        <p class="footer-sub">Portal de Transparencia Financiera · Ciclo 2026-1</p>
      </div>
      <div class="footer-meta">
        <p>Información derivada del Registro de Transacciones mensual.</p>
        <p>Consultas: área financiera.</p>
      </div>
    </div>
  </footer>
</body>
</html>
"""


# =============================================================================
# Componente: fila de transacción
# =============================================================================
def render_fila(*, titulo, monto, fecha, categoria, descripcion, tipo,
                badge_txt=None):
    """tipo: 'in' | 'op' | 'inv'"""
    signo = "+" if tipo == "in" else "−"
    monto_cls = {"in": "in", "op": "op", "inv": "inv"}[tipo]
    badge_html = ""
    if badge_txt:
        badge_html = f'<span class="row-badge {monto_cls}">{esc(badge_txt)}</span>'
    fecha_corta = fmt_fecha_corta(fecha)
    meta_parts = []
    if badge_html:
        meta_parts.append(badge_html)
    if fecha_corta:
        meta_parts.append(f'<span class="row-meta-item">{esc(fecha_corta)}</span>')
    if categoria:
        meta_parts.append(f'<span class="row-meta-item">{esc(categoria)}</span>')
    meta_html = ('<div class="row-meta">'
                 + '<span class="row-sep"></span>'.join(meta_parts)
                 + '</div>') if meta_parts else ""
    return f"""
    <article class="tx-row tx-{monto_cls}">
      <div class="tx-main">
        <div class="tx-head">
          <h4 class="tx-title">{esc(titulo)}</h4>
          <div class="tx-monto {monto_cls}">{signo} {fmt_soles(monto)}</div>
        </div>
        {meta_html}
        <p class="tx-desc">{esc(descripcion)}</p>
      </div>
    </article>
    """


# =============================================================================
# Página mes
# =============================================================================
def render_mes(info: InformeMes, slug: str, narrativa: dict, xlsx_filename: str) -> str:
    # delta de saldo
    delta = info.saldo_final - info.saldo_inicial
    delta_sign = "+" if delta >= 0 else "−"
    delta_cls = "up" if delta >= 0 else "down"

    # ---- Hero saldo
    hero_saldo = f"""
    <section class="hero-saldo">
      <div class="hero-saldo-main">
        <p class="eyebrow">Saldo final del mes</p>
        <div class="hero-saldo-num">{fmt_soles(info.saldo_final)}</div>
        <p class="hero-saldo-delta {delta_cls}">
          <span class="arrow">{'↑' if delta >= 0 else '↓'}</span>
          {delta_sign} {fmt_soles(abs(delta))} vs. saldo inicial
        </p>
      </div>
      <div class="hero-saldo-calc">
        <p class="eyebrow">Cálculo</p>
        <dl class="calc-list">
          <div><dt>Saldo inicial</dt><dd>{fmt_soles(info.saldo_inicial)}</dd></div>
          <div class="op"><dt><span class="op-sign verde">+</span> Ingresos</dt><dd>{fmt_soles(info.ingresos)}</dd></div>
          <div class="op"><dt><span class="op-sign rojo">−</span> Egresos operativos</dt><dd>{fmt_soles(info.egresos_op)}</dd></div>
          <div class="op"><dt><span class="op-sign ambar">−</span> Inversión IME</dt><dd>{fmt_soles(info.inversion)}</dd></div>
          <div class="total"><dt>Saldo final</dt><dd>{fmt_soles(info.saldo_final)}</dd></div>
        </dl>
      </div>
    </section>
    """

    # ---- Stat strip
    stat_strip = f"""
    <div class="stat-strip">
      <div class="stat">
        <span class="stat-label">Saldo inicial</span>
        <span class="stat-value">{fmt_soles(info.saldo_inicial)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Ingresos</span>
        <span class="stat-value verde">{fmt_soles(info.ingresos)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Egresos operativos</span>
        <span class="stat-value rojo">{fmt_soles(info.egresos_op)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Inversión IME</span>
        <span class="stat-value ambar">{fmt_soles(info.inversion)}</span>
      </div>
    </div>
    """

    # ---- Ingresos
    fuentes = narrativa.get("fuentes_ingresos", [])
    filas_ingreso = []
    for f in fuentes:
        filas_ingreso.append(render_fila(
            titulo=f['nombre'],
            monto=f['monto'],
            fecha=f.get('fecha', ''),
            categoria='',
            descripcion=f.get('detalle', ''),
            tipo='in',
            badge_txt='Ingreso',
        ))
    if not filas_ingreso:
        filas_ingreso.append('<p class="muted">No se registran ingresos en el mes.</p>')

    # ---- Egresos
    egresos_cfg = sorted(narrativa.get("egresos", []), key=lambda e: e["monto"], reverse=True)
    filas_egreso = []
    for e in egresos_cfg:
        tipo = 'inv' if e.get('es_inversion') else 'op'
        badge = 'Inversión IME' if e.get('es_inversion') else 'Operativo'
        filas_egreso.append(render_fila(
            titulo=e['titulo'],
            monto=e['monto'],
            fecha=e.get('fecha', ''),
            categoria=e.get('categoria_ui', ''),
            descripcion=e.get('para_que', ''),
            tipo=tipo,
            badge_txt=badge,
        ))
    if not filas_egreso:
        filas_egreso.append('<p class="muted">No se registran egresos en el mes.</p>')

    # ---- Subtotal headers
    egresos_total = info.egresos_op + info.inversion

    # ---- Charts
    dist = {}
    for e in egresos_cfg:
        c = e.get("categoria_ui", "Otros")
        dist[c] = dist.get(c, 0) + e["monto"]
    dist_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)
    dist_labels = [k for k,_ in dist_items]
    dist_data = [v for _,v in dist_items]
    paleta = ["#7AB929", "#1F2937", "#F59E0B", "#3B82F6", "#DC2626", "#8B5CF6", "#6B7280"]
    color_list = [paleta[i % len(paleta)] for i in range(len(dist_labels))]
    donut_svg = svg_donut(dist_labels, dist_data, color_list,
                          fmt_soles(sum(dist_data)) if dist_data else "S/ 0")

    cmp_labels = ["Ingresos", "Egresos op.", "Inversión"]
    cmp_values = [info.ingresos, info.egresos_op, info.inversion]
    cmp_colors = ["#7AB929", "#DC2626", "#F59E0B"]
    barras_svg = svg_barras(cmp_labels, cmp_values, cmp_colors)

    # ---- Análisis (pull-quote style)
    nota = narrativa.get("nota_cierre", "")
    cierre_html = ""
    if nota:
        cierre_html = f"""
        <section class="analisis-section">
          <p class="section-eyebrow">Análisis</p>
          <h3 class="section-title-big">Comentario del mes</h3>
          <blockquote class="pullquote">{md(nota)}</blockquote>
        </section>
        """

    # ---- Descarga
    descarga_html = f"""
    <div class="descarga">
      <div class="descarga-info">
        <p class="eyebrow">Archivo fuente</p>
        <h4>Registro de Transacciones — {info.mes} {info.ciclo}</h4>
        <p>Verifica línea por línea. Los datos del informe se generan
           automáticamente a partir de este archivo.</p>
      </div>
      <a class="btn-descarga" href="../downloads/{esc(xlsx_filename)}" download>
        <span>Descargar Excel</span>
        <span class="btn-arrow">↓</span>
      </a>
    </div>
    """

    # ---- Info box inversión
    info_box_inv = ""
    if info.inversion > 0:
        info_box_inv = """
        <div class="info-box">
          <strong>Inversión IME</strong>
          Compras de bienes durables que permanecen como activo de la
          agrupación (polos institucionales, photochecks, equipamiento)
          y se reutilizan en ciclos siguientes. Se reporta separada del
          gasto operativo para no distorsionar el resultado del mes.
        </div>
        """

    body = f"""
    <div class="breadcrumb">
      <a href="../index.html">Inicio</a>
      <span class="bc-sep">/</span>
      <span>{info.mes} 2026-1</span>
    </div>

    <header class="page-hero">
      <p class="eyebrow">Ciclo 2026-1 · Reporte mensual</p>
      <h1 class="page-title">{info.mes}</h1>
      <p class="page-meta">
        Responsable de actualización: <strong>{esc(info.responsable)}</strong>
        <span class="meta-sep">·</span>
        Última actualización: <strong>{esc(info.actualizacion)}</strong>
      </p>
    </header>

    {hero_saldo}
    {stat_strip}

    <section class="section">
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Movimientos</p>
          <h3 class="section-title-big">Ingresos del mes</h3>
        </div>
        <div class="section-total verde">
          <span class="total-label">Total</span>
          <span class="total-value">+ {fmt_soles(info.ingresos)}</span>
        </div>
      </div>
      <div class="tx-list">{''.join(filas_ingreso)}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Movimientos</p>
          <h3 class="section-title-big">Egresos del mes</h3>
        </div>
        <div class="section-total rojo">
          <span class="total-label">Total</span>
          <span class="total-value">− {fmt_soles(egresos_total)}</span>
        </div>
      </div>
      {info_box_inv}
      <div class="tx-list">{''.join(filas_egreso)}</div>
    </section>

    <section class="section">
      <p class="section-eyebrow">Visualización</p>
      <h3 class="section-title-big">Distribución del gasto</h3>
      <div class="chart-grid">
        <div class="chart-block">
          <h4 class="chart-title">Egresos por categoría</h4>
          {donut_svg}
        </div>
        <div class="chart-block">
          <h4 class="chart-title">Comparativo del mes</h4>
          {barras_svg}
        </div>
      </div>
    </section>

    {cierre_html}

    <section class="section">
      <p class="section-eyebrow">Verificación</p>
      <h3 class="section-title-big">Datos abiertos</h3>
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
    delta_ciclo = saldo_actual - saldo_inicio
    delta_sign = "+" if delta_ciclo >= 0 else "−"
    delta_cls = "up" if delta_ciclo >= 0 else "down"

    # ---- Hero
    hero = f"""
    <section class="index-hero">
      <p class="eyebrow">180 Degrees Consulting PUCP</p>
      <h1 class="hero-title">Reporte de transparencia financiera</h1>
      <p class="hero-lead">
        Movimiento financiero detallado de la agrupación durante el ciclo
        académico 2026-1. Cada transacción cuenta con su descripción y el
        archivo fuente está disponible para verificación.
      </p>
      <div class="hero-saldo-strip">
        <div>
          <p class="eyebrow">Saldo actual</p>
          <div class="hero-saldo-big">{fmt_soles(saldo_actual)}</div>
          <p class="hero-saldo-delta {delta_cls}">
            <span class="arrow">{'↑' if delta_ciclo >= 0 else '↓'}</span>
            {delta_sign} {fmt_soles(abs(delta_ciclo))} desde el inicio del ciclo
          </p>
        </div>
      </div>
    </section>
    """

    # ---- Stat strip
    stat_strip = f"""
    <div class="stat-strip stat-strip-index">
      <div class="stat">
        <span class="stat-label">Saldo de inicio</span>
        <span class="stat-value">{fmt_soles(saldo_inicio)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Ingresos acumulados</span>
        <span class="stat-value verde">{fmt_soles(total_ing)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Egresos operativos</span>
        <span class="stat-value rojo">{fmt_soles(total_eg)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Inversión IME</span>
        <span class="stat-value ambar">{fmt_soles(total_inv)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Meses reportados</span>
        <span class="stat-value">{len(infos)}</span>
      </div>
    </div>
    """

    # ---- Month cards
    cards = []
    for idx, (info, cfg) in enumerate(zip(infos, MESES_CONFIG), 1):
        delta_mes = info.saldo_final - info.saldo_inicial
        d_sign = "+" if delta_mes >= 0 else "−"
        d_cls = "up" if delta_mes >= 0 else "down"
        cards.append(f"""
        <a class="mes-card" href="meses/{cfg['slug']}.html">
          <div class="mes-card-head">
            <div>
              <p class="eyebrow">Mes {idx:02d} · 2026-1</p>
              <h3 class="mes-card-title">{info.mes}</h3>
            </div>
            <span class="mes-arrow">→</span>
          </div>
          <div class="mes-card-saldo">
            <p class="eyebrow">Saldo final</p>
            <div class="mes-saldo-num">{fmt_soles(info.saldo_final)}</div>
            <p class="mes-delta {d_cls}">
              <span class="arrow">{'↑' if delta_mes >= 0 else '↓'}</span>
              {d_sign} {fmt_soles(abs(delta_mes))}
            </p>
          </div>
          <div class="mes-card-stats">
            <div>
              <span>Ingresos</span>
              <b class="verde">+ {fmt_soles(info.ingresos)}</b>
            </div>
            <div>
              <span>Egresos op.</span>
              <b class="rojo">− {fmt_soles(info.egresos_op)}</b>
            </div>
            <div>
              <span>Inversión</span>
              <b class="ambar">− {fmt_soles(info.inversion)}</b>
            </div>
          </div>
        </a>
        """)

    body = f"""
    {hero}
    {stat_strip}

    <section class="section">
      <div class="section-head">
        <div>
          <p class="section-eyebrow">Reportes</p>
          <h3 class="section-title-big">Informes mensuales</h3>
        </div>
      </div>
      <div class="meses-grid">{''.join(cards)}</div>
    </section>

    <section class="section two-col">
      <div>
        <p class="section-eyebrow">Marco contable</p>
        <h3 class="section-title-big">Metodología</h3>
        <p class="prose">
          Los montos provienen directamente del <em>Registro de Transacciones</em>
          mensual que mantiene el área financiera. Cada movimiento del archivo
          contable original tiene su correlativo en el portal, y el archivo
          fuente de cada mes está disponible para descarga, lo cual permite
          verificación línea por línea.
        </p>
        <p class="prose">
          Para consultas adicionales o detalle complementario, comunícate con
          el área financiera de la agrupación.
        </p>
      </div>
      <div>
        <p class="section-eyebrow">Definiciones</p>
        <h3 class="section-title-big">Conceptos clave</h3>
        <dl class="def-list">
          <div>
            <dt>Ingresos</dt>
            <dd>Fondos que entran a caja en el mes (membresías, donaciones, recaudaciones, patrocinios).</dd>
          </div>
          <div>
            <dt>Egresos operativos</dt>
            <dd>Consumibles del mes: bocaditos, transporte, ITF, capacitaciones, integración.</dd>
          </div>
          <div>
            <dt>Inversión IME</dt>
            <dd>Inventario / material reutilizable. Bienes durables que permanecen como activo de la agrupación.</dd>
          </div>
          <div>
            <dt>Saldo final</dt>
            <dd>Saldo inicial + Ingresos − Egresos operativos − Inversión.</dd>
          </div>
        </dl>
      </div>
    </section>
    """
    return layout("180DC PUCP · Transparencia Financiera", body,
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
