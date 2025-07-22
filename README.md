# Build your own Local MCP Client with LlamaIndex

This project demonstrates how to build a **local MCP (Model Context Protocol) client** using LlamaIndex. The client connects to a local MCP server (which exposes tools like a SQLite database) and lets you interact with it using natural language and tool-calling agents—all running locally on your machine.

## Architecture

[![](https://mermaid.ink/img/pako:eNqFVO9v2jAQ_VciV5U2ibYJkEGiqlKBVkOiarfQL0v2wYQLjebYke10ZU3_9_lHAoFWGxLg49753r134RWlbA0oRBuOyydnOUmoo16iWtkfpiQHKuME2YOzwFvgCfppYfr1OI8fBXBnTiXwDKfQyV1vdPFtRVOZM2qiTnaxuIvVe195ueIXV_eE4AJf3JdAr-cd9N30oSEzwSJPd-EhZMkYEfFdWupDVELapIGuE3o0WwT8GbiazR4-mO0WC6kujZvvpqIDsO30p_MdNrmQfNvJzibxp-jbIpfgzLDEKyzg8z_4TFlRVDRPsRZLS96NP2AXRTexZXQWaW9untWnMCKqlPPAmWQpI-87np46XTtVY0rBWCQs4HHunJ1d1Y2vZSVra6XNmqMBmMGnmBBR78S3mDbawxZKnXrv4vFVehEU4xSEyOmm1sthITvKXZfeU24t2vVr_DDi1U6H2p5Xa4qjls0C1RyzyVHfj2ygBxvpXOrbvi6XDxdK-FobYxHaBpMz1jiR5ICLuuXascMwviXs9zFFk5hBltO84fc_nW9eIK0Oht4rKLdEiWvjlGAh1M3qYGbIckLCE_AyP4OeEo79gvDE9fxRsDoqENYIW5ANwM_8XcEQe8NxetxBKdjeP858CHZwb-VD3-0Kbora9Uw7q2ITzRJYCgcVBy7pjqin_tTyNQolr6CHCuAF1iF61XUJkk9QQIJCdVxDhisiE5TQN1VWYvqDsaKt5KzaPKEww0SoqCrXWMIsx-qh3UPU0wV8yioqUeh5nmsuQeErekHhyOufjweB1x8Ho_5oMAx6aKtR_fOB7w6HA9cdBd4X13vroT-mrXs-9tyBP_D8IFCA8dtfrS7MNQ?type=png)](https://mermaid.live/edit#pako:eNqFVO9v2jAQ_VciV5U2ibYJkEGiqlKBVkOiarfQL0v2wYQLjebYke10ZU3_9_lHAoFWGxLg49753r134RWlbA0oRBuOyydnOUmoo16iWtkfpiQHKuME2YOzwFvgCfppYfr1OI8fBXBnTiXwDKfQyV1vdPFtRVOZM2qiTnaxuIvVe195ueIXV_eE4AJf3JdAr-cd9N30oSEzwSJPd-EhZMkYEfFdWupDVELapIGuE3o0WwT8GbiazR4-mO0WC6kujZvvpqIDsO30p_MdNrmQfNvJzibxp-jbIpfgzLDEKyzg8z_4TFlRVDRPsRZLS96NP2AXRTexZXQWaW9untWnMCKqlPPAmWQpI-87np46XTtVY0rBWCQs4HHunJ1d1Y2vZSVra6XNmqMBmMGnmBBR78S3mDbawxZKnXrv4vFVehEU4xSEyOmm1sthITvKXZfeU24t2vVr_DDi1U6H2p5Xa4qjls0C1RyzyVHfj2ygBxvpXOrbvi6XDxdK-FobYxHaBpMz1jiR5ICLuuXascMwviXs9zFFk5hBltO84fc_nW9eIK0Oht4rKLdEiWvjlGAh1M3qYGbIckLCE_AyP4OeEo79gvDE9fxRsDoqENYIW5ANwM_8XcEQe8NxetxBKdjeP858CHZwb-VD3-0Kbora9Uw7q2ITzRJYCgcVBy7pjqin_tTyNQolr6CHCuAF1iF61XUJkk9QQIJCdVxDhisiE5TQN1VWYvqDsaKt5KzaPKEww0SoqCrXWMIsx-qh3UPU0wV8yioqUeh5nmsuQeErekHhyOufjweB1x8Ho_5oMAx6aKtR_fOB7w6HA9cdBd4X13vroT-mrXs-9tyBP_D8IFCA8dtfrS7MNQ)

The diagram above illustrates the key components and their interactions in the MCP architecture:
- Client Layer: Handles user interactions and tool management
- Server Layer: Manages tool execution and database operations
- Communication Layer: Facilitates real-time communication between client and server

### Setup

To sync dependencies, run:

```sh
python -m pip install -r requirements.txt
```

---

## Usage

- Start the local MCP server (for example, the included SQLite demo server):

```sh
uv run server.py --server_type=sse
```

- Run the client (choose the appropriate client script, e.g. `ollama_client.ipynb` for Ollama):

```sh
uv run client.py
```

- Interact with the agent in your terminal. Type your message and the agent will use the available tools to answer your queries.

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.