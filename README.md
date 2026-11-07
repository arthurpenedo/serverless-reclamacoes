# serverless-reclamacoes

[![CI](https://github.com/arthurpenedo/serverless-reclamacoes/actions/workflows/ci.yml/badge.svg)](https://github.com/arthurpenedo/serverless-reclamacoes/actions/workflows/ci.yml)

Pipeline **serverless na AWS**: um CSV de reclamações de consumidor cai no S3, uma função Lambda resume por empresa
(quantidade, nota média, assunto mais comum) e grava o resultado em outro prefixo do S3 e numa tabela DynamoDB.

## Por que existe
Nuvem (AWS/Azure) aparece em cerca de 28% e 23% das vagas de dados e IA que o meu radar coleta, e eu só tinha
experiência de uso (Athena/QuickSight no Itaú), sem projeto no GitHub. Aqui a infraestrutura é código
(`template.yaml`, AWS SAM) e **tudo roda de graça, sem conta AWS**, porque os testes usam o `moto`, que imita S3 e DynamoDB.

## Como funciona
```
entrada/*.csv (S3) ──evento──▶ Lambda `handler` ──▶ resumo/<arquivo>.json (S3)
                                              └──▶ DynamoDB (empresa, arquivo)
```
- `nucleo.py`: regra pura, sem AWS (fácil de testar).
- `handler.py`: ponta AWS (lê S3, grava S3 e DynamoDB). Ignora chaves fora de `entrada/`, para o resumo não disparar a função de novo (laço infinito).
- `template.yaml`: bucket, tabela (cobrança por uso), função com permissões mínimas e o gatilho S3.
- **Versão Azure Functions** (`function_app.py`, modelo v2): blob em `entrada/` vira JSON em `resumo/` (outro container, sem laço). A regra fica em `azure.py` (bytes entram, JSON sai), então os testes rodam sem conta Azure.

## Como rodar
```bash
pip install -e ".[dev]"
pytest -q                                       # 16 testes, sem conta AWS nem Azure
serverless-reclamacoes dados/exemplo.csv        # mesma regra, direto no terminal
```
Para publicar na sua conta (nível gratuito): `sam build && sam deploy --guided`, depois
`aws s3 cp dados/exemplo.csv s3://<bucket>/entrada/exemplo.csv`.

## Números medidos
- 16 testes passando (5 da regra, 4 do Lambda com S3 e DynamoDB simulados, 3 da CLI, 4 da versão Azure): `pytest -q`, 07/11/2026.
- Agregar 100 mil linhas sintéticas (500 empresas): **~0,43 s** (mediana de 3 execuções, máquina de desenvolvimento, Python 3.13).

## Limites honestos
- **Não foi implantado numa conta AWS real**: o comportamento foi validado só com `moto`; o `template.yaml` é verificado com `cfn-lint` no CI, mas não com `sam deploy`.
- O Lambda lê o arquivo inteiro na memória (128 MB): só serve para arquivos que caibam na memória da função (limite não medido).
- A versão Azure também não foi implantada (sem `func start` nem conta): o teste só confere que o gatilho é registrado.
- Dados de exemplo fictícios.

## Licença
MIT.
