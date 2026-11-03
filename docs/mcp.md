# Call the published Data Agent as an MCP server

The Model Context Protocol (MCP) connects an AI client to discoverable tools. After publication, a Fabric Data Agent exposes **one MCP tool representing that agent**. A compatible client sends a natural-language question to that tool and receives the agent's response.

The MCP server is the **Data Agent's own endpoint**, not the Fabric Core MCP server or a generic Lakehouse MCP endpoint. It's not a plain REST URL to which you can send arbitrary questions: the client must perform the MCP initialization and tool discovery/call protocol.

## Prerequisites

- Complete the [workshop](workshop.md) through semantic model creation and Data Agent configuration.
- **Publish** `Nowcom Billing Analyst`. The MCP server is available only for a published agent.
- Meet the Data Agent capacity and tenant settings described in [workshop prerequisites](workshop.md#prerequisites).
- The caller must be authorized to use the published agent and the data/semantic model. Access to the agent doesn't automatically grant access to data.
- Use an MCP client that supports **streamable HTTP** and can authenticate to Fabric and attach a valid Fabric bearer token to every request.
- Use an organization-approved client. Responses sent to an MCP client may leave Fabric's compliance boundary or geographic region and be processed under the client's policies. This workshop uses fictional data, but obtain approval before connecting real business data.

## 1. Copy your agent's MCP details

1. In Fabric, open the **published** Data Agent.
2. Select **Settings > Model Context Protocol**.
3. Copy the **MCP server URL**. Note the Data Agent MCP server name, tool name, and tool description shown on that tab.
4. The tab can also download an `mcp.json` file for a compatible client. Treat it as configuration; never put bearer tokens or secrets in a repository.

The URL is specific to the workspace and published agent. Its documented shape is:

```text
https://api.fabric.microsoft.com/v1/mcp/workspaces/{WorkspaceId}/dataagents/{DataAgentId}/agent
```

Copy the actual value from Fabric rather than guessing IDs. Publishing the agent exposes its description as the tool description, which helps the client decide when to call it.

## 2. Connect from Visual Studio Code

1. Open a local folder in VS Code. In that folder create a `.vscode` folder and an `mcp.json` file, or use the file downloaded from Fabric's MCP settings.
2. In `mcp.json`, select VS Code's **Add Server**, choose **HTTP**, and paste the copied agent MCP URL. Give it a recognizable name such as `Nowcom Billing Agent`.
3. When prompted, use the client's Fabric sign-in flow and sign in as an authorized work/school user. Approve only the connection and permissions appropriate for your organization.
4. Start the server and confirm that VS Code shows it as connected and discovers the agent's one tool. If the client asks which tools to enable, enable the displayed Data Agent tool.
5. In GitHub Copilot Chat choose **Agent** mode and an available model. Ask: “Use the Nowcom Billing Agent to tell me October 2026 net billed revenue in USD.”
6. Approve the tool call if prompted. Inspect the tool call and answer. The baseline result should be **$66,728.00**. Compare it with the report visual and the Data Agent's own chat.

VS Code's exact commands and prompts can vary by version. See Microsoft's [Data Agent MCP documentation](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server) for the current client-specific flow.

## Authentication and limitations

Microsoft documents a Fabric token scope of `https://api.fabric.microsoft.com/.default`. The MCP server **doesn't support dynamic client registration or client identity metadata**. A client relying solely on automatic registration may fail; it must support its own compatible authentication flow and attach the Fabric bearer token. VS Code's documented interactive sign-in is one option when supported by the installed version and tenant. A generic MCP client with no token-injection mechanism isn't sufficient. Don't paste tokens into `mcp.json`, source control, or chat.

For long-running questions, the server can support the MCP tasks extension if the client implements it; otherwise the call uses the normal connection. Timeouts don't prove that the agent's calculations are wrong.

| Problem | Check |
|---|---|
| MCP settings missing or URL errors | Confirm the agent was **published**, then reopen Settings > Model Context Protocol. Copy the agent URL again. |
| Can't sign in or client asks for unsupported dynamic registration | Check that the client can authenticate independently and send a Fabric bearer token on each request; consult your admin and the current Microsoft documentation. |
| Permission error | Verify the signed-in identity has access to the agent and its semantic model/data. |
| Tool isn't discovered | Confirm streamable HTTP support and that you added the Data Agent URL, not a generic Fabric MCP URL. Restart the server after correcting configuration. |
| Answer differs from $66,728 | First check the question, model types/relationships, loaded data and permissions in Fabric; then inspect the MCP tool response. Agent answers aren't guaranteed. |

Reference: [Data agent as Model Context Protocol server](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server).
