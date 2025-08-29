#!/usr/bin/env python3

# @owner: nick
# @expose
# @maturity: stable

"""
Slim wrapper for EchoAgent API.

- Keeps import path compatibility: `from echo_engine.echo_agent_api import app`
- Delegates to the modular slim implementation.
"""
from .echo_agent_api_slim import app  # re-export

__all__ = ["app"]

if __name__ == "__main__":
    # Optional local run helper
    import uvicorn

    uvicorn.run(
        "echo_engine.echo_agent_api:app", host="0.0.0.0", port=9000, reload=False
    )
