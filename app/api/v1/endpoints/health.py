from __future__ import annotations

from html import escape

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

from app.core.maintenance import get_maintenance_state
from app.core.responses import success_response

router = APIRouter(tags=["Health"])


def _root_payload() -> dict[str, object]:
    state = get_maintenance_state()
    return {
        "message": "Ynix FastAPI Core online",
        "docs": "/docs",
        "health": "/health",
        "maintenance": state.enabled,
    }


def _root_html(payload: dict[str, object]) -> HTMLResponse:
    message = escape(str(payload["message"]))
    docs = escape(str(payload["docs"]))
    health = escape(str(payload["health"]))
    maintenance = "true" if payload["maintenance"] else "false"
    status_color = "#f59e0b" if payload["maintenance"] else "#22c55e"
    status_label = "MAINTENANCE" if payload["maintenance"] else "ONLINE"

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ynix FastAPI Core</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #05070a;
      --panel: rgba(15, 23, 42, 0.92);
      --panel-border: rgba(34, 197, 94, 0.18);
      --text: #dcfce7;
      --muted: #86efac;
      --accent: #22c55e;
      --accent-2: #16a34a;
      --soft: #a7f3d0;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      color: var(--text);
      background:
        radial-gradient(circle at top, rgba(34, 197, 94, 0.16), transparent 28%),
        linear-gradient(180deg, #020409 0%, #05070a 42%, #020409 100%);
    }}
    a {{ color: #86efac; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .shell {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 18px 48px;
    }}
    .window {{
      border: 1px solid var(--panel-border);
      border-radius: 18px;
      overflow: hidden;
      background: var(--panel);
      box-shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
      backdrop-filter: blur(14px);
    }}
    .chrome {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 18px;
      border-bottom: 1px solid rgba(34, 197, 94, 0.12);
      background: rgba(2, 6, 23, 0.9);
    }}
    .dots {{ display: flex; gap: 8px; }}
    .dot {{
      width: 12px;
      height: 12px;
      border-radius: 999px;
      background: rgba(148, 163, 184, 0.45);
    }}
    .dot.red {{ background: #ef4444; }}
    .dot.yellow {{ background: #eab308; }}
    .dot.green {{ background: #22c55e; }}
    .title {{
      font-size: 12px;
      color: var(--muted);
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}
    .hero {{
      padding: 28px 24px 18px;
    }}
    .kicker {{
      color: var(--muted);
      font-size: 13px;
      letter-spacing: 0.04em;
      margin-bottom: 8px;
    }}
    h1 {{
      margin: 0 0 14px;
      font-size: clamp(30px, 6vw, 58px);
      line-height: 1.03;
      letter-spacing: -0.05em;
      color: #f0fdf4;
    }}
    .subtitle {{
      max-width: 780px;
      margin: 0 0 22px;
      color: var(--soft);
      font-size: 15px;
      line-height: 1.7;
    }}
    .status {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      border-radius: 999px;
      padding: 8px 13px;
      border: 1px solid rgba(34, 197, 94, 0.18);
      background: rgba(4, 12, 8, 0.8);
      color: #dcfce7;
      font-size: 12px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}
    .status::before {{
      content: "";
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: {status_color};
      box-shadow: 0 0 16px {status_color};
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin: 18px 0 24px;
    }}
    .card {{
      border: 1px solid rgba(34, 197, 94, 0.14);
      border-radius: 14px;
      padding: 14px 16px;
      background: rgba(1, 6, 12, 0.7);
    }}
    .label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    .value {{
      color: #ecfdf5;
      font-size: 14px;
      word-break: break-word;
    }}
    .panel {{
      margin: 0 24px 24px;
      border: 1px solid rgba(34, 197, 94, 0.16);
      border-radius: 16px;
      overflow: hidden;
      background: rgba(1, 6, 12, 0.92);
    }}
    .panel-head {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      padding: 14px 16px;
      color: #86efac;
      font-size: 12px;
      border-bottom: 1px solid rgba(34, 197, 94, 0.12);
    }}
    pre {{
      margin: 0;
      padding: 18px 16px 20px;
      overflow-x: auto;
      color: #bbf7d0;
      font-size: 13px;
      line-height: 1.7;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .key {{ color: #86efac; }}
    .string {{ color: #34d399; }}
    .bool {{ color: #fbbf24; }}
    .footer {{
      padding: 0 24px 24px;
      color: #86efac;
      font-size: 12px;
      line-height: 1.8;
    }}
    @media (max-width: 900px) {{
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 640px) {{
      .shell {{ padding: 18px 12px 28px; }}
      .hero {{ padding: 20px 14px 14px; }}
      .panel {{ margin: 0 14px 18px; }}
      .footer {{ padding: 0 14px 18px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .panel-head {{ flex-direction: column; align-items: flex-start; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="window">
      <div class="chrome">
        <div class="dots" aria-hidden="true">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
        </div>
        <div class="title">Ynix FastAPI Core</div>
      </div>
      <div class="hero">
        <div class="kicker">Base modular, console Artisan-like, migrations e observers.</div>
        <h1>{message}</h1>
        <p class="subtitle">
          Interface leve para navegar pelo core no browser com um visual mais terminal, destacando status,
          docs e caminhos mais usados.
        </p>
        <div class="status">{status_label}</div>
        <div class="grid">
          <div class="card">
            <div class="label">Docs</div>
            <div class="value">{docs}</div>
          </div>
          <div class="card">
            <div class="label">Health</div>
            <div class="value">{health}</div>
          </div>
          <div class="card">
            <div class="label">Maintenance</div>
            <div class="value">{maintenance}</div>
          </div>
          <div class="card">
            <div class="label">Mode</div>
            <div class="value">JSON + HTML</div>
          </div>
        </div>
      </div>
      <section class="panel">
        <div class="panel-head">
          <span>response.json</span>
          <span>status: 200</span>
        </div>
        <pre>{{
  <span class="key">"success"</span>: <span class="bool">true</span>,
  <span class="key">"message"</span>: <span class="string">{message!r}</span>,
  <span class="key">"data"</span>: {{
    <span class="key">"docs"</span>: <span class="string">{docs!r}</span>,
    <span class="key">"health"</span>: <span class="string">{health!r}</span>,
    <span class="key">"maintenance"</span>: <span class="bool">{maintenance}</span>
  }},
  <span class="key">"errors"</span>: <span class="bool">null</span>
}}</pre>
      </section>
      <div class="footer">
        Acesse <a href="{docs}">{docs}</a> para a documentacao e <a href="{health}">{health}</a> para status da API.
      </div>
    </section>
  </main>
</body>
</html>
"""
    return HTMLResponse(content=html)


@router.get("/health")
def health():
    state = get_maintenance_state()
    return success_response("API online", {"status": "ok", "maintenance": state.enabled})


@router.get("/")
def root(request: Request):
    payload = _root_payload()
    accept = request.headers.get("accept", "")
    if "text/html" in accept or "application/xhtml+xml" in accept:
        return _root_html(payload)
    return success_response(
        str(payload["message"]),
        {
            "docs": payload["docs"],
            "health": payload["health"],
            "maintenance": payload["maintenance"],
        },
    )


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@router.get("/service-worker.js", include_in_schema=False)
def service_worker():
    return Response(status_code=204, media_type="application/javascript")
