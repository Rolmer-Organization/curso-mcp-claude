"""Etapa 2: confere se o SDK de MCP foi instalado no ambiente virtual."""

from importlib.metadata import PackageNotFoundError, version


def main() -> None:
    print("Olá, MCP!")
    try:
        print(f"SDK de MCP instalado: versão {version('mcp')}")
    except PackageNotFoundError:
        print("SDK de MCP não encontrado. Rode: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
