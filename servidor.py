"""Etapa 4: nosso próprio servidor MCP, uma lista de tarefas.

Ele expõe os três tipos de recurso do protocolo:
  - ferramentas (tools): ações que o modelo pode pedir
  - recursos (resources): dados que o aplicativo pode ler
  - prompts: modelos de pedido prontos para o usuário

Importante: no transporte stdio, a saída padrão é o canal do protocolo.
Nunca use print() neste arquivo; para depurar, escreva em sys.stderr.
"""

import json
import sys
from pathlib import Path
from typing import TypedDict

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

ARQUIVO = Path(__file__).parent / "tarefas.json"

mcp = MCPServer(
    "Tarefas",
    instructions="Gerencia a lista de tarefas pessoais do usuário.",
    log_level="WARNING",
)


class Tarefa(TypedDict):
    """Formato de uma tarefa. Vira o esquema de saída das ferramentas."""

    id: int
    titulo: str
    concluida: bool


def carregar() -> list[Tarefa]:
    if not ARQUIVO.exists():
        return []
    return json.loads(ARQUIVO.read_text(encoding="utf-8"))


def salvar(tarefas: list[Tarefa]) -> None:
    ARQUIVO.write_text(
        json.dumps(tarefas, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# --- Ferramentas -----------------------------------------------------------
# O nome da função vira o nome da ferramenta, a docstring vira a descrição
# que o modelo lê, e as anotações de tipo viram o esquema dos argumentos.


@mcp.tool()
def adicionar_tarefa(titulo: str) -> Tarefa:
    """Adiciona uma tarefa nova à lista e devolve a tarefa criada."""
    tarefas = carregar()
    proximo_id = max((t["id"] for t in tarefas), default=0) + 1
    tarefa: Tarefa = {"id": proximo_id, "titulo": titulo, "concluida": False}
    tarefas.append(tarefa)
    salvar(tarefas)
    return tarefa


@mcp.tool()
def listar_tarefas(apenas_pendentes: bool = False) -> list[Tarefa]:
    """Lista as tarefas. Com apenas_pendentes=True, omite as concluídas."""
    tarefas = carregar()
    if apenas_pendentes:
        tarefas = [t for t in tarefas if not t["concluida"]]
    return tarefas


@mcp.tool()
def concluir_tarefa(id: int) -> Tarefa:
    """Marca como concluída a tarefa com o id informado."""
    tarefas = carregar()
    for tarefa in tarefas:
        if tarefa["id"] == id:
            tarefa["concluida"] = True
            salvar(tarefas)
            return tarefa
    # ToolError é o erro "esperado": chega ao cliente como um resultado com
    # is_error=True e esta mensagem, para o modelo ler e se corrigir.
    raise ToolError(f"Não existe tarefa com id {id}.")


# --- Recurso ---------------------------------------------------------------


@mcp.resource("tarefas://resumo")
def resumo() -> str:
    """Resumo da lista: totais e tarefas pendentes."""
    tarefas = carregar()
    pendentes = [t for t in tarefas if not t["concluida"]]
    linhas = [
        f"Total: {len(tarefas)}",
        f"Concluídas: {len(tarefas) - len(pendentes)}",
        f"Pendentes: {len(pendentes)}",
    ]
    linhas += [f"- [{t['id']}] {t['titulo']}" for t in pendentes]
    return "\n".join(linhas)


# --- Prompt ----------------------------------------------------------------


@mcp.prompt()
def planejar_dia(foco: str = "trabalho") -> str:
    """Pede um plano para o dia a partir das tarefas pendentes."""
    return (
        "Consulte minhas tarefas pendentes e monte um plano para hoje, "
        f"com foco em {foco}. Ordene por prioridade e sugira horários."
    )


if __name__ == "__main__":
    if "--http" in sys.argv:
        # Servidor de rede: fica em http://127.0.0.1:8000/mcp
        mcp.run(transport="streamable-http")
    else:
        # Padrão: stdio, iniciado pelo próprio cliente
        mcp.run()
