"""
GuardCommit Command Line Interface.
Built with Typer and Rich for beautiful terminal developer experience.
"""

from __future__ import annotations
import sys
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import typer
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from guardcommit import __version__
from guardcommit.config import Config, load_config, save_config
from guardcommit.generator import generate_commit_options, generate_pull_request
from guardcommit.git_utils import (
    GitError,
    execute_commit,
    get_branch_diff_against_base,
    get_current_branch,
    get_staged_diff,
    get_staged_files,
    is_git_repository,
)
from guardcommit.hook import install_git_hook, uninstall_git_hook
from guardcommit.providers.base import LLMResponse
from guardcommit.providers.factory import get_provider
from guardcommit.reviewer import review_staged_code
from guardcommit.scanner import scan_staged_changes

app = typer.Typer(
    name="guardcommit",
    help="GuardCommit: Blazing fast Git AI code review, secret leak detector & conventional commit generator.",
    add_completion=False,
    no_args_is_help=True,
)
hook_app = typer.Typer(help="Manage Git pre-commit hooks for automated secret blocking.")
app.add_typer(hook_app, name="hook")

console = Console(force_terminal=True)


def _print_token_stats(stats: LLMResponse):
    """Render a sleek performance, token, and cost badge."""
    cost_str = f"${stats.estimated_cost_usd:.5f}" if stats.estimated_cost_usd > 0 else "FREE ($0.00)"
    info = (
        f"[dim]⚡ [bold cyan]{stats.provider_name}[/bold cyan] ({stats.model_name}) | "
        f"Tokens: [bold green]{stats.total_tokens}[/bold green] (in: {stats.prompt_tokens}, out: {stats.completion_tokens}) | "
        f"Cost: [bold yellow]{cost_str}[/bold yellow] | "
        f"Latency: [bold magenta]{stats.latency_ms}ms[/bold magenta][/dim]"
    )
    console.print(Panel(info, border_style="dim", expand=False))


@app.callback(invoke_without_command=True)
def version_callback(
    version: Optional[bool] = typer.Option(None, "--version", "-v", help="Show GuardCommit version.")
):
    if version:
        rprint(f"[bold cyan]guardcommit[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.command(name="scan")
def scan_cmd(
    exit_on_error: bool = typer.Option(
        False, "--exit-on-error", "-e", help="Exit with code 1 if secrets or dangerous files are found (for CI/Hooks)."
    )
):
    """
    Scan staged files and diff for leaked API keys, tokens, and sensitive files (.env).
    """
    if not is_git_repository():
        console.print("[bold red]Error:[/bold red] Current directory is not a Git repository.")
        raise typer.Exit(code=1)

    staged_files = get_staged_files()
    if not staged_files:
        console.print("[dim yellow]No staged changes detected to scan. (Run 'git add' first)[/dim yellow]")
        raise typer.Exit(code=0)

    diff = get_staged_diff()
    findings = scan_staged_changes(staged_files, diff)

    if not findings:
        console.print(
            Panel(
                f"[bold green]✔ Security Audit Passed![/bold green]\n"
                f"[dim]Scanned {len(staged_files)} staged file(s). Zero sensitive keys or credentials detected.[/dim]",
                border_style="green",
                expand=False,
            )
        )
        return

    table = Table(title="🚨 High-Risk Credentials Detected in Staged Changes!", border_style="red")
    table.add_column("Severity", style="bold red", justify="center")
    table.add_column("Rule / Secret Type", style="cyan")
    table.add_column("File", style="yellow")
    table.add_column("Line", style="magenta", justify="center")
    table.add_column("Snippet (Masked)", style="white")

    for f in findings:
        line_str = str(f.line_number) if f.line_number is not None else "Filename"
        table.add_row(f.severity, f.rule_name, f.file_path, line_str, f.matched_snippet)

    console.print(table)
    console.print(
        "\n[bold red]⚠️ Security Alert:[/bold red] Please unstage or remove these credentials before committing!\n"
    )

    if exit_on_error:
        raise typer.Exit(code=1)


@app.command(name="review")
def review_cmd(
    provider_name: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM Provider: groq, ollama, gemini, openai"),
):
    """
    Perform an automated pre-commit AI code review on staged diffs.
    """
    if not is_git_repository():
        console.print("[bold red]Error:[/bold red] Current directory is not a Git repository.")
        raise typer.Exit(code=1)

    staged_files = get_staged_files()
    if not staged_files:
        console.print("[dim yellow]No staged changes found to review. (Run 'git add' first)[/dim yellow]")
        raise typer.Exit(code=0)

    diff = get_staged_diff()
    provider = get_provider(provider_name)

    with console.status(f"[bold cyan]Reviewing {len(staged_files)} staged files with {provider.__class__.__name__}...[/bold cyan]"):
        try:
            report, stats = review_staged_code(diff, provider)
        except Exception as e:
            console.print(f"[bold red]AI Review Failed:[/bold red] {e}")
            raise typer.Exit(code=1)

    console.print("\n" + "=" * 60)
    console.print(Markdown(report))
    console.print("=" * 60 + "\n")
    _print_token_stats(stats)


@app.command(name="commit")
def commit_cmd(
    provider_name: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM Provider: groq, ollama, gemini, openai"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Generate commit message without executing git commit."),
    skip_scan: bool = typer.Option(False, "--skip-scan", help="Skip the pre-commit secret leak scanner."),
):
    """
    Generate Conventional Commits from staged diffs with interactive confirmation.
    """
    if not is_git_repository():
        console.print("[bold red]Error:[/bold red] Current directory is not a Git repository.")
        raise typer.Exit(code=1)

    staged_files = get_staged_files()
    if not staged_files:
        console.print("[dim yellow]No staged changes detected. Stage your changes with 'git add' first.[/dim yellow]")
        raise typer.Exit(code=0)

    diff = get_staged_diff()

    if not skip_scan:
        findings = scan_staged_changes(staged_files, diff)
        critical_findings = [f for f in findings if f.severity in ("CRITICAL", "HIGH")]
        if critical_findings:
            console.print(f"[bold red]🚨 BLOCKED: {len(critical_findings)} high-risk credentials detected in staged diff![/bold red]")
            console.print("[dim]Run 'guardcommit scan' to inspect findings or '--skip-scan' to force commit.[/dim]")
            raise typer.Exit(code=1)

    provider = get_provider(provider_name)
    with console.status(f"[bold magenta]Analyzing diff with {provider.__class__.__name__}...[/bold magenta]"):
        try:
            options, body, stats = generate_commit_options(diff, provider)
        except Exception as e:
            console.print(f"[bold red]Commit Generation Failed:[/bold red] {e}")
            raise typer.Exit(code=1)

    if not options:
        options = ["chore: update staged files"]

    console.print("\n[bold cyan]Select a Conventional Commit Title:[/bold cyan]")
    for idx, opt in enumerate(options, 1):
        console.print(f"  [bold green][{idx}][/bold green] {opt}")
    console.print("  [bold yellow][e][/bold yellow] Edit custom commit title")
    console.print("  [bold red][c][/bold red] Cancel")

    choice = Prompt.ask("\nChoose an option", default="1")
    if choice.lower() == "c":
        console.print("[dim]Commit aborted.[/dim]")
        raise typer.Exit(code=0)
    elif choice.lower() == "e":
        final_title = Prompt.ask("Enter your custom commit message")
    else:
        try:
            idx = int(choice) - 1
            final_title = options[idx] if 0 <= idx < len(options) else options[0]
        except ValueError:
            final_title = options[0]

    full_message = final_title
    if body and Confirm.ask("Include detailed bullet points in commit body?", default=True):
        full_message = f"{final_title}\n\n{body}"

    console.print("\n[bold]Final Commit Message:[/bold]")
    console.print(Panel(full_message, border_style="cyan"))
    _print_token_stats(stats)

    if dry_run:
        console.print("[dim yellow]Dry run enabled. Git commit was not executed.[/dim yellow]")
        return

    try:
        execute_commit(full_message)
        console.print("[bold green]✔ Committed successfully![/bold green]")
    except GitError as e:
        console.print(f"[bold red]Commit error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(name="pr")
def pr_cmd(
    base: str = typer.Option("main", "--base", "-b", help="Base branch to compare against (e.g. main, master)."),
    provider_name: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM Provider: groq, ollama, gemini, openai"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Write generated PR markdown to a file."),
):
    """
    Generate a production-grade GitHub Pull Request description from your branch diff.
    """
    if not is_git_repository():
        console.print("[bold red]Error:[/bold red] Current directory is not a Git repository.")
        raise typer.Exit(code=1)

    branch = get_current_branch()
    console.print(f"[bold cyan]Comparing current branch '[yellow]{branch}[/yellow]' against '[yellow]{base}[/yellow]'...[/bold cyan]")

    try:
        diff = get_branch_diff_against_base(base_branch=base)
    except GitError as e:
        console.print(f"[bold red]Failed to get branch diff:[/bold red] {e}")
        raise typer.Exit(code=1)

    if not diff.strip():
        console.print(f"[dim yellow]No differences found between {branch} and {base}.[/dim yellow]")
        raise typer.Exit(code=0)

    provider = get_provider(provider_name)
    with console.status("[bold cyan]Generating PR description...[/bold cyan]"):
        try:
            pr_markdown, stats = generate_pull_request(diff, base, provider)
        except Exception as e:
            console.print(f"[bold red]PR Generation Failed:[/bold red] {e}")
            raise typer.Exit(code=1)

    console.print("\n" + "=" * 60)
    console.print(Markdown(pr_markdown))
    console.print("=" * 60 + "\n")
    _print_token_stats(stats)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(pr_markdown)
        console.print(f"[bold green]PR markdown written to [cyan]{output_file}[/cyan][/bold green]")


@hook_app.command(name="install")
def hook_install_cmd():
    """
    Install GuardCommit as an automated Git pre-commit hook in the current repository.
    """
    try:
        hook_path = install_git_hook()
        console.print(
            Panel(
                f"[bold green]Pre-commit hook installed successfully![/bold green]\n"
                f"[dim]Location: {hook_path}\n"
                f"GuardCommit will now automatically block leaked secrets & dangerous files whenever 'git commit' is run.[/dim]",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(f"[bold red]Hook Installation Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@hook_app.command(name="uninstall")
def hook_uninstall_cmd():
    """
    Remove GuardCommit pre-commit hook from the current repository.
    """
    try:
        removed = uninstall_git_hook()
        if removed:
            console.print("[bold yellow]Pre-commit hook removed.[/bold yellow]")
        else:
            console.print("[dim]No existing GuardCommit pre-commit hook found.[/dim]")
    except Exception as e:
        console.print(f"[bold red]Hook Removal Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(name="config")
def config_cmd():
    """
    Interactive configuration wizard for API keys and default LLM provider.
    """
    cfg = load_config()
    console.print("\n[bold cyan]GuardCommit Configuration Wizard[/bold cyan]")
    console.print(f"Current Default Provider: [bold green]{cfg.default_provider}[/bold green]\n")

    provider = Prompt.ask("Choose default provider", choices=["groq", "ollama", "gemini", "openai"], default=cfg.default_provider)
    cfg.default_provider = provider

    if provider == "groq":
        key = Prompt.ask("Enter Groq API Key (starts with gsk_)", default=cfg.groq_api_key or "")
        if key:
            cfg.groq_api_key = key
        model = Prompt.ask("Enter Groq Model", default=cfg.groq_model)
        cfg.groq_model = model
    elif provider == "ollama":
        endpoint = Prompt.ask("Enter Ollama Endpoint", default=cfg.ollama_endpoint)
        cfg.ollama_endpoint = endpoint
        model = Prompt.ask("Enter Ollama Model", default=cfg.ollama_model)
        cfg.ollama_model = model
    elif provider == "gemini":
        key = Prompt.ask("Enter Gemini API Key", default=cfg.gemini_api_key or "")
        if key:
            cfg.gemini_api_key = key
        model = Prompt.ask("Enter Gemini Model (e.g. gemini-2.0-flash, gemini-flash-lite, gemini-2.5-pro)", default=cfg.gemini_model)
        cfg.gemini_model = model
    elif provider == "openai":
        key = Prompt.ask("Enter OpenAI API Key (starts with sk-)", default=cfg.openai_api_key or "")
        if key:
            cfg.openai_api_key = key
        model = Prompt.ask("Enter Model", default=cfg.openai_model)
        cfg.openai_model = model

    save_config(cfg)
    console.print("[bold green]✔ Configuration saved successfully![/bold green]\n")


if __name__ == "__main__":
    app()
