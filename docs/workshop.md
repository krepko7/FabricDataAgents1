# Workshop with file upload

## What you'll build

**Seven fictional CSVs -> Lakehouse Files -> seven Delta tables -> Power BI semantic model -> Fabric Data Agent -> MCP client.**

There is no SQL database or mirroring in this workshop. Uploading and loading files is a **manual snapshot**, not continuous synchronization: uploading a changed CSV later doesn't automatically update its table.

## Agenda (3 hours)

| Time | Topic | Outcome |
|---|---|---|
| 00:00-00:15 | Introduction to Fabric | Understand workspace, OneLake, Lakehouse, semantic model, and Data Agent |
| 00:15-00:30 | Create a workspace and Lakehouse | Create a capacity-backed workspace and `AutomobileBilling` Lakehouse |
| 00:30-01:05 | Upload CSVs and create tables | Seven CSVs uploaded and loaded as Delta tables; inspect types |
| 01:05-01:35 | Create a semantic model | Create and validate six relationships and simple report checks |
| 01:35-02:00 | Create and configure a Data Agent | Add the model, apply AI instructions, and publish |
| 02:00-02:35 | Explore 12 business questions | Compare responses with the facilitator answer key |
| 02:35-02:55 | Connect the Data Agent as an MCP server | Add the published agent to an MCP client and ask a question |
| 02:55-03:00 | Wrap-up | Discuss results, permissions, and next steps |

If capacity provisioning or tenant approvals aren't already complete, arrange them before the session.

## Prerequisites

- Download the repository as a ZIP from GitHub using **Code > Download ZIP**, extract it, and locate the seven `.csv` files in `data`. You don't need a Git client.
- Sign in to [Microsoft Fabric](https://app.fabric.microsoft.com/) with a work or school account. Your organization must permit workspace creation, Lakehouse authoring, semantic model authoring, and Data Agent use.
- Have access to an active **paid F2 or higher Fabric capacity**, or **P1 or higher Power BI Premium capacity with Fabric enabled**, for the Data Agent and MCP parts. Confirm applicable AI/cross-geo processing and storing tenant settings and regional availability with an administrator. A trial capacity can support other Fabric exercises but doesn't by itself satisfy this documented Data Agent requirement.
- Have permission to create/assign a workspace to that capacity; if not, use an existing approved capacity-backed workspace. For the workshop author, use an appropriate Admin/Member/Contributor role, model edit permissions, and necessary Power BI licensing. Consumers need the appropriate agent and data/model permissions.
- For the MCP exercise, use an approved MCP client that supports **streamable HTTP** and can authenticate to Fabric. VS Code is the example; organizational app, network, and authentication policies apply.

Capacity and workspace resources may incur charges. Use only this fictional data and follow organizational sharing policies.

## 1. Introduction to Fabric

| Component | Role |
|---|---|
| Workspace | Collaboration and access boundary containing the workshop items |
| OneLake | Shared storage for Fabric data |
| Lakehouse | Stores uploaded files and Delta tables in OneLake |
| Semantic model | Relationships, business meaning, and a consistent Power BI analysis layer |
| Data Agent | Translates natural-language questions into queries against authorized data |
| MCP | A standard way for a compatible client to discover and call the published Data Agent as a tool |

Data Agents are conversational query tools, not autonomous proof of why an anomaly occurred. Review their results against the data.

## 2. Create a workspace

1. In Fabric, select **Workspaces** in the left navigation, then **New workspace**.
2. Name it `Automobile Billing Workshop` (add a unique suffix if needed).
3. Expand **Advanced**. Choose an available eligible Fabric capacity or qualifying Premium capacity; select **Apply**.
4. If capacity selection isn't offered during creation, open workspace **Settings > Workspace type**, select **Edit**, and choose the approved capacity. Ask your admin if no eligible capacity is available.
5. Confirm the workspace is on that capacity and that you can create items. Don't change tenant settings or share the workspace more broadly without approval.

**Checkpoint:** the workspace opens and its capacity is active.

## 3. Create a Lakehouse

1. Open the workspace and select **New item**.
2. Search for **Lakehouse**, select it, enter `AutomobileBilling`, and select **Create**.
3. Wait for the Lakehouse explorer. Locate **Files** and **Tables**.

**Checkpoint:** the new Lakehouse opens with both sections visible.

## 4. Upload the seven CSV files

1. In the Lakehouse explorer, select **...** next to **Files** and create a folder named `billing`.
2. Select **...** next to `billing` > **Upload** > **Upload files**.
3. Select the seven `.csv` files from the extracted `data` folder. If multi-select isn't available, upload each file individually.
4. Open `Files > billing` and confirm all seven appear: `Dealerships.csv`, `Products.csv`, `Subscriptions.csv`, `UsageRecords.csv`, `Invoices.csv`, `InvoiceLines.csv`, and `Payments.csv`.

**Checkpoint:** preview `Products.csv` and confirm the first row contains column names, not an actual product. The files are comma-delimited with UTF-8 encoding.

## 5. Turn the files into Lakehouse tables

For **each** CSV:

1. Select **...** next to the file > **Load to tables** > **New table**.
2. If a **Schema** field appears, keep the same default schema for all seven tables.
3. Enter the lowercase name from the table below. Lakehouse table names in this UI must use lowercase letters, digits, or underscores.
4. Select **Column header** and set **Separator** to a comma (`,`). Select **Load**.
5. Wait for the load to complete before proceeding; repeat for the other six files.

| File | New table name | Expected rows |
|---|---|---:|
| `Dealerships.csv` | `dealerships` | 24 |
| `Products.csv` | `products` | 7 |
| `Subscriptions.csv` | `subscriptions` | 127 |
| `UsageRecords.csv` | `usagerecords` | 540 |
| `Invoices.csv` | `invoices` | 240 |
| `InvoiceLines.csv` | `invoicelines` | 1,797 |
| `Payments.csv` | `payments` | 242 |

Don't use **Append** on a table already loaded for this workshop: it would duplicate rows. **Overwrite** replaces a table and can affect downstream models; use it only in your dedicated workshop environment after reviewing the impact.

Expand **Tables**, select each table, and inspect its preview and column types. The preview can be limited to the first 1,000 rows, so it isn't a complete count for `invoicelines`. Use a report visual's count of `InvoiceLineID` to verify 1,797 after model creation. See [the data dictionary](dataset.md#types-to-check-after-loading) for intended types.

**Checkpoint:** all seven tables are visible; keys are compatible, amounts numeric, dates parsed, and blank contract end dates are null. The Lakehouse loader doesn't let you choose a custom schema in this dialog; if inference is unsuitable, follow [troubleshooting](#troubleshooting) instead of proceeding with wrong types.

## 6. Create a semantic model

1. From the Lakehouse ribbon select **New Power BI semantic model** (sometimes labeled **New semantic model**).
2. Name it `Automobile Billing`, choose the workshop workspace, select all seven tables, and confirm.
3. Open its model editor. In model view, remove conflicting auto-detected relationships and add the six active single-direction relationships in the [semantic model guide](semantic-model.md#relationships).
4. Verify data types and descriptions; use the [no-code report checks](semantic-model.md#check-the-data-without-code). October's signed billed amount should be **$66,728.00**.
5. Save the model. In **Prep data for AI**, apply the model-specific instructions in [AI instructions](agent-instructions.md) and review the AI data schema.

**Checkpoint:** the model has seven tables, six relationships, no ambiguity warning, and a correct October billing check. The model intentionally doesn't bridge dealership filters to invoice headers/payments; read the documented limitation before presenting collections results.

## 7. Create and publish the Data Agent

1. In the workspace, select **New item** and search for **Fabric data agent**.
2. Name it `Automobile Billing Analyst`.
3. In the OneLake catalog, select the `Automobile Billing` **Power BI semantic model**, then **Add**. Use only that source for this exercise.
4. In the agent Explorer, select the seven tables, consistent with the semantic model's Prep for AI schema.
5. Add the **agent-level** text from [AI instructions](agent-instructions.md). Ensure model-specific business rules are also in **Prep data for AI**; agent instructions alone don't control semantic-model DAX generation.
6. Ask: “What is October 2026 net billed revenue in USD?” Expect **$66,728.00**. Review the evidence/query if the UI exposes it.
7. Give the agent a clear **description** for MCP clients: “Answers questions about fictional dealership subscriptions, billing, usage, and payments for the Automobile workshop; data is in USD for January-October 2026.”
8. **Publish** the agent using the UI. Publishing is required for MCP. Share only with approved participants and verify their permissions to the agent and semantic model.

Semantic-model sources don't support agent-level data source descriptions or SQL example queries. The published **agent description** is separate and becomes the advertised MCP tool description. The model's Prep for AI configuration supplies business context for its DAX generator.

## 8. Try the 12 questions

Use the [question list and answer key](demo-scenarios.md). Start a fresh conversation or restate the reporting dates for each question. Divide the 12 questions among teams.

For each answer, check the values, time period, sign, units, and customer/product set. Inspect query/evidence when available. Complex comparisons and dealer-level collections are **stretch questions** for this deliberately simple model; if a result is wrong or unsupported, record it as a failure and discuss how a better model or validated measures would help. Don't insert the answer key into agent instructions.

## 9. Call the agent as an MCP server

Follow the [MCP guide](mcp.md). In brief:

1. Open the **published** Data Agent's **Settings > Model Context Protocol** and copy its MCP server URL. The screen also shows the server/tool names and tool description.
2. In VS Code, add an HTTP MCP server using that copied URL and sign in using an authorized Fabric account when prompted.
3. Enable/select the discovered Data Agent tool, ask the October billing question, and inspect the tool call and answer.
4. Compare the returned **$66,728.00** with the Fabric chat and report visual. A generic HTTP request or the unrelated Fabric Core MCP endpoint isn't a substitute for the Data Agent MCP protocol.

**Checkpoint:** the client discovers the agent's tool and invokes it; if authentication/client compatibility fails, use the troubleshooting guidance rather than claiming MCP worked.

### Optional: call the MCP server from Python

This is an alternative to the VS Code client, not a requirement for loading the CSVs or completing the no-code lab. Use **Python 3.10+** and the **Azure CLI** on your local computer. The signed-in account must have access to the published agent and its semantic model.

Install the client libraries and sign in to the tenant containing your Fabric workspace:

```powershell
python -m pip install "mcp>=1.10,<2" azure-identity
az login --tenant YOUR_TENANT_ID
```

Save the following as `call_agent.py`. Replace `MCP_URL` with the **actual URL copied from Settings > Model Context Protocol**, not the agent's browser URL. This example uses the MCP Python SDK's version 1 API, obtains a Fabric token from your Azure CLI sign-in, initializes the MCP connection, discovers the agent's tool and question argument, and calls it.

```python
import asyncio

from azure.identity.aio import AzureCliCredential
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = "PASTE_YOUR_PUBLISHED_DATA_AGENT_MCP_URL_HERE"
QUESTION = "What is October 2026 net billed revenue in USD?"


async def main():
    if not MCP_URL.startswith("https://api.fabric.microsoft.com/v1/mcp/"):
        raise ValueError("Copy the published Data Agent MCP URL into MCP_URL.")

    async with AzureCliCredential() as credential:
        token = await credential.get_token(
            "https://api.fabric.microsoft.com/.default"
        )

    headers = {"Authorization": f"Bearer {token.token}"}
    async with streamablehttp_client(MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            if len(tools) != 1:
                raise RuntimeError("Expected one tool from the Data Agent server.")

            tool = tools[0]
            properties = tool.inputSchema.get("properties", {})
            if len(properties) != 1:
                raise RuntimeError(
                    f"Inspect the tool input schema before calling: {tool.inputSchema}"
                )
            question_arg, definition = next(iter(properties.items()))
            if definition.get("type") != "string":
                raise RuntimeError("Expected a single string question argument.")

            print(f"Calling tool: {tool.name}")
            result = await session.call_tool(tool.name, {question_arg: QUESTION})
            if result.isError:
                raise RuntimeError(f"MCP tool failed: {result.model_dump_json()}")
            for block in result.content:
                print(block.text if block.type == "text" else block.model_dump_json())


if __name__ == "__main__":
    asyncio.run(main())
```

Run it from the folder where you saved the file:

```powershell
python .\call_agent.py
```

Compare the answer with **$66,728.00** and the Fabric chat/report result. The sample acquires a token for this short-lived session; a long-running application needs token renewal. Never print or save bearer tokens. Authentication, permission, transport, and tool errors are surfaced rather than treated as valid answers. This example hasn't been run against a live workshop agent.

## Troubleshooting

| Issue | What to check |
|---|---|
| Can't create workspace or pick capacity | Ask the Fabric admin for workspace creation and eligible capacity access, or use an approved existing workspace. |
| CSV load fails | Use the individual file's menu, lowercase table name, a comma separator, and checked column header. Review the load status and Fabric's error. |
| Dates/amounts/keys load as text or incompatible types | **Load to tables doesn't support a custom schema.** Use a no-code Dataflow Gen2: create **Dataflow Gen2** in the workspace; use **Get data > Text/CSV > Upload file** to import the affected local CSV, choose **Organizational account**, and sign in. The upload is stored in your work or school OneDrive. Promote headers if needed and set column types with the Power Query UI; choose **Add data destination > Lakehouse**, select the workshop Lakehouse and a **new** lowercase table, then save and run. Recheck types and values, then select that table in the model. See [Power Query file upload](https://learn.microsoft.com/en-us/power-query/upload-file) and [Dataflow destinations](https://learn.microsoft.com/en-us/fabric/data-factory/dataflow-gen2-data-destinations-and-managed-settings). This optional fallback adds a dataflow item, not Python/SQL code. Automatic destination settings can replace and recreate the table on refresh, affecting downstream models; review the destination settings before refreshing. |
| Monetary numbers appear as floating point | Validate the expected two-decimal results. For production use fixed-precision data prepared through an appropriate governed ingestion process; formatting alone doesn't restore precision. |
| Model relationships are ambiguous or don't filter as expected | Use exactly the six relationships in the model guide. Dealer-to-invoice/payment filtering is intentionally not an active path; don't use unvalidated collections visuals. |
| Missing Data Agent or Prep for AI | Verify capacity, tenant AI settings, permissions, region, and feature availability. |
| Agent gives incorrect or stale answers | Recheck types, relationships, selected tables, Prep for AI, and the explicit question/date. Start a new conversation and compare to the answer key. CSV upload and Delta table load are separate; an updated file doesn't refresh a table automatically. |
| MCP server isn't shown or authentication fails | Publish first; copy the URL from the agent's MCP settings; confirm client support for streamable HTTP and its ability to attach a Fabric bearer token. See [MCP guide](mcp.md). |

## References

- [Create a Fabric workspace](https://learn.microsoft.com/en-us/fabric/fundamentals/create-workspaces)
- [Upload a CSV and create a Delta table](https://learn.microsoft.com/en-us/fabric/data-engineering/get-started-csv-upload)
- [Lakehouse Load to tables options and limitations](https://learn.microsoft.com/en-us/fabric/data-engineering/load-to-tables)
- [Create a semantic model](https://learn.microsoft.com/en-us/fabric/data-warehouse/create-semantic-model)
- [Create a Fabric Data Agent](https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent)
- [Semantic model best practices for Data Agents](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)
- [Data Agent as an MCP server](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server)

Reviewed against Microsoft documentation on November 3, 2026. UI labels and capabilities may change.
