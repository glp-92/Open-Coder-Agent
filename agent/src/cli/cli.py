import traceback

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage
from langgraph.graph.state import CompiledStateGraph
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


def run_cli(user_input: str, graph: CompiledStateGraph, initial_state: any):
    all_nodes: list[str] = list(graph.get_graph().nodes)
    last_node: str = "__start__"
    console = Console()
    console.print(Panel(f"[bold blue]Prompt:[/bold blue] {user_input}", title="🚀 AGENT START", border_style="blue"))
    try:
        for event in graph.stream(initial_state, stream_mode="updates"):
            event: dict[str, any]
            for node_name, state_update in event.items():
                transition = (
                    f"[dim]{last_node}[/dim] [bold cyan]➔[/bold cyan] "
                    f"[bold reverse green] {node_name} [/bold reverse green]"
                )
                others = " | ".join([f"[dim]{n}[/dim]" for n in all_nodes if n != node_name])
                console.print(
                    f"\n[bold magenta]📍 Step:[/bold magenta] {transition}  [dim](available nodes: {others})[/dim]"
                )
                last_node = node_name
                if "messages" in state_update:
                    last_message: BaseMessage = state_update["messages"][-1]
                    if isinstance(last_message, SystemMessage) and "Summary" in str(last_message.content):
                        console.print(
                            Panel(
                                f"[bold cyan]{last_message.content}[/bold cyan]",
                                title="🧠 MEMORY COMPACTED",
                                border_style="cyan",
                                subtitle="Tokens optimized",
                            )
                        )
                    elif isinstance(last_message, AIMessage):
                        clean_content: str = last_message.content.strip()
                        if clean_content:
                            console.print(
                                Panel(
                                    Markdown(str(clean_content)),
                                    title="🤖 AI Thinking",
                                    border_style="green",
                                    padding=(1, 2),
                                )
                            )
                        if last_message.tool_calls:
                            table = Table(show_header=True, header_style="bold cyan", title="🛠️ Running tools")
                            table.add_column("Tool")
                            table.add_column("Args")
                            for tool in last_message.tool_calls:
                                table.add_row(tool["name"], str(tool["args"]))
                            console.print(table)
                    elif isinstance(last_message, ToolMessage):
                        content_str = str(last_message.content)
                        content_preview = (content_str[:500] + "...") if len(content_str) > 500 else content_str
                        console.print(
                            Panel(
                                content_preview,
                                title=f"📥 Result: {last_message.name}",
                                border_style="yellow",
                                subtitle="Truncated output" if len(content_str) > 500 else "",
                            )
                        )
    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Process finished by user.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Critical error:[/bold red] {e}")
        console.print(f"\n[bold red]{traceback.format_exc()}[/bold red]")
    finally:
        console.print("✅ [bold green]FINISHED TASK[/bold green]", justify="center")
