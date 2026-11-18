"""Etapa 3: nosso primeiro cliente MCP.

Ele se conecta a um servidor MCP que já existe (mcp-server-time), pergunta
quais ferramentas o servidor oferece e chama uma delas.

O arquivo tem duas partes bem separadas:
  1. `definir_servidor`  -> COMO o servidor é iniciado (detalhe de infraestrutura).
  2. `usar_servidor`     -> o que o CLIENTE MCP faz com ele (o foco do curso).
"""

import asyncio
import sys

from mcp import Client, StdioServerParameters


# ---------------------------------------------------------------------------
# Parte 1: o servidor
# ---------------------------------------------------------------------------
def definir_servidor() -> StdioServerParameters:
    """Descreve como iniciar o servidor MCP de relógio (mcp-server-time).

    Esta função só devolve a "receita" do servidor. Ela NÃO inicia nada.

    Transporte "stdio": quando o cliente se conectar, ele vai rodar o comando
    abaixo como um PROCESSO FILHO, como se digitássemos no terminal:
        python -m mcp_server_time --local-timezone America/Sao_Paulo
    e conversar com ele pela entrada e saída padrão (stdin/stdout).

    Consequências:
      - O servidor é exclusivo do cliente que o iniciou: não há porta nem URL,
        e nenhuma outra aplicação consegue se conectar a ele.
      - Ele só existe enquanto a conexão estiver aberta; quando o cliente
        desconecta, o processo é encerrado.

    Para usar outro servidor MCP local, basta trocar `command` e `args`.
    """
    return StdioServerParameters(
        # Programa a executar: o mesmo Python do ambiente virtual atual,
        # onde o pacote mcp-server-time está instalado.
        command=sys.executable,
        # "-m mcp_server_time" executa o módulo do servidor;
        # "--local-timezone" define o fuso horário padrão dele.
        args=["-m", "mcp_server_time", "--local-timezone", "America/Sao_Paulo"],
    )


# ---------------------------------------------------------------------------
# Parte 2: o cliente MCP
# ---------------------------------------------------------------------------
async def usar_servidor(servidor: StdioServerParameters) -> None:
    """Conecta ao servidor, descobre as ferramentas e chama uma delas."""
    # Entrar no `async with` abre a conexão: o servidor é iniciado e o
    # handshake do protocolo é feito. Ao sair do bloco, tudo é fechado.
    async with Client(servidor) as cliente:
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
    asyncio.run(usar_servidor(definir_servidor()))
