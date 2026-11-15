"""Etapa 6 (bônus): o Claude no comando.

Até aqui, quem escolhia a ferramenta era você, digitando o comando. Agora o
programa entrega ao Claude a lista de ferramentas do servidor MCP, e é o
modelo que decide qual chamar a partir de um pedido em português.

Antes de rodar, defina a variável de ambiente ANTHROPIC_API_KEY com uma chave
criada no Claude Console. O uso da API é cobrado à parte da assinatura.

Uso:
    python chat.py
"""

import asyncio
import os
import sys
from pathlib import Path

from anthropic import AsyncAnthropic
from mcp import Client, StdioServerParameters

MODELO = os.environ.get("MODELO_CLAUDE", "claude-sonnet-5-5")

SERVIDOR = StdioServerParameters(
    command=sys.executable,
    args=[str(Path(__file__).parent / "servidor.py")],
)

SISTEMA = (
    "Você ajuda o usuário a cuidar da lista de tarefas dele. "
    "Use as ferramentas disponíveis sempre que precisar ler ou alterar a lista."
)


def para_formato_claude(ferramentas_mcp) -> list[dict]:
    """Converte as ferramentas do MCP para o formato que a API do Claude espera.

    A tradução é quase direta, e esse é o ponto do protocolo: nome, descrição
    e esquema dos argumentos já vêm prontos do servidor.
    """
    return [
        {
            "name": f.name,
            "description": f.description or "",
            "input_schema": f.input_schema,
        }
        for f in ferramentas_mcp
    ]


async def responder(claude: AsyncAnthropic, mcp: Client, ferramentas, mensagens) -> None:
    """Um turno da conversa: repete enquanto o Claude pedir ferramentas."""
    while True:
        resposta = await claude.messages.create(
            model=MODELO,
            max_tokens=1024,
            system=SISTEMA,
            tools=ferramentas,
            messages=mensagens,
        )
        mensagens.append({"role": "assistant", "content": resposta.content})

        for bloco in resposta.content:
            if bloco.type == "text" and bloco.text.strip():
                print(f"\nClaude: {bloco.text}")

        if resposta.stop_reason != "tool_use":
            return

        # O Claude pediu ferramentas: o cliente MCP executa e devolve o resultado
        resultados = []
        for bloco in resposta.content:
            if bloco.type != "tool_use":
                continue
            print(f"  [ferramenta] {bloco.name}({bloco.input})")
            resultado = await mcp.call_tool(bloco.name, bloco.input)
            texto = "\n".join(c.text for c in resultado.content if c.type == "text")
            resultados.append(
                {
                    "type": "tool_result",
                    "tool_use_id": bloco.id,
                    "content": texto,
                    "is_error": resultado.is_error,
                }
            )
        mensagens.append({"role": "user", "content": resultados})


async def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Defina a variável de ambiente ANTHROPIC_API_KEY antes de rodar.")
        return

    claude = AsyncAnthropic()
    async with Client(SERVIDOR) as mcp:
        ferramentas = para_formato_claude((await mcp.list_tools()).tools)
        nomes = ", ".join(f["name"] for f in ferramentas)
        print(f"Ferramentas entregues ao Claude: {nomes}")
        print('Digite seu pedido ("sair" para encerrar).')

        mensagens: list[dict] = []
        while True:
            pedido = (await asyncio.to_thread(input, "\nVocê: ")).strip()
            if pedido.lower() in {"sair", "exit", "quit"}:
                break
            if not pedido:
                continue
            mensagens.append({"role": "user", "content": pedido})
            await responder(claude, mcp, ferramentas, mensagens)


if __name__ == "__main__":
    asyncio.run(main())
