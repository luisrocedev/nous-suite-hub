import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "suite_hub.sqlite3"

app = Flask(__name__)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                family TEXT NOT NULL,
                business_area TEXT NOT NULL,
                color_code TEXT NOT NULL,
                description TEXT NOT NULL,
                monthly_cost REAL NOT NULL,
                value_score INTEGER NOT NULL,
                complexity_score INTEGER NOT NULL,
                maturity TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS suites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mission TEXT NOT NULL,
                owner TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS suite_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suite_id INTEGER NOT NULL,
                module_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                UNIQUE(suite_id, module_id),
                FOREIGN KEY(suite_id) REFERENCES suites(id) ON DELETE CASCADE,
                FOREIGN KEY(module_id) REFERENCES modules(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS integration_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suite_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                summary_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(suite_id) REFERENCES suites(id) ON DELETE CASCADE
            );
            """
        )


def ensure_seed_data() -> None:
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) AS total FROM modules").fetchone()["total"]
        if count == 0:
            now = now_iso()
            seed_modules = [
                (
                    "SEO Avanzado",
                    "marketing",
                    "Nous | marketing - crm",
                    "deeppink",
                    "Optimiza posicionamiento orgánico y auditorías on-page.",
                    149.0,
                    82,
                    44,
                    "estable",
                    now,
                ),
                (
                    "Analítica Web",
                    "marketing",
                    "Nous | marketing - crm",
                    "palevioletred",
                    "Mide tráfico, embudos y cohortes con panel ejecutivo.",
                    119.0,
                    78,
                    37,
                    "estable",
                    now,
                ),
                (
                    "ERP Core",
                    "gestion",
                    "Nous | gestión - erp",
                    "saddlebrown",
                    "Gestión de operaciones empresariales y datos maestros.",
                    320.0,
                    91,
                    67,
                    "estable",
                    now,
                ),
                (
                    "Dashboard ERP",
                    "gestion",
                    "Nous | gestión - erp",
                    "royalblue",
                    "Panel de indicadores para dirección y control de procesos.",
                    210.0,
                    85,
                    52,
                    "beta",
                    now,
                ),
                (
                    "LMS Video",
                    "formacion",
                    "Nous | formación - lms para alumnos",
                    "lightgray",
                    "Plataforma de cursos con progreso y seguimiento del alumnado.",
                    185.0,
                    74,
                    46,
                    "estable",
                    now,
                ),
                (
                    "Foros Académicos",
                    "formacion",
                    "Nous | formación - lms para alumnos",
                    "mintcream",
                    "Espacios de debate y tutoría para campus virtual.",
                    65.0,
                    64,
                    28,
                    "estable",
                    now,
                ),
                (
                    "Gestor de CV",
                    "rrhh",
                    "Nous | personas - rrhh",
                    "paleturquoise",
                    "Pipeline de talento para selección y evaluación curricular.",
                    130.0,
                    76,
                    41,
                    "beta",
                    now,
                ),
                (
                    "Agente IA",
                    "inteligencia",
                    "Nous | inteligencia - IA",
                    "magenta",
                    "Asistente para recomendación automática y soporte de negocio.",
                    259.0,
                    88,
                    59,
                    "beta",
                    now,
                ),
                (
                    "Facturación",
                    "empresa",
                    "Nous | empresa - facturación, contabilidad",
                    "rosybrown",
                    "Módulo de facturas, cobros y conciliación contable.",
                    170.0,
                    83,
                    49,
                    "estable",
                    now,
                ),
                (
                    "Gestor de Proyectos",
                    "proyectos",
                    "Nous | proyectos - gestión de proyectos",
                    "firebrick",
                    "Planificación de tareas, hitos y recursos por equipo.",
                    145.0,
                    79,
                    43,
                    "estable",
                    now,
                ),
                (
                    "Mapas Mentales",
                    "oficina",
                    "Nous | oficina",
                    "deepskyblue",
                    "Organización visual de ideas para trabajo colaborativo.",
                    52.0,
                    60,
                    19,
                    "estable",
                    now,
                ),
                (
                    "Comparador de Código",
                    "infraestructura",
                    "Nous | infraestructura",
                    "honeydew",
                    "Comparación de versiones para auditoría técnica interna.",
                    95.0,
                    68,
                    31,
                    "estable",
                    now,
                ),
            ]
            conn.executemany(
                """
                INSERT INTO modules (
                    name, family, business_area, color_code, description,
                    monthly_cost, value_score, complexity_score, maturity, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                seed_modules,
            )

        conn.execute(
            """
            UPDATE modules
            SET business_area = REPLACE(business_area, 'jocarsa |', 'Nous |')
            WHERE business_area LIKE 'jocarsa |%'
            """
        )

        suite_count = conn.execute("SELECT COUNT(*) AS total FROM suites").fetchone()["total"]
        if suite_count == 0:
            now = now_iso()
            suite_id = conn.execute(
                """
                INSERT INTO suites (name, mission, owner, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "Suite Comercial 360",
                    "Unificar captación, operación ERP y análisis para decisiones de negocio.",
                    "Luis (DAM2)",
                    now,
                    now,
                ),
            ).lastrowid

            defaults = conn.execute(
                "SELECT id FROM modules WHERE family IN ('marketing','gestion','empresa','inteligencia')"
            ).fetchall()
            conn.executemany(
                "INSERT INTO suite_modules (suite_id, module_id, role) VALUES (?, ?, ?)",
                [(suite_id, row["id"], "core") for row in defaults[:4]],
            )


def suite_aggregate(conn: sqlite3.Connection, suite_id: int) -> dict:
    suite = conn.execute(
        "SELECT id, name, mission, owner, created_at, updated_at FROM suites WHERE id = ?",
        (suite_id,),
    ).fetchone()
    if not suite:
        raise RuntimeError("Suite no encontrada")

    modules = conn.execute(
        """
        SELECT m.id, m.name, m.family, m.business_area, m.color_code, m.description,
               m.monthly_cost, m.value_score, m.complexity_score, m.maturity, sm.role
        FROM suite_modules sm
        JOIN modules m ON m.id = sm.module_id
        WHERE sm.suite_id = ?
        ORDER BY m.family, m.name
        """,
        (suite_id,),
    ).fetchall()

    module_items = [dict(row) for row in modules]
    total_cost = round(sum(item["monthly_cost"] for item in module_items), 2)
    total_value = sum(item["value_score"] for item in module_items)
    avg_complexity = round(
        (sum(item["complexity_score"] for item in module_items) / len(module_items)) if module_items else 0,
        2,
    )

    return {
        "suite": dict(suite),
        "modules": module_items,
        "metrics": {
            "moduleCount": len(module_items),
            "totalCost": total_cost,
            "totalValue": total_value,
            "avgComplexity": avg_complexity,
        },
    }


def simulate_suite(conn: sqlite3.Connection, suite_id: int) -> dict:
    detail = suite_aggregate(conn, suite_id)
    modules = detail["modules"]

    if not modules:
        raise RuntimeError("No se puede simular una suite vacía")

    families = {m["family"] for m in modules}
    module_count = len(modules)
    total_cost = detail["metrics"]["totalCost"]
    total_value = detail["metrics"]["totalValue"]
    avg_complexity = detail["metrics"]["avgComplexity"]

    synergy_bonus = max(0, (len(families) - 1) * 8)
    integration_effort = round(avg_complexity * module_count - synergy_bonus, 2)
    annual_cost = round(total_cost * 12, 2)
    annual_value = round(total_value * 120.0, 2)
    roi_estimate = round(annual_value - annual_cost - (integration_effort * 15), 2)

    status = "ok" if roi_estimate >= 0 else "warning"

    summary = {
        "suiteId": suite_id,
        "suiteName": detail["suite"]["name"],
        "status": status,
        "families": sorted(families),
        "moduleCount": module_count,
        "integrationEffort": integration_effort,
        "annualCost": annual_cost,
        "annualEstimatedValue": annual_value,
        "estimatedROI": roi_estimate,
        "recommendation": (
            "La suite aporta retorno positivo y puede escalarse por fases."
            if status == "ok"
            else "La suite necesita simplificación o reducción de coste antes de implantarse."
        ),
    }

    conn.execute(
        "INSERT INTO integration_runs (suite_id, status, summary_json, created_at) VALUES (?, ?, ?, ?)",
        (suite_id, status, json.dumps(summary, ensure_ascii=False), now_iso()),
    )

    return summary


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/overview")
def api_overview():
    with get_db() as conn:
        module_total = conn.execute("SELECT COUNT(*) AS total FROM modules").fetchone()["total"]
        suite_total = conn.execute("SELECT COUNT(*) AS total FROM suites").fetchone()["total"]
        run_total = conn.execute("SELECT COUNT(*) AS total FROM integration_runs").fetchone()["total"]
        last_run = conn.execute(
            "SELECT summary_json, created_at FROM integration_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()

    payload = {
        "modules": module_total,
        "suites": suite_total,
        "runs": run_total,
        "lastRun": {
            "createdAt": last_run["created_at"],
            "summary": json.loads(last_run["summary_json"]),
        }
        if last_run
        else None,
    }
    return jsonify({"ok": True, "overview": payload})


@app.get("/api/catalog")
def api_catalog():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, name, family, business_area, color_code, description,
                   monthly_cost, value_score, complexity_score, maturity
            FROM modules
            ORDER BY family, name
            """
        ).fetchall()

    modules = [dict(row) for row in rows]
    families = sorted({item["family"] for item in modules})
    return jsonify({"ok": True, "families": families, "modules": modules})


@app.post("/api/modules")
def api_create_module():
    body = request.get_json(silent=True) or {}

    required = ["name", "family", "businessArea", "colorCode", "description"]
    missing = [field for field in required if not str(body.get(field, "")).strip()]
    if missing:
        return jsonify({"ok": False, "error": f"Campos obligatorios ausentes: {', '.join(missing)}"}), 400

    with get_db() as conn:
        module_id = conn.execute(
            """
            INSERT INTO modules (
                name, family, business_area, color_code, description,
                monthly_cost, value_score, complexity_score, maturity, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(body["name"]).strip(),
                str(body["family"]).strip(),
                str(body["businessArea"]).strip(),
                str(body["colorCode"]).strip(),
                str(body["description"]).strip(),
                float(body.get("monthlyCost", 0)),
                int(body.get("valueScore", 50)),
                int(body.get("complexityScore", 30)),
                str(body.get("maturity", "beta")).strip() or "beta",
                now_iso(),
            ),
        ).lastrowid

    return jsonify({"ok": True, "moduleId": module_id})


@app.get("/api/suites")
def api_list_suites():
    with get_db() as conn:
        suites = conn.execute(
            "SELECT id, name, mission, owner, created_at, updated_at FROM suites ORDER BY id DESC"
        ).fetchall()

        items = []
        for row in suites:
            detail = suite_aggregate(conn, row["id"])
            item = dict(row)
            item["metrics"] = detail["metrics"]
            items.append(item)

    return jsonify({"ok": True, "items": items})


@app.post("/api/suites")
def api_create_suite():
    body = request.get_json(silent=True) or {}

    name = str(body.get("name", "")).strip()
    mission = str(body.get("mission", "")).strip()
    owner = str(body.get("owner", "")).strip() or "Equipo DAM2"

    if not name or not mission:
        return jsonify({"ok": False, "error": "Nombre y misión son obligatorios"}), 400

    with get_db() as conn:
        suite_id = conn.execute(
            """
            INSERT INTO suites (name, mission, owner, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, mission, owner, now_iso(), now_iso()),
        ).lastrowid

    return jsonify({"ok": True, "suiteId": suite_id})


@app.get("/api/suites/<int:suite_id>")
def api_get_suite(suite_id: int):
    with get_db() as conn:
        try:
            detail = suite_aggregate(conn, suite_id)
        except RuntimeError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 404

        runs = conn.execute(
            "SELECT id, status, summary_json, created_at FROM integration_runs WHERE suite_id = ? ORDER BY id DESC LIMIT 8",
            (suite_id,),
        ).fetchall()

    run_items = []
    for row in runs:
        item = dict(row)
        item["summary"] = json.loads(item.pop("summary_json"))
        run_items.append(item)

    return jsonify({"ok": True, "detail": detail, "runs": run_items})


@app.post("/api/suites/<int:suite_id>/modules")
def api_assign_modules(suite_id: int):
    body = request.get_json(silent=True) or {}
    module_ids = body.get("moduleIds") if isinstance(body.get("moduleIds"), list) else []

    clean_ids = []
    for value in module_ids:
        try:
            clean_ids.append(int(value))
        except Exception:
            continue

    with get_db() as conn:
        exists = conn.execute("SELECT id FROM suites WHERE id = ?", (suite_id,)).fetchone()
        if not exists:
            return jsonify({"ok": False, "error": "Suite no encontrada"}), 404

        conn.execute("DELETE FROM suite_modules WHERE suite_id = ?", (suite_id,))
        for module_id in sorted(set(clean_ids)):
            conn.execute(
                "INSERT OR IGNORE INTO suite_modules (suite_id, module_id, role) VALUES (?, ?, 'core')",
                (suite_id, module_id),
            )
        conn.execute("UPDATE suites SET updated_at = ? WHERE id = ?", (now_iso(), suite_id))

    return jsonify({"ok": True})


@app.post("/api/suites/<int:suite_id>/simulate")
def api_simulate_suite(suite_id: int):
    with get_db() as conn:
        exists = conn.execute("SELECT id FROM suites WHERE id = ?", (suite_id,)).fetchone()
        if not exists:
            return jsonify({"ok": False, "error": "Suite no encontrada"}), 404

        try:
            summary = simulate_suite(conn, suite_id)
        except RuntimeError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, "summary": summary})


if __name__ == "__main__":
    init_db()
    ensure_seed_data()
    app.run(debug=True, port=5113)
