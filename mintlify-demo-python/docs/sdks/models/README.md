# Models

## Overview

Model information endpoints

### Available Operations

* [count](#count) - Get total count of available models
* [list](#list) - List all models and their properties
* [list_for_user](#list_for_user) - List models filtered by user provider preferences, privacy settings, and guardrails

## count

Get total count of available models

### Example Usage

<!-- UsageSnippet language="python" operationID="listModelsCount" method="get" path="/models/count" -->
```python
from mintlify_demo import MintlifyDemo
import os


with MintlifyDemo(
    http_referer="<value>",
    app_title="<value>",
    app_categories="<value>",
    api_key=os.getenv("MINTLIFYDEMO_API_KEY", ""),
) as md_client:

    res = md_client.models.count(output_modalities="text")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                                                                                           | Type                                                                                                                                                                | Required                                                                                                                                                            | Description                                                                                                                                                         | Example                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `http_referer`                                                                                                                                                      | *Optional[str]*                                                                                                                                                     | :heavy_minus_sign:                                                                                                                                                  | The app identifier should be your app's URL and is used as the primary identifier for rankings.<br/>This is used to track API usage per application.<br/>           |                                                                                                                                                                     |
| `app_title`                                                                                                                                                         | *Optional[str]*                                                                                                                                                     | :heavy_minus_sign:                                                                                                                                                  | The app display name allows you to customize how your app appears in OpenRouter's dashboard.<br/>                                                                   |                                                                                                                                                                     |
| `app_categories`                                                                                                                                                    | *Optional[str]*                                                                                                                                                     | :heavy_minus_sign:                                                                                                                                                  | Comma-separated list of app categories (e.g. "cli-agent,cloud-agent"). Used for marketplace rankings.<br/>                                                          |                                                                                                                                                                     |
| `output_modalities`                                                                                                                                                 | *Optional[str]*                                                                                                                                                     | :heavy_minus_sign:                                                                                                                                                  | Filter models by output modality. Accepts a comma-separated list of modalities (text, image, audio, embeddings) or "all" to include all models. Defaults to "text". | text                                                                                                                                                                |
| `retries`                                                                                                                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                                                                    | :heavy_minus_sign:                                                                                                                                                  | Configuration to override the default retry behavior of the client.                                                                                                 |                                                                                                                                                                     |

### Response

**[models.ModelsCountResponse](../../models/modelscountresponse.md)**

### Errors

| Error Type                         | Status Code                        | Content Type                       |
| ---------------------------------- | ---------------------------------- | ---------------------------------- |
| errors.BadRequestResponseError     | 400                                | application/json                   |
| errors.InternalServerResponseError | 500                                | application/json                   |
| errors.MintlifyDemoDefaultError    | 4XX, 5XX                           | \*/\*                              |

## list

List all models and their properties

### Example Usage

<!-- UsageSnippet language="python" operationID="getModels" method="get" path="/models" -->
```python
from mintlify_demo import MintlifyDemo
import os


with MintlifyDemo(
    http_referer="<value>",
    app_title="<value>",
    app_categories="<value>",
    api_key=os.getenv("MINTLIFYDEMO_API_KEY", ""),
) as md_client:

    res = md_client.models.list(category="programming", supported_parameters="temperature", output_modalities="text")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                                                                                           | Type                                                                                                                                                                | Required                                                                                                                                                            | Description                                                                                                                                                         | Example                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `http_referer`                                                                                                                                                      | *Optional[str]*                                                                                                                                                     | :heavy_minus_sign:                                                                                                                                                  | The app identifier should be your app's URL and is used as the primary identifier for rankings.<br/>This is used to track API usage per application.<br/>           |                                                                                                                                                                     |
| `app_title`                                                                                                                                                         | *Optional[str]*                                                                                                                                                     | :heavy_minus_sign:                                                                                                                                                  | The app display name allows you to customize how your app appears in OpenRouter's dashboard.<br/>                                                                   |                                                                                                                                                                     |
| `app_categories`                                                                                                                                                    | *Optional[str]*                                                                                                                                                     | :heavy_minus_sign:                                                                                                                                                  | Comma-separated list of app categories (e.g. "cli-agent,cloud-agent"). Used for marketplace rankings.<br/>                                                          |                                                                                                                                                                     |
| `category`                                                                                                                                                          | [Optional[models.Category]](../../models/category.md)                                                                                                               | :heavy_minus_sign:                                                                                                                                                  | Filter models by use case category                                                                                                                                  | programming                                                                                                                                                         |
| `supported_parameters`                                                                                                                                              | *Optional[str]*                                                                                                                                                     | :heavy_minus_sign:                                                                                                                                                  | Filter models by supported parameter (comma-separated)                                                                                                              | temperature                                                                                                                                                         |
| `output_modalities`                                                                                                                                                 | *Optional[str]*                                                                                                                                                     | :heavy_minus_sign:                                                                                                                                                  | Filter models by output modality. Accepts a comma-separated list of modalities (text, image, audio, embeddings) or "all" to include all models. Defaults to "text". | text                                                                                                                                                                |
| `retries`                                                                                                                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                                                                    | :heavy_minus_sign:                                                                                                                                                  | Configuration to override the default retry behavior of the client.                                                                                                 |                                                                                                                                                                     |

### Response

**[models.ModelsListResponse](../../models/modelslistresponse.md)**

### Errors

| Error Type                         | Status Code                        | Content Type                       |
| ---------------------------------- | ---------------------------------- | ---------------------------------- |
| errors.BadRequestResponseError     | 400                                | application/json                   |
| errors.InternalServerResponseError | 500                                | application/json                   |
| errors.MintlifyDemoDefaultError    | 4XX, 5XX                           | \*/\*                              |

## list_for_user

List models filtered by user provider preferences, [privacy settings](https://openrouter.ai/docs/guides/privacy/logging), and [guardrails](https://openrouter.ai/docs/guides/features/guardrails). If requesting through `eu.openrouter.ai/api/v1/...` the results will be filtered to models that satisfy [EU in-region routing](https://openrouter.ai/docs/guides/privacy/logging#enterprise-eu-in-region-routing).

### Example Usage

<!-- UsageSnippet language="python" operationID="listModelsUser" method="get" path="/models/user" -->
```python
from mintlify_demo import MintlifyDemo, models
import os


with MintlifyDemo(
    http_referer="<value>",
    app_title="<value>",
    app_categories="<value>",
) as md_client:

    res = md_client.models.list_for_user(security=models.ListModelsUserSecurity(
        bearer=os.getenv("MINTLIFYDEMO_BEARER", ""),
    ))

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                                                                         | Type                                                                                                                                              | Required                                                                                                                                          | Description                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `security`                                                                                                                                        | [models.ListModelsUserSecurity](../../models/listmodelsusersecurity.md)                                                                           | :heavy_check_mark:                                                                                                                                | N/A                                                                                                                                               |
| `http_referer`                                                                                                                                    | *Optional[str]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | The app identifier should be your app's URL and is used as the primary identifier for rankings.<br/>This is used to track API usage per application.<br/> |
| `app_title`                                                                                                                                       | *Optional[str]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | The app display name allows you to customize how your app appears in OpenRouter's dashboard.<br/>                                                 |
| `app_categories`                                                                                                                                  | *Optional[str]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | Comma-separated list of app categories (e.g. "cli-agent,cloud-agent"). Used for marketplace rankings.<br/>                                        |
| `retries`                                                                                                                                         | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                                                  | :heavy_minus_sign:                                                                                                                                | Configuration to override the default retry behavior of the client.                                                                               |

### Response

**[models.ModelsListResponse](../../models/modelslistresponse.md)**

### Errors

| Error Type                         | Status Code                        | Content Type                       |
| ---------------------------------- | ---------------------------------- | ---------------------------------- |
| errors.UnauthorizedResponseError   | 401                                | application/json                   |
| errors.NotFoundResponseError       | 404                                | application/json                   |
| errors.InternalServerResponseError | 500                                | application/json                   |
| errors.MintlifyDemoDefaultError    | 4XX, 5XX                           | \*/\*                              |