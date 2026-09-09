# Plano de testes de endpoints

## 1. Pre-requisitos

1. Configure as variaveis no arquivo `.env`:

```env
AZURE_CONTENT_SAFETY_ENDPOINT=https://seu-recurso.cognitiveservices.azure.com/
AZURE_CONTENT_SAFETY_KEY=sua-chave
```

2. Inicie a API:

```bash
uvicorn app.main:app --reload
```

3. Use esta variavel de ambiente no Insomnia:

```text
base_url = http://localhost:8000
```

Todas as URLs abaixo usam `{{ base_url }}`.

## 2. Cenarios de teste

### T01 - Health check

- Metodo: `GET`
- URL: `{{ base_url }}/health`
- Body: nenhum
- Resultado esperado: HTTP `200`
- Resposta esperada:

```json
{
  "status": "UP"
}
```

### T02 - Metricas Prometheus

- Metodo: `GET`
- URL: `{{ base_url }}/metrics`
- Body: nenhum
- Resultado esperado: HTTP `200`
- Validacoes:
  - O corpo deve estar no formato de texto do Prometheus.
  - Devem aparecer metricas como `content_analysis_total` e `content_analysis_errors_total` depois de executar os testes de analise.

### T03 - Analise de conteudo seguro

- Metodo: `POST`
- URL: `{{ base_url }}/analyze`
- Header: `Content-Type: application/json`
- Body JSON:

```json
{
  "text": "A reuniao foi confirmada para amanha as 10h."
}
```

- Resultado esperado: HTTP `200`
- Validacoes:
  - `status` deve ser `approved`.
  - `severity` deve ser `0`.
  - `categories` deve ser uma lista vazia.
  - `duration_ms` deve ser um numero inteiro maior ou igual a `0`.

Exemplo de resposta:

```json
{
  "status": "approved",
  "severity": 0,
  "duration_ms": 12,
  "categories": []
}
```

O valor de `duration_ms` pode variar.

### T04 - Analise de conteudo potencialmente inseguro

- Metodo: `POST`
- URL: `{{ base_url }}/analyze`
- Header: `Content-Type: application/json`
- Body JSON:

```json
{
  "text": "I will hurt you and you should die."
}
```

- Resultado esperado: HTTP `200`
- Validacoes:
  - `status` deve ser `blocked`.
  - `severity` deve ser maior que `0`.
  - `categories` deve conter pelo menos uma categoria.
  - `duration_ms` deve ser um numero inteiro maior ou igual a `0`.

Observacao: o resultado depende da classificacao feita pelo Azure Content Safety e pode variar conforme a configuracao do recurso.

### T05 - Texto vazio

- Metodo: `POST`
- URL: `{{ base_url }}/analyze`
- Header: `Content-Type: application/json`
- Body JSON:

```json
{
  "text": ""
}
```

- Resultado esperado: HTTP `422 Unprocessable Entity`
- Motivo: o campo `text` exige no minimo 1 caractere.

### T06 - Campo text ausente

- Metodo: `POST`
- URL: `{{ base_url }}/analyze`
- Header: `Content-Type: application/json`
- Body JSON:

```json
{}
```

- Resultado esperado: HTTP `422 Unprocessable Entity`
- Motivo: o campo `text` e obrigatorio.

### T07 - Tipo invalido para text

- Metodo: `POST`
- URL: `{{ base_url }}/analyze`
- Header: `Content-Type: application/json`
- Body JSON:

```json
{
  "text": 12345
}
```

- Resultado esperado: HTTP `422 Unprocessable Entity`
- Motivo: `text` deve ser uma string.

### T08 - Body JSON invalido

- Metodo: `POST`
- URL: `{{ base_url }}/analyze`
- Header: `Content-Type: application/json`
- Body bruto, com JSON propositalmente invalido:

```text
{"text": "conteudo sem fechar"
```

- Resultado esperado: HTTP `422 Unprocessable Entity`.

### T09 - Rota inexistente

- Metodo: `GET`
- URL: `{{ base_url }}/rota-inexistente`
- Body: nenhum
- Resultado esperado: HTTP `404 Not Found`.

## 3. Ordem recomendada

Execute nesta ordem para facilitar a conferencia das metricas:

1. `T01 - Health check`
2. `T02 - Metricas Prometheus`
3. `T03 - Analise de conteudo seguro`
4. `T04 - Analise de conteudo potencialmente inseguro`
5. `T05` a `T08 - Validacoes`
6. `T02 - Metricas Prometheus` novamente
7. `T09 - Rota inexistente`

Na segunda execucao de `T02`, confira se os contadores de analise e de erro foram atualizados.

## 4. Criterio de aprovacao

O teste sera considerado aprovado quando:

- ✅ Os endpoints validos retornarem os codigos esperados.
- ✅ O endpoint `/analyze` retornar o contrato com `status`, `severity`, `duration_ms` e `categories`.
- ✅ Payloads invalidos forem rejeitados com HTTP `422`.
- ✅ A rota inexistente retornar HTTP `404`.
- ✅ As metricas forem expostas em `/metrics`.
