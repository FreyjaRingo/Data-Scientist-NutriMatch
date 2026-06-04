from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "final_datasets" / "train_ready_dataset.csv"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
DASHBOARD_PATH = DASHBOARD_DIR / "nutrimatch_data_science_dashboard.html"


def value_counts_records(df: pd.DataFrame, column: str, limit: int = 12) -> list[dict[str, object]]:
    if column not in df.columns:
        return []
    counts = df[column].fillna("unknown").astype(str).value_counts().head(limit)
    return [{"label": str(label), "value": int(value)} for label, value in counts.items()]


def build_dashboard() -> None:
    df = pd.read_csv(DATASET_PATH)
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

    table_columns = [
        "food_id",
        "food_name",
        "calories_100g",
        "protein_100g",
        "food_category",
        "recommendation_item_type",
        "pairing_group",
        "meal_template_role",
        "primary_meal_time",
        "halal_status",
        "meal_combo_valid",
        "image_url",
    ]
    records = df[table_columns].fillna("").to_dict(orient="records")
    payload = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "metrics": {
            "halal_candidate": int((df["halal_status"] == "halal_candidate").sum()),
            "image_refreshed": int((df["image_url_status"] == "refreshed").sum()),
            "meal_combo_valid": int(df["meal_combo_valid"].astype(str).str.lower().eq("true").sum()),
            "avg_calories": round(float(df["calories_100g"].mean()), 1),
        },
        "charts": {
            "pairing_group": value_counts_records(df, "pairing_group"),
            "meal_template_role": value_counts_records(df, "meal_template_role"),
            "halal_status": value_counts_records(df, "halal_status"),
            "primary_meal_time": value_counts_records(df, "primary_meal_time"),
        },
        "records": records,
    }

    html = f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NutriMatch Data Science Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #667085;
      --line: #d8dee9;
      --panel: #ffffff;
      --bg: #f5f7fb;
      --accent: #0f766e;
      --accent-2: #2563eb;
      --warn: #b45309;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }}
    header {{
      padding: 28px 32px 16px;
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 28px;
      letter-spacing: 0;
    }}
    .subhead {{
      color: var(--muted);
      font-size: 14px;
      margin: 0;
    }}
    main {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 24px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .metric, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .metric .label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .metric .value {{
      margin-top: 8px;
      font-size: 28px;
      font-weight: 700;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }}
    .panel h2 {{
      margin: 0 0 14px;
      font-size: 16px;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: minmax(110px, 190px) 1fr 46px;
      gap: 10px;
      align-items: center;
      margin: 8px 0;
      font-size: 13px;
    }}
    .bar-track {{
      height: 10px;
      border-radius: 999px;
      background: #e7ebf2;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      border-radius: 999px;
      background: var(--accent);
    }}
    .filters {{
      display: grid;
      grid-template-columns: 1.4fr repeat(4, minmax(130px, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }}
    input, select {{
      width: 100%;
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px 10px;
      background: #fff;
      color: var(--ink);
      font-size: 14px;
    }}
    .table-wrap {{
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 1020px;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid #edf0f5;
      text-align: left;
      font-size: 13px;
      vertical-align: middle;
    }}
    th {{
      position: sticky;
      top: 0;
      background: #fbfcff;
      z-index: 1;
      color: #344054;
      font-weight: 700;
    }}
    .thumb {{
      width: 44px;
      height: 44px;
      object-fit: cover;
      border-radius: 6px;
      border: 1px solid var(--line);
      background: #eef2f6;
    }}
    .status {{
      display: inline-block;
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      background: #e7f8f5;
      color: #0f766e;
      white-space: nowrap;
    }}
    .status.warn {{
      background: #fff7ed;
      color: var(--warn);
    }}
    @media (max-width: 900px) {{
      main {{ padding: 16px; }}
      .metrics, .grid, .filters {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>NutriMatch Data Science Dashboard</h1>
    <p class="subhead">Dataset train-ready v6, image URL audit, meal pairing, halal guardrail, dan ringkasan feature engineering.</p>
  </header>
  <main>
    <section class="metrics" id="metrics"></section>
    <section class="grid" id="charts"></section>
    <section class="panel">
      <h2>Food Explorer</h2>
      <div class="filters">
        <input id="search" placeholder="Cari makanan, kategori, pairing...">
        <select id="meal"></select>
        <select id="halal"></select>
        <select id="pairing"></select>
        <select id="combo"></select>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Image</th>
              <th>Food</th>
              <th>Calories</th>
              <th>Protein</th>
              <th>Category</th>
              <th>Role</th>
              <th>Pairing</th>
              <th>Meal</th>
              <th>Halal</th>
              <th>Combo</th>
            </tr>
          </thead>
          <tbody id="rows"></tbody>
        </table>
      </div>
    </section>
  </main>
  <script>
    const data = {json.dumps(payload, ensure_ascii=False)};
    const rowsEl = document.getElementById('rows');
    const searchEl = document.getElementById('search');
    const filters = {{
      meal: document.getElementById('meal'),
      halal: document.getElementById('halal'),
      pairing: document.getElementById('pairing'),
      combo: document.getElementById('combo')
    }};

    function uniq(key) {{
      return [...new Set(data.records.map(row => String(row[key] || '')))].filter(Boolean).sort();
    }}
    function fillSelect(el, label, values) {{
      el.innerHTML = `<option value="">${{label}}</option>` + values.map(value => `<option value="${{value}}">${{value}}</option>`).join('');
    }}
    fillSelect(filters.meal, 'Semua meal', uniq('primary_meal_time'));
    fillSelect(filters.halal, 'Semua halal', uniq('halal_status'));
    fillSelect(filters.pairing, 'Semua pairing', uniq('pairing_group'));
    fillSelect(filters.combo, 'Semua combo', uniq('meal_combo_valid'));

    function renderMetrics() {{
      const items = [
        ['Rows', data.rows],
        ['Kolom', data.columns],
        ['Halal candidate', data.metrics.halal_candidate],
        ['Image refreshed', data.metrics.image_refreshed],
        ['Combo valid', data.metrics.meal_combo_valid],
        ['Avg calories', data.metrics.avg_calories]
      ];
      document.getElementById('metrics').innerHTML = items.map(([label, value]) => `
        <div class="metric"><div class="label">${{label}}</div><div class="value">${{value}}</div></div>
      `).join('');
    }}

    function renderCharts() {{
      const chartTitles = {{
        pairing_group: 'Pairing Group',
        meal_template_role: 'Meal Template Role',
        halal_status: 'Halal Status',
        primary_meal_time: 'Primary Meal Time'
      }};
      const html = Object.entries(data.charts).map(([key, values]) => {{
        const max = Math.max(...values.map(item => item.value), 1);
        return `<div class="panel"><h2>${{chartTitles[key]}}</h2>` + values.map(item => `
          <div class="bar-row">
            <div>${{item.label}}</div>
            <div class="bar-track"><div class="bar-fill" style="width: ${{(item.value / max) * 100}}%"></div></div>
            <div>${{item.value}}</div>
          </div>
        `).join('') + `</div>`;
      }}).join('');
      document.getElementById('charts').innerHTML = html;
    }}

    function renderRows() {{
      const query = searchEl.value.toLowerCase();
      const subset = data.records.filter(row => {{
        const text = Object.values(row).join(' ').toLowerCase();
        return (!query || text.includes(query))
          && (!filters.meal.value || row.primary_meal_time === filters.meal.value)
          && (!filters.halal.value || row.halal_status === filters.halal.value)
          && (!filters.pairing.value || row.pairing_group === filters.pairing.value)
          && (!filters.combo.value || String(row.meal_combo_valid) === filters.combo.value);
      }}).slice(0, 180);
      rowsEl.innerHTML = subset.map(row => `
        <tr>
          <td><img class="thumb" src="${{row.image_url}}" alt="${{row.food_name}}"></td>
          <td><strong>${{row.food_name}}</strong><br><span style="color: var(--muted)">${{row.food_id}}</span></td>
          <td>${{row.calories_100g}}</td>
          <td>${{row.protein_100g}}</td>
          <td>${{row.food_category}}</td>
          <td>${{row.meal_template_role}}</td>
          <td>${{row.pairing_group}}</td>
          <td>${{row.primary_meal_time}}</td>
          <td><span class="status ${{row.halal_status === 'halal_candidate' ? '' : 'warn'}}">${{row.halal_status}}</span></td>
          <td>${{row.meal_combo_valid}}</td>
        </tr>
      `).join('');
    }}

    renderMetrics();
    renderCharts();
    renderRows();
    searchEl.addEventListener('input', renderRows);
    Object.values(filters).forEach(el => el.addEventListener('change', renderRows));
  </script>
</body>
</html>
"""
    DASHBOARD_PATH.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    build_dashboard()
    print(f"Dashboard: {DASHBOARD_PATH}")
