"""Camada de dados do gerenciador de tarefas (SQLite).

Todas as funções recebem uma conexão aberta, o que facilita os testes
(basta usar um banco em memória).
"""

import sqlite3
from datetime import date, datetime

PRIORIDADES = ("baixa", "média", "alta")


def conectar(caminho="tarefas.db"):
    """Abre (e cria, se preciso) o banco de dados de tarefas."""
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tarefas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo     TEXT    NOT NULL,
            prioridade TEXT    NOT NULL
                       CHECK (prioridade IN ('baixa', 'média', 'alta')),
            prazo      TEXT,
            concluida  INTEGER NOT NULL DEFAULT 0,
            criada_em  TEXT    NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def converter_prazo(texto):
    """Converte 'DD/MM/AAAA' para 'AAAA-MM-DD'. Texto vazio vira None."""
    texto = (texto or "").strip()
    if not texto:
        return None
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date().isoformat()
    except ValueError:
        raise ValueError("Prazo inválido. Use o formato DD/MM/AAAA.") from None


def formatar_prazo(iso):
    """Converte 'AAAA-MM-DD' para 'DD/MM/AAAA'."""
    if not iso:
        return "sem prazo"
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")


def _validar_titulo(titulo):
    titulo = (titulo or "").strip()
    if not titulo:
        raise ValueError("O título não pode ficar vazio.")
    return titulo


def _validar_prioridade(prioridade):
    prioridade = (prioridade or "").strip().lower()
    if prioridade not in PRIORIDADES:
        raise ValueError("Prioridade inválida. Use: " + ", ".join(PRIORIDADES) + ".")
    return prioridade


def adicionar(conn, titulo, prioridade="média", prazo=None):
    """Cria uma tarefa e devolve o id dela. O prazo vem em DD/MM/AAAA."""
    titulo = _validar_titulo(titulo)
    prioridade = _validar_prioridade(prioridade)
    prazo_iso = converter_prazo(prazo)
    cursor = conn.execute(
        "INSERT INTO tarefas (titulo, prioridade, prazo, criada_em) VALUES (?, ?, ?, ?)",
        (titulo, prioridade, prazo_iso, date.today().isoformat()),
    )
    conn.commit()
    return cursor.lastrowid


def listar(conn, apenas_pendentes=False):
    """Lista tarefas: pendentes primeiro, depois por prioridade e prazo."""
    consulta = "SELECT * FROM tarefas"
    if apenas_pendentes:
        consulta += " WHERE concluida = 0"
    consulta += """
        ORDER BY concluida,
                 CASE prioridade WHEN 'alta' THEN 0 WHEN 'média' THEN 1 ELSE 2 END,
                 prazo IS NULL,
                 prazo,
                 id
    """
    return conn.execute(consulta).fetchall()


def concluir(conn, id_tarefa):
    """Marca como concluída. Devolve False se o id não existir."""
    cursor = conn.execute("UPDATE tarefas SET concluida = 1 WHERE id = ?", (id_tarefa,))
    conn.commit()
    return cursor.rowcount > 0


def editar(conn, id_tarefa, titulo=None, prioridade=None, prazo=None):
    """Altera só os campos informados. Devolve False se o id não existir.

    Para limpar o prazo, passe prazo="" (texto vazio).
    """
    campos, valores = [], []
    if titulo is not None:
        campos.append("titulo = ?")
        valores.append(_validar_titulo(titulo))
    if prioridade is not None:
        campos.append("prioridade = ?")
        valores.append(_validar_prioridade(prioridade))
    if prazo is not None:
        campos.append("prazo = ?")
        valores.append(converter_prazo(prazo))
    if not campos:
        raise ValueError("Informe ao menos um campo para editar.")
    valores.append(id_tarefa)
    cursor = conn.execute(
        "UPDATE tarefas SET " + ", ".join(campos) + " WHERE id = ?", valores
    )
    conn.commit()
    return cursor.rowcount > 0


def remover(conn, id_tarefa):
    """Apaga a tarefa. Devolve False se o id não existir."""
    cursor = conn.execute("DELETE FROM tarefas WHERE id = ?", (id_tarefa,))
    conn.commit()
    return cursor.rowcount > 0
