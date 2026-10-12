"""
Control local de intentos de clasificación.

No importa LangGraph ni ejecuta OpenAI.
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_DEFAULT = BASE_DIR / ".runtime" / "ejecuciones.sqlite3"


def reservar_ejecucion(
    cui: str,
    db_path=None,
    instante=None,
    max_por_dia: int = 2,
    espera_minutos: int = 60,
) -> int:

    cui = str(cui).strip()

    if not (len(cui) == 7 and cui.isascii() and cui.isdigit()):
        raise ValueError("CUI invalido.")

    if max_por_dia < 1 or espera_minutos < 1:
        raise ValueError("Limites invalidos.")

    ahora = instante or datetime.now(timezone.utc)

    if ahora.tzinfo is None:
        raise ValueError("Se requiere fecha con zona horaria.")

    ahora = ahora.astimezone(timezone.utc)

    inicio_dia = ahora.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    fin_dia = inicio_dia + timedelta(days=1)
    inicio_espera = ahora - timedelta(minutes=espera_minutos)

    def fecha(valor):
        return valor.isoformat(timespec="seconds")

    ruta = Path(db_path) if db_path else DB_DEFAULT
    ruta.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(
        str(ruta),
        timeout=15,
        isolation_level=None,
    )

    try:
        conexion.execute("BEGIN IMMEDIATE")

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS ejecuciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cui TEXT NOT NULL,
                instante TEXT NOT NULL
            )
        """)

        cantidad = conexion.execute(
            """
            SELECT COUNT(*)
            FROM ejecuciones
            WHERE instante >= ? AND instante < ?
            """,
            (fecha(inicio_dia), fecha(fin_dia)),
        ).fetchone()[0]

        if cantidad >= max_por_dia:
            raise PermissionError(
                "Se alcanzo el limite diario de intentos."
            )

        repetido = conexion.execute(
            """
            SELECT 1
            FROM ejecuciones
            WHERE cui = ? AND instante >= ?
            LIMIT 1
            """,
            (cui, fecha(inicio_espera)),
        ).fetchone()

        if repetido:
            raise PermissionError(
                "Este CUI fue solicitado recientemente."
            )

        cursor = conexion.execute(
            """
            INSERT INTO ejecuciones (cui, instante)
            VALUES (?, ?)
            """,
            (cui, fecha(ahora)),
        )

        identificador = cursor.lastrowid
        conexion.execute("COMMIT")

        return identificador

    except Exception:
        if conexion.in_transaction:
            conexion.execute("ROLLBACK")
        raise

    finally:
        conexion.close()
