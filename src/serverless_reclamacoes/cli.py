"""CLI local: roda a mesma regra do Lambda sobre um CSV, sem precisar de conta AWS."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .nucleo import agregar


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="serverless-reclamacoes", description=__doc__)
    p.add_argument("csv", type=Path, help="arquivo CSV (empresa,assunto,estado,nota)")
    args = p.parse_args(argv)
    try:
        resumo = agregar(args.csv.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
