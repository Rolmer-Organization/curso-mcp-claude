# curso-mcp-claude

Projeto das videoaulas "MCP com Claude". Cada etapa do curso é uma branch:

| Branch | O que entra |
| --- | --- |
| `01-hello-world` | Esqueleto do projeto |
| `02-dependencias` | Ambiente virtual e SDK de MCP |
| `03-cliente-mcp` | Cliente que usa um servidor MCP pronto |
| `04-servidor-mcp` | Nosso próprio servidor MCP |
| `05-cliente-do-servidor` | Cliente que consome o nosso servidor |
| `06-claude` | Bônus: o Claude escolhe as ferramentas |

Para ir a uma etapa: `git checkout 03-cliente-mcp`

## Etapa 1: hello world

Requisito: Python 3.10 ou mais novo.

```
python main.py
```

Saída esperada: `Olá, MCP!`

## Etapa 2: dependências

Crie o ambiente virtual e instale as dependências.

Windows (PowerShell):

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Linux e macOS:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Saída esperada: `SDK de MCP instalado: versão 2.x.x`

Atenção: este curso usa a série 2.x do SDK. Tutoriais antigos usam
`from mcp.server.fastmcp import FastMCP`, que não existe mais na 2.x.

## Etapa 3: cliente MCP

`cliente_relogio.py` se conecta a um servidor MCP pronto (`mcp-server-time`),
lista as ferramentas e chama `get_current_time`.

```
python cliente_relogio.py
```

O cliente inicia o servidor sozinho, como processo filho. Não é preciso abrir
outro terminal.

## Etapa 4: servidor MCP

`servidor.py` é um servidor de lista de tarefas, com três ferramentas, um
recurso e um prompt. Os dados ficam em `tarefas.json`, ao lado do arquivo.

Um servidor stdio não se usa sozinho no terminal: ele fica esperando um
cliente. Para testar com o MCP Inspector (precisa de `uv` e Node.js):

```
mcp dev servidor.py
```

Para rodar como servidor de rede, em `http://127.0.0.1:8000/mcp`:

```
python servidor.py --http
```

## Etapa 5: cliente do nosso servidor

`cliente.py` consome o `servidor.py`: descobre o que ele oferece, chama as
ferramentas, lê o recurso e busca o prompt.

```
python cliente.py explorar
python cliente.py adicionar "Gravar a aula 5"
python cliente.py listar
python cliente.py concluir 1
python cliente.py resumo
python cliente.py planejar estudos
```

O mesmo cliente fala com o servidor de rede. Em um terminal, rode
`python servidor.py --http`; em outro, `python cliente.py --http listar`.
