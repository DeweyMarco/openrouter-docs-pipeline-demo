# Rerank

## Overview

Reranking endpoints

### Available Operations

* [rerank](#rerank) - Submit a rerank request

## rerank

Submits a rerank request to the rerank router

### Example Usage

<!-- UsageSnippet language="python" operationID="createRerank" method="post" path="/rerank" -->
```python
from mintlify_demo import MintlifyDemo
import os


with MintlifyDemo(
    http_referer="<value>",
    app_title="<value>",
    app_categories="<value>",
    api_key=os.getenv("MINTLIFYDEMO_API_KEY", ""),
) as md_client:

    res = md_client.rerank.rerank(model="cohere/rerank-v3.5", query="What is the capital of France?", documents=[
        "Paris is the capital of France.",
        "Berlin is the capital of Germany.",
        "Madrid is the capital of Spain.",
    ], top_n=3, provider={
        "allow_fallbacks": True,
    })

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                                                                         | Type                                                                                                                                              | Required                                                                                                                                          | Description                                                                                                                                       | Example                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                                                                                                                                           | *str*                                                                                                                                             | :heavy_check_mark:                                                                                                                                | The rerank model to use                                                                                                                           | cohere/rerank-v3.5                                                                                                                                |
| `query`                                                                                                                                           | *str*                                                                                                                                             | :heavy_check_mark:                                                                                                                                | The search query to rerank documents against                                                                                                      | What is the capital of France?                                                                                                                    |
| `documents`                                                                                                                                       | List[*str*]                                                                                                                                       | :heavy_check_mark:                                                                                                                                | The list of documents to rerank                                                                                                                   | [<br/>"Paris is the capital of France.",<br/>"Berlin is the capital of Germany."<br/>]                                                            |
| `http_referer`                                                                                                                                    | *Optional[str]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | The app identifier should be your app's URL and is used as the primary identifier for rankings.<br/>This is used to track API usage per application.<br/> |                                                                                                                                                   |
| `app_title`                                                                                                                                       | *Optional[str]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | The app display name allows you to customize how your app appears in OpenRouter's dashboard.<br/>                                                 |                                                                                                                                                   |
| `app_categories`                                                                                                                                  | *Optional[str]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | Comma-separated list of app categories (e.g. "cli-agent,cloud-agent"). Used for marketplace rankings.<br/>                                        |                                                                                                                                                   |
| `top_n`                                                                                                                                           | *Optional[int]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | Number of most relevant documents to return                                                                                                       | 3                                                                                                                                                 |
| `provider`                                                                                                                                        | [OptionalNullable[models.ProviderPreferences]](../../models/providerpreferences.md)                                                               | :heavy_minus_sign:                                                                                                                                | N/A                                                                                                                                               | {<br/>"allow_fallbacks": true<br/>}                                                                                                               |
| `retries`                                                                                                                                         | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                                                  | :heavy_minus_sign:                                                                                                                                | Configuration to override the default retry behavior of the client.                                                                               |                                                                                                                                                   |

### Response

**[models.CreateRerankResponse](../../models/creatererankresponse.md)**

### Errors

| Error Type                             | Status Code                            | Content Type                           |
| -------------------------------------- | -------------------------------------- | -------------------------------------- |
| errors.BadRequestResponseError         | 400                                    | application/json                       |
| errors.UnauthorizedResponseError       | 401                                    | application/json                       |
| errors.PaymentRequiredResponseError    | 402                                    | application/json                       |
| errors.NotFoundResponseError           | 404                                    | application/json                       |
| errors.TooManyRequestsResponseError    | 429                                    | application/json                       |
| errors.InternalServerResponseError     | 500                                    | application/json                       |
| errors.BadGatewayResponseError         | 502                                    | application/json                       |
| errors.ServiceUnavailableResponseError | 503                                    | application/json                       |
| errors.EdgeNetworkTimeoutResponseError | 524                                    | application/json                       |
| errors.ProviderOverloadedResponseError | 529                                    | application/json                       |
| errors.MintlifyDemoDefaultError        | 4XX, 5XX                               | \*/\*                                  |