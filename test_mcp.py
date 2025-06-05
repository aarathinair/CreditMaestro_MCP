# test_mcp.py

from unity_mcp_client.client import UnityMCP
import json

# Initialize the MCP client with your registry (positional args)
client = UnityMCP(
    "mcp_registry.json",  # first arg: path to the registry file
    "plaid"               # second arg: the default server ID
)

# Call the getTransactions operation via MCP
resp = client.call(
    operation_id="getTransactions",
    params={
        "startDate": "2025-04-01",
        "endDate":   "2025-04-30"
    }
)

# Print out the result
print(json.dumps(resp, indent=2))
