from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage


@wrap_tool_call
def tool_error_handler(request, handler):
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"tool error: ({e!s})",
            tool_call_id=request.tool_call["id"],
        )
