

import sys

from fastmcp import Client
from fastmcp.client.transports import (
    StdioTransport
)

client = Client(

    StdioTransport(

        command=sys.executable,

        args=[

            r"C:/Users/New/Downloads/Projects/first_lexi_ai_agent/backend/src/mcp/mcp_local_servers/main.py"
        ]
    )
)