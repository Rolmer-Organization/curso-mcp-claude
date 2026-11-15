"""Etapa 3: nosso primeiro cliente MCP.

Ele se conecta a um servidor MCP que já existe (mcp-server-time), pergunta
quais ferramentas o servidor oferece e chama uma delas.
"""

import asyncio
import sys

from mcp import Client, StdioServerParameters

# Como iniciar o servidor: o cliente abre o servidor como um processo filho
# e conversa com ele pela entrada e saída padrão (transporte "stdio").
SERVIDOR = StdioServerParameters(
    command=sys.executable,  # o mesmo Python do ambiente virtual
    args=["-m", "mcp_server_time", "--local-timezone", "America/Sao_Paulo"],
)


async def main() -> None:
    async with Client(SERVIDOR) as cliente:
        # 1. Quem é o servidor?
        print(f"Conectado a: {cliente.server_info.name}")
        print(f"Versão do protocolo: {cliente.protocol_version}\n")

        # 2. Descoberta: o que ele sabe fazer?
        resposta = await cliente.list_tools()
        print("Ferramentas disponíveis:")
        for ferramenta in resposta.tools:
            print(f"  - {ferramenta.name}: {ferramenta.description}")

        # 3. Chamada: usa uma ferramenta pelo nome
        resultado = await cliente.call_tool(
            "get_current_time", {"timezone": "America/Sao_Paulo"}
        )
        print("\nResultado de get_current_time:")
        print(resultado.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
