"""Azure Functions (modelo v2): blob em `entrada/` vira resumo JSON em `resumo/`."""

import azure.functions as func

from serverless_reclamacoes.azure import CONTAINER_ENTRADA, CONTAINER_SAIDA, resumir_blob

app = func.FunctionApp()


@app.blob_trigger(arg_name="blob", path=f"{CONTAINER_ENTRADA}/{{name}}", connection="AzureWebJobsStorage")
@app.blob_output(arg_name="saida", path=f"{CONTAINER_SAIDA}/{{name}}.json", connection="AzureWebJobsStorage")
def resumir(blob: func.InputStream, saida: func.Out[str]) -> None:
    _, texto = resumir_blob(blob.name, blob.read())
    saida.set(texto)
