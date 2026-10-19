import unittest

import tarefas


class TestTarefas(unittest.TestCase):
    def setUp(self):
        self.conn = tarefas.conectar(":memory:")

    def tearDown(self):
        self.conn.close()

    def test_adicionar_e_listar(self):
        id_tarefa = tarefas.adicionar(self.conn, "Estudar SQL", "alta", "31/12/2026")
        lista = tarefas.listar(self.conn)
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0]["id"], id_tarefa)
        self.assertEqual(lista[0]["prazo"], "2026-12-31")

    def test_titulo_vazio_e_rejeitado(self):
        with self.assertRaises(ValueError):
            tarefas.adicionar(self.conn, "   ")

    def test_prioridade_invalida(self):
        with self.assertRaises(ValueError):
            tarefas.adicionar(self.conn, "Teste", "urgente")

    def test_prazo_invalido(self):
        with self.assertRaises(ValueError):
            tarefas.adicionar(self.conn, "Teste", "média", "2026-12-31")
        with self.assertRaises(ValueError):
            tarefas.adicionar(self.conn, "Teste", "média", "31/02/2026")

    def test_concluir(self):
        id_tarefa = tarefas.adicionar(self.conn, "Lavar o carro")
        self.assertTrue(tarefas.concluir(self.conn, id_tarefa))
        self.assertEqual(tarefas.listar(self.conn, apenas_pendentes=True), [])
        self.assertFalse(tarefas.concluir(self.conn, 999))

    def test_editar_parcialmente(self):
        id_tarefa = tarefas.adicionar(self.conn, "Antigo", "baixa", "01/01/2027")
        tarefas.editar(self.conn, id_tarefa, titulo="Novo")
        t = tarefas.listar(self.conn)[0]
        self.assertEqual(t["titulo"], "Novo")
        self.assertEqual(t["prioridade"], "baixa")
        self.assertEqual(t["prazo"], "2027-01-01")

    def test_editar_limpa_prazo(self):
        id_tarefa = tarefas.adicionar(self.conn, "Com prazo", "média", "01/01/2027")
        tarefas.editar(self.conn, id_tarefa, prazo="")
        self.assertIsNone(tarefas.listar(self.conn)[0]["prazo"])

    def test_editar_sem_campos(self):
        id_tarefa = tarefas.adicionar(self.conn, "Teste")
        with self.assertRaises(ValueError):
            tarefas.editar(self.conn, id_tarefa)

    def test_remover(self):
        id_tarefa = tarefas.adicionar(self.conn, "Apagar")
        self.assertTrue(tarefas.remover(self.conn, id_tarefa))
        self.assertFalse(tarefas.remover(self.conn, id_tarefa))

    def test_ordem_por_prioridade(self):
        tarefas.adicionar(self.conn, "baixa", "baixa")
        tarefas.adicionar(self.conn, "alta", "alta")
        tarefas.adicionar(self.conn, "média", "média")
        titulos = [t["titulo"] for t in tarefas.listar(self.conn)]
        self.assertEqual(titulos, ["alta", "média", "baixa"])

    def test_concluidas_vao_para_o_fim(self):
        a = tarefas.adicionar(self.conn, "alta", "alta")
        tarefas.adicionar(self.conn, "baixa", "baixa")
        tarefas.concluir(self.conn, a)
        titulos = [t["titulo"] for t in tarefas.listar(self.conn)]
        self.assertEqual(titulos, ["baixa", "alta"])


if __name__ == "__main__":
    unittest.main()
