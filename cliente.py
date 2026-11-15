"""Etapa 5: um cliente para o nosso servidor de tarefas.

Uso:
    python cliente.py explorar
    python cliente.py adicionar "Gravar a aula 5"
    python cliente.py listar
    python cliente.py concluir 1
    python cliente.py resumo
    python cliente.py planejar estudos

Para usar o servidor de rede em vez do stdio (rode antes
"python servidor.py --http" em outro terminal):
    python cliente.py --http listar
"""

import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

SERVIDOR_STDIO = StdioServerParameters(
    command=sys.executable,
    args=[str(Path(__file__).parent / "servidor.py")],
)
SERVIDOR_HTTP = "http://127.0.0.1:8000/mcp"


def mostrar_tarefa(tarefa: dict) -> None:
    marca = "x" if tarefa["concluida"] else " "
    print(f"  [{marca}] {tarefa['id']}. {tarefa['titulo']}")


async def chamar(cliente: Client, nome: str, argumentos: dict):
    """Chama uma ferramenta. Devolve os dados, ou None se o servidor recusou."""
    resultado = await cliente.call_tool(nome, argumentos)
    if resultado.is_error:
        print(f"O servidor respondeu com erro: {resultado.content[0].text}")
        return None
    dados = resultado.structured_content
    # Uma lista não pode ser a raiz de um objeto JSON, então o SDK a embrulha
    # em {"result": [...]}. Um dicionário vem direto.
    if isinstance(dados, dict) and set(dados) == {"result"}:
        return dados["result"]
    return dados


async def explorar(cliente: Client) -> None:
    print(f"Servidor: {cliente.server_info.name}\n")

    print("Ferramentas:")
    for f in (await cliente.list_tools()).tools:
        print(f"  - {f.name}: {f.description}")

    print("\nRecursos:")
    for r in (await cliente.list_resources()).resources:
        print(f"  - {r.uri}: {r.description}")

    print("\nPrompts:")
    for p in (await cliente.list_prompts()).prompts:
        print(f"  - {p.name}: {p.description}")


async def executar(cliente: Client, comando: str, args: list[str]) -> None:
    if comando == "explorar":
        await explorar(cliente)

    elif comando == "adicionar":
        tarefa = await chamar(cliente, "adicionar_tarefa", {"titulo": " ".join(args)})
        if tarefa:
            print("Tarefa criada:")
            mostrar_tarefa(tarefa)

    elif comando == "listar":
        tarefas = await chamar(cliente, "listar_tarefas", {}) or []
        if not tarefas:
            print("Nenhuma tarefa ainda.")
        for tarefa in tarefas:
            mostrar_tarefa(tarefa)

    elif comando == "concluir":
        tarefa = await chamar(cliente, "concluir_tarefa", {"id": int(args[0])})
        if tarefa:
            print("Tarefa concluída:")
            mostrar_tarefa(tarefa)

    elif comando == "resumo":
        recurso = await cliente.read_resource("tarefas://resumo")
        print(recurso.contents[0].text)

    elif comando == "planejar":
        foco = args[0] if args else "trabalho"
        prompt = await cliente.get_prompt("planejar_dia", {"foco": foco})
        print("Texto que seria enviado ao modelo:\n")
        print(prompt.messages[0].content.text)

    else:
        print(__doc__)


async def main() -> None:
    args = sys.argv[1:]
    servidor = SERVIDOR_STDIO
    if "--http" in args:
        args.remove("--http")
        servidor = SERVIDOR_HTTP
    if not args:
        raise SystemExit(__doc__)

    async with Client(servidor) as cliente:
        await executar(cliente, args[0], args[1:])


if __name__ == "__main__":
    asyncio.run(main())
