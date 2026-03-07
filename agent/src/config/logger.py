from loguru import logger


def log_agent_event(event):
    if "model" in event:
        msgs = event["model"]["messages"]
        for m in msgs:
            logger.info(
                f"""
                🔵 MODEL OUTPUT
                Type: {getattr(m, "type", "unknown")}
                Content:
                {str(m.content)[:500]}
                Tool Calls:
                {getattr(m, "tool_calls", None)}
                """
            )
    elif "tools" in event:
        msgs = event["tools"]["messages"]
        logger.info(
            f"""
            🟢 TOOL EXECUTION
            Tool: {getattr(msgs[-1], "name", "")}
            Output:
            {msgs[-1].content[:500]}
            """
        )
