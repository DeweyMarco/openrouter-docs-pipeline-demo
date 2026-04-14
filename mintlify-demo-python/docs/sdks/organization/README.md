# Organization

## Overview

Organization endpoints

### Available Operations

* [list_members](#list_members) - List organization members

## list_members

List all members of the organization associated with the authenticated management key. [Management key](/docs/guides/overview/auth/management-api-keys) required.

### Example Usage

<!-- UsageSnippet language="python" operationID="listOrganizationMembers" method="get" path="/organization/members" -->
```python
from mintlify_demo import MintlifyDemo
import os


with MintlifyDemo(
    http_referer="<value>",
    app_title="<value>",
    app_categories="<value>",
    api_key=os.getenv("MINTLIFYDEMO_API_KEY", ""),
) as md_client:

    res = md_client.organization.list_members(offset=0, limit=50)

    while res is not None:
        # Handle items

        res = res.next()

```

### Parameters

| Parameter                                                                                                                                         | Type                                                                                                                                              | Required                                                                                                                                          | Description                                                                                                                                       | Example                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `http_referer`                                                                                                                                    | *Optional[str]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | The app identifier should be your app's URL and is used as the primary identifier for rankings.<br/>This is used to track API usage per application.<br/> |                                                                                                                                                   |
| `app_title`                                                                                                                                       | *Optional[str]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | The app display name allows you to customize how your app appears in OpenRouter's dashboard.<br/>                                                 |                                                                                                                                                   |
| `app_categories`                                                                                                                                  | *Optional[str]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | Comma-separated list of app categories (e.g. "cli-agent,cloud-agent"). Used for marketplace rankings.<br/>                                        |                                                                                                                                                   |
| `offset`                                                                                                                                          | *Optional[int]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | Number of records to skip for pagination                                                                                                          | 0                                                                                                                                                 |
| `limit`                                                                                                                                           | *Optional[int]*                                                                                                                                   | :heavy_minus_sign:                                                                                                                                | Maximum number of records to return (max 100)                                                                                                     | 50                                                                                                                                                |
| `retries`                                                                                                                                         | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                                                  | :heavy_minus_sign:                                                                                                                                | Configuration to override the default retry behavior of the client.                                                                               |                                                                                                                                                   |

### Response

**[models.ListOrganizationMembersResponse](../../models/listorganizationmembersresponse.md)**

### Errors

| Error Type                         | Status Code                        | Content Type                       |
| ---------------------------------- | ---------------------------------- | ---------------------------------- |
| errors.UnauthorizedResponseError   | 401                                | application/json                   |
| errors.NotFoundResponseError       | 404                                | application/json                   |
| errors.InternalServerResponseError | 500                                | application/json                   |
| errors.MintlifyDemoDefaultError    | 4XX, 5XX                           | \*/\*                              |