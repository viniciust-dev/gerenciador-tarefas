"""Gerenciador de tarefas no terminal. Execute com: python main.py"""

import tarefas

MENU = """
=== Gerenciador de tarefas ===
1) Adicionar tarefa
2) Listar todas
3) Listar pendentes
4) Editar tarefa
5) Concluir tarefa
6) Remover tarefa
0) Sair
"""


def ler_id(mensagem="Número da tarefa: "):
    """Pede um id ao usuário. Devolve None se o valor não for um número."""
    try:
        return int(input(mensagem).strip())
    except ValueError:
        print("Digite apenas números.")
        return None


def mostrar(lista):
    if not lista:
        print("Nenhuma tarefa encontrada.")
        return
    for t in lista:
        marca = "x" if t["concluida"] else " "
        prazo = tarefas.formatar_prazo(t["prazo"])
        print(f"[{marca}] #{t['id']} {t['titulo']} | prioridade: {t['prioridade']} | prazo: {prazo}")


def adicionar(conn):
    titulo = input("Título: ")
    prioridade = input("Prioridade (baixa/média/alta) [média]: ") or "média"
    prazo = input("Prazo (DD/MM/AAAA, opcional): ")
    novo_id = tarefas.adicionar(conn, titulo, prioridade, prazo)
    print(f"Tarefa #{novo_id} criada.")


def editar(conn):
    id_tarefa = ler_id()
    if id_tarefa is None:
        return
    print("Deixe em branco o que não quiser mudar. Digite - no prazo para limpá-lo.")
    titulo = input("Novo título: ").strip() or None
    prioridade = input("Nova prioridade: ").strip() or None
    prazo = input("Novo prazo (DD/MM/AAAA): ").strip()
    if prazo == "-":
        prazo = ""          # texto vazio limpa o prazo
    elif prazo == "":
        prazo = None        # None mantém o prazo atual
    if tarefas.editar(conn, id_tarefa, titulo, prioridade, prazo):
        print("Tarefa atualizada.")
    else:
        print("Tarefa não encontrada.")


def concluir(conn):
    id_tarefa = ler_id()
    if id_tarefa is not None:
        print("Tarefa concluída." if tarefas.concluir(conn, id_tarefa) else "Tarefa não encontrada.")


def remover(conn):
    id_tarefa = ler_id()
    if id_tarefa is not None:
        print("Tarefa removida." if tarefas.remover(conn, id_tarefa) else "Tarefa não encontrada.")


def main():
    conn = tarefas.conectar()
    acoes = {
        "1": lambda: adicionar(conn),
        "2": lambda: mostrar(tarefas.listar(conn)),
        "3": lambda: mostrar(tarefas.listar(conn, apenas_pendentes=True)),
        "4": lambda: editar(conn),
        "5": lambda: concluir(conn),
        "6": lambda: remover(conn),
    }
    while True:
        print(MENU)
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Até logo!")
            break
        acao = acoes.get(opcao)
        if acao is None:
            print("Opção inválida.")
            continue
        try:
            acao()
        except ValueError as erro:
            print(f"Erro: {erro}")
    conn.close()


if __name__ == "__main__":
    main()
