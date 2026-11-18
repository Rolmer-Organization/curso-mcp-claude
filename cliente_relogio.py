"""Etapa 3: nosso primeiro cliente MCP.

Ele se conecta a um servidor MCP que já existe (mcp-server-time), pergunta
quais ferramentas o servidor oferece e chama uma delas.
"""

import asyncio
import sys

from mcp import Client, StdioServerParameters


def criar_cliente_relogio() -> Client:
    """Cria (mas NÃO conecta) um cliente MCP para o servidor de relógio.

    >>> Este é o ÚNICO lugar do arquivo que sabe COMO o servidor é ligado. <<<
    O resto do arquivo só usa o cliente que esta função devolve.

    O que esta função faz e o que NÃO faz:
      - Faz: monta um objeto `Client` com a "receita" de como iniciar o
        servidor.
      - NÃO faz: iniciar o servidor nem conectar. Chamar esta função não
        tem nenhum efeito além de devolver o objeto.

    Quando o servidor realmente nasce:
      A conexão só acontece quando quem chamou entra no `async with`
      (veja `main`). Nesse momento, e só nesse momento:
        1. O cliente inicia o servidor como um PROCESSO FILHO, rodando o
           comando abaixo, como se digitássemos no terminal:
               python -m mcp_server_time --local-timezone America/Sao_Paulo
        2. Cliente e servidor trocam mensagens MCP pela entrada e saída
           padrão (stdin/stdout) desse processo. É o transporte "stdio".
        3. Ao sair do `async with`, a conexão fecha e o processo morre.

    Consequências do transporte stdio (importante entender):
      - O servidor é EXCLUSIVO deste cliente. Não há porta, endereço ou
        URL, então nenhuma outra aplicação consegue se conectar a ele.
      - Ele só existe enquanto o `async with` está aberto. Outra aplicação
        com cliente MCP que queira o mesmo servidor inicia a sua própria
        instância.
      - Para um servidor compartilhado entre várias aplicações, seria
        preciso outro transporte (HTTP): o servidor rodaria sozinho,
        escutando numa porta, e os clientes se conectariam por uma URL.

    Para usar outro servidor MCP local, basta trocar `command` e `args`.
    Nada mais no arquivo precisa mudar.
    """
    parametros = StdioServerParameters(
        # Programa a executar: o mesmo Python do ambiente virtual atual,
        # onde o pacote mcp-server-time está instalado.
        command=sys.executable,
        # Argumentos: "-m mcp_server_time" executa o módulo do servidor;
        # "--local-timezone" define o fuso horário padrão dele.
        args=["-m", "mcp_server_time", "--local-timezone", "America/Sao_Paulo"],
    )
    return Client(parametros)


async def main() -> None:
    # `criar_cliente_relogio()` só monta o cliente; nada está rodando ainda.
    # Ao ENTRAR no `async with`, o servidor é iniciado como processo filho e
    # o handshake do protocolo é feito. Ao SAIR, a conexão fecha e o
    # servidor é encerrado. Dentro do bloco, `cliente` está pronto para uso.
    async with criar_cliente_relogio() as cliente:
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
