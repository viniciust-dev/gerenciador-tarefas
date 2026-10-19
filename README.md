# Gerenciador de tarefas (Python + SQLite)

Programa de terminal para organizar tarefas. Os dados ficam salvos em um banco
SQLite, então continuam lá depois que você fecha o programa.

## O que ele faz

- Adiciona tarefas com título, prioridade (baixa, média ou alta) e prazo
- Lista todas as tarefas ou só as pendentes, ordenadas por prioridade e prazo
- Edita, conclui e remove tarefas
- Valida o que o usuário digita (título vazio, prioridade e data inválidas)

## Como rodar

Requisito: Python 3.8 ou mais novo. Não precisa instalar nada além disso.

```bash
python main.py
```

## Como rodar os testes

```bash
python -m unittest -v
```

## Como o código está organizado

| Arquivo | Função |
|---|---|
| `tarefas.py` | Acesso ao banco: criar tabela, adicionar, listar, editar, concluir e remover |
| `main.py` | Menu no terminal, que só conversa com o usuário |
| `test_tarefas.py` | Testes automatizados da camada de dados |

Separar a lógica (`tarefas.py`) da interface (`main.py`) permite testar o
programa sem digitar nada no terminal.

## Consulta SQL usada na listagem

```sql
SELECT * FROM tarefas
ORDER BY concluida,
         CASE prioridade WHEN 'alta' THEN 0 WHEN 'média' THEN 1 ELSE 2 END,
         prazo IS NULL,
         prazo,
         id;
```

## Ideias para evoluir

- Filtrar por prioridade ou por prazo vencido
- Exportar as tarefas para CSV
- Trocar o menu por uma interface web com Flask
