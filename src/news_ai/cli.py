"""CLI interface for News AI Summary"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from news_ai.config import get_config, AppConfig
from news_ai.miniflux_client import MinifluxClient
from news_ai.ai_client import AIClientFactory
from news_ai.summarizer import NewsSummarizer
from news_ai.exporter import MarkdownExporter

app = typer.Typer(
    name="news-ai",
    help="News AI Summary - 基于 Miniflux 的新闻 AI 总结工具",
    add_completion=False,
)
console = Console()


def display_feeds_table(feeds: list) -> None:
    """Display feeds in a formatted table"""
    table = Table(
        title="📋 可用新闻源",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("[ID]", style="bold yellow", width=5)
    table.add_column("名称", style="green", min_width=25)
    table.add_column("分类", style="blue", width=8)
    table.add_column("状态", justify="center", width=6)

    for f in feeds:
        status = "[green]✓[/green]"
        table.add_row(
            f"[bold]{f.id}[/bold]",
            f.title,
            f"[{_get_category_color(f.category)}]{f.category}[/{_get_category_color(f.category)}]",
            status,
        )

    console.print(table)


def _get_category_color(category: str) -> str:
    """Get color for category"""
    colors = {
        "资讯": "cyan",
        "研报": "magenta",
        "策略": "yellow",
        "宏观": "green",
        "晨报": "blue",
        "社群": "red",
        "热点": "orange",
    }
    return colors.get(category, "white")


def display_header(config: AppConfig) -> None:
    """Display program header"""
    panel = Panel(
        f"[bold]📰 News AI Summary[/bold]\n"
        f"[dim]{'─' * 50}[/dim]\n"
        f"数据源: [link]{config.miniflux.url}[/link]  │  "
        f"AI: [yellow]{config.ai.provider.upper()}[/yellow] {config.ai.model}",
        box=box.DOUBLE,
        style="bold cyan",
    )
    console.print(panel)


def interactive_select_feeds(client: MinifluxClient) -> list:
    """Interactive feed selection"""
    console.print("\n[bold]📋 请选择要分析的 Feeds（多选）[/bold]")
    console.print("[dim]输入编号，用空格分隔，例如: 1 3 5[/dim]")
    console.print("[dim]或输入 'a' 选择全部[/dim]\n")

    all_feeds = client.list_feeds()
    display_feeds_table(all_feeds)

    while True:
        try:
            choice = console.input("\n[bold cyan]请选择 Feeds[/bold cyan]: ").strip()
            if choice.lower() == 'a':
                return all_feeds

            selected_ids = [int(x.strip()) for x in choice.split()]
            selected_feeds = [f for f in all_feeds if f.id in selected_ids]

            if not selected_feeds:
                console.print("[red]⚠️  未选择任何 Feed，请重试[/red]")
                continue

            console.print(f"[green]已选择 {len(selected_feeds)} 个 Feeds[/green]")
            return selected_feeds

        except ValueError:
            console.print("[red]⚠️  输入格式错误，请输入数字编号[/red]")


@app.command()
def list(
    config_path: Optional[Path] = typer.Option(None, help="配置文件路径"),
) -> None:
    """列出所有配置的 feeds"""
    config = get_config()
    display_header(config)

    try:
        with console.status("[bold cyan]正在连接 Miniflux...[/bold cyan]"):
            client = MinifluxClient(
                url=config.miniflux.url,
                api_key=config.miniflux.api_key,
            )
            feeds = client.list_feeds()

        console.print(f"\n[green]✅ 成功获取 {len(feeds)} 个 Feeds[/green]\n")
        display_feeds_table(feeds)

    except Exception as e:
        console.print(f"[red]❌ 连接 Miniflux 失败: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def summary(
    feeds: Optional[str] = typer.Option(None, help="Feed IDs，逗号分隔"),
    limit: int = typer.Option(20, help="每个 feed 获取的新闻数"),
    output: Optional[Path] = typer.Option(None, help="输出目录"),
    interactive: bool = typer.Option(False, help="交互式选择 feeds"),
) -> None:
    """生成新闻总结"""
    config = get_config()
    display_header(config)

    # Step 1: Get Feeds
    try:
        with console.status("[bold cyan]正在连接 Miniflux...[/bold cyan]"):
            client = MinifluxClient(
                url=config.miniflux.url,
                api_key=config.miniflux.api_key,
            )
            all_feeds = client.list_feeds()

        console.print(f"[green]✅ 成功获取 {len(all_feeds)} 个 Feeds[/green]")
    except Exception as e:
        console.print(f"[red]❌ 连接 Miniflux 失败: {e}[/red]")
        raise typer.Exit(code=1)

    # Step 2: Select Feeds
    if interactive or not feeds:
        selected_feeds = interactive_select_feeds(client)
    else:
        try:
            feed_ids = [int(fid.strip()) for fid in feeds.split(",")]
            selected_feeds = [f for f in all_feeds if f.id in feed_ids]

            if not selected_feeds:
                console.print("[red]❌ 未找到匹配的 Feeds[/red]")
                console.print("\n[bold]可用的 Feeds:[/bold]")
                display_feeds_table(all_feeds)
                raise typer.Exit(code=1)

            console.print(f"[cyan]已选择 {len(selected_feeds)} 个 Feeds[/cyan]")
        except ValueError:
            console.print("[red]❌ Feed ID 格式错误，请使用逗号分隔的数字[/red]")
            raise typer.Exit(code=1)

    # Step 3: Get News
    feed_ids = [f.id for f in selected_feeds]
    try:
        with console.status(f"[cyan]正在获取 {len(feed_ids)} 个 Feeds 的新闻...[/cyan]"):
            entries = client.get_entries(feed_ids, limit=limit)

        console.print(f"[green]✅ 已获取 {len(entries)} 条新闻[/green]")
    except Exception as e:
        console.print(f"[red]❌ 获取新闻失败: {e}[/red]")
        raise typer.Exit(code=1)

    if not entries:
        console.print("[yellow]⚠️  警告: 所有指定 Feeds 暂无新闻[/yellow]")

    # Step 4: AI Analysis
    if entries and config.ai.api_key:
        try:
            with console.status("[bold yellow]🤖 正在调用 AI 进行分析...[/bold yellow]"):
                ai_client = AIClientFactory.create(
                    provider=config.ai.provider,
                    config={
                        "api_key": config.ai.api_key,
                        "model": config.ai.model,
                        "max_tokens": config.ai.max_tokens,
                        "temperature": config.ai.temperature,
                    },
                )
                summarizer = NewsSummarizer(ai_client)
                report = summarizer.summarize(entries, selected_feeds)

            console.print(f"[green]✅ AI 分析完成[/green]")
        except Exception as e:
            console.print(f"[red]❌ AI 分析失败: {e}[/red]")
            raise typer.Exit(code=1)
    elif not config.ai.api_key:
        console.print("[yellow]⚠️  AI API Key 未配置，跳过分析[/yellow]")
        raise typer.Exit(code=1)
    else:
        console.print("[yellow]⚠️  无新闻可分析[/yellow]")
        raise typer.Exit(code=1)

    # Step 5: Export Report
    output_dir = output or Path.cwd()
    try:
        exporter = MarkdownExporter(str(output_dir))
        filepath = exporter.export(report)
    except PermissionError as e:
        console.print(f"[red]❌ 导出失败: {e}[/red]")
        raise typer.Exit(code=1)

    # Done
    console.print(Panel.fit(
        f"[bold green]✨ 总结完成！[/bold green]\n\n"
        f"📄 报告已保存到:\n[link]{filepath}[/link]\n\n"
        f"📊 统计信息:\n"
        f"   • Feeds 数量: {len(selected_feeds)}\n"
        f"   • 新闻总数: {report.total_count}\n"
        f"   • 情感倾向: {report.result.sentiment}",
        title="✅ 任务完成",
        border_style="green",
    ))


@app.command()
def config_check() -> None:
    """检查配置是否正确"""
    config = get_config()

    console.print("\n[bold]🔍 配置检查[/bold]\n")

    # Check Miniflux
    try:
        client = MinifluxClient(
            url=config.miniflux.url,
            api_key=config.miniflux.api_key,
        )
        success, message = client.test_connection()
        if success:
            console.print(f"[green]✓ Miniflux[/green]  连接成功 ({message})")
        else:
            console.print(f"[red]✗ Miniflux[/red]  连接失败: {message}")
    except Exception as e:
        console.print(f"[red]✗ Miniflux[/red]  连接失败: {e}")

    # Check AI
    if config.ai.api_key:
        console.print(f"[green]✓ AI API Key[/green]  已配置")
        console.print(f"  Provider: {config.ai.provider}")
        console.print(f"  Model: {config.ai.model}")
    else:
        console.print(f"[red]✗ AI API Key[/red]  未配置")
        console.print("\n  请设置环境变量:")
        console.print("  export OPENAI_API_KEY=\"your_api_key\"")
        console.print("  export ANTHROPIC_API_KEY=\"your_api_key\"")

    console.print()


def main() -> None:
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
