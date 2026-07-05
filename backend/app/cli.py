import os
import sys
import json
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.status import Status
from rich.live import Live

from backend.app.config.config import load_config, save_config, get_config_path
from backend.app.models.models import LLMConfig, Issue, ReviewReport
from backend.app.graph.workflow import run_review_workflow

app = typer.Typer(help="AI Secure Review CLI - Code security and quality audit tool.")
console = Console()

REPORTS_DIR = Path(os.path.expanduser("~")) / ".secure-review" / "reports"

def save_report(report_data: dict) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / f"{report_data['report_id']}.json"
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2)
    return report_file

def ensure_backend_server() -> bool:
    import httpx
    import subprocess
    import sys
    import time
    
    try:
        res = httpx.get("http://localhost:8000/health", timeout=1.0)
        if res.status_code == 200:
            return True
    except Exception:
        pass
        
    console.print("[bold yellow]Starting the server in background...[/bold yellow]")
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        # Set cwd to the workspace root installation directory of the package
        package_root = str(Path(__file__).parent.parent.parent.resolve())
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--port", "8000"],
            cwd=package_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            close_fds=True
        )
        
        # Wait a moment for startup
        for _ in range(5):
            time.sleep(1.0)
            try:
                res = httpx.get("http://localhost:8000/health", timeout=1.0)
                if res.status_code == 200:
                    console.print("[bold green]✓ Backend API started on port 8000.[/bold green]")
                    return True
            except Exception:
                continue
        console.print("[bold red]Failed to start API backend automatically.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error launching backend: {e}[/bold red]")
    return False

@app.command("review")
def review(
    path: str = typer.Argument(".", help="Path to local folder to analyze"),
    path_opt: Optional[str] = typer.Option(None, "-p", "--path", help="Path to local folder to analyze (alternative to argument)"),
    save: bool = typer.Option(True, "--save/--no-save", help="Whether to save JSON report locally")
):
    """
    Run multi-agent code analysis on a repository.
    """
    target_path = path_opt if path_opt is not None else path
    if target_path.startswith(("http://", "https://", "git@")):
        console.print("[bold red]Error: Only local repositories are allowed for scanning.[/bold red]")
        raise typer.Exit(code=1)
    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        console.print(f"[bold red]Error: Local path '{target_path}' does not exist or is not a directory.[/bold red]")
        raise typer.Exit(code=1)
        
    # Start the backend server in background if it's not running
    ensure_backend_server()
            
    # Load LLM Config to verify settings
    config = load_config()
    console.print(f"[bold blue]Using LLM configuration:[/bold blue]")
    console.print(f"  Provider:    [cyan]{config.provider}[/cyan]")
    console.print(f"  Base URL:    [cyan]{config.base_url}[/cyan]")
    console.print(f"  Model name:  [cyan]{config.model}[/cyan]")
    console.print(f"  Config file: [cyan]{get_config_path()}[/cyan]\n")
    
    # Resolve to absolute path
    resolved_path = str(Path(target_path).resolve()).replace('\\', '/')
    console.print(f"[bold green]Starting security and quality audit workflow on:[/bold green] {resolved_path}")
    
    import httpx
    import time
    import webbrowser
    
    # Request background job on API server
    try:
        res = httpx.post("http://localhost:8000/review", json={"repo_path": resolved_path}, timeout=10.0)
        if res.status_code != 200:
            console.print(f"[bold red]Failed to submit job to API backend: {res.text}[/bold red]")
            raise typer.Exit(code=1)
        job_data = res.json()
        report_id = job_data.get("report_id")
    except Exception as e:
        console.print(f"[bold red]Failed to submit job: {e}[/bold red]")
        raise typer.Exit(code=1)
        
    result = None
    # Run audit workflow with visual status indicator
    with Status("[bold magenta]Initializing scanner...[/bold magenta]", console=console, spinner="dots") as status:
        while True:
            try:
                res = httpx.get(f"http://localhost:8000/review/{report_id}/status", timeout=5.0)
                if res.status_code != 200:
                    status.update("[bold red]Retrying status ping...[/bold red]")
                    time.sleep(1.0)
                    continue
                
                data = res.json()
                step = data.get("step")
                status_str = data.get("status")
                
                if status_str == "completed" and step == "done":
                    result = data.get("report")
                    break
                elif status_str == "failed":
                    status.stop()
                    console.print(f"\n[bold red]Workflow execution failed: {data.get('error')}[/bold red]")
                    raise typer.Exit(code=1)
                    
                # Update CLI Rich spinner message based on actual agent node progress
                if step == "scanner":
                    status.update("[bold magenta]Scanning repository file tree...[/bold magenta]")
                elif step == "sast":
                    status.update("[bold cyan]Running Bandit and regex heuristic scans...[/bold cyan]")
                elif step == "planner":
                    status.update("[bold yellow]Planner Agent allocating file analysis workloads...[/bold yellow]")
                elif step == "agents":
                    status.update("[bold purple]Parallel Agents executing security, bug, and design checks...[/bold purple]")
                elif step == "summary":
                    status.update("[bold green]Summary Agent compiling metrics scorecard...[/bold green]")
                    
                time.sleep(1.0)
            except Exception:
                time.sleep(1.0)
            
    console.print("\n[bold green]✓ Audit Completed Successfully![/bold green]\n")
    
    if not result:
        console.print("[bold red]Error: No report was returned by the audit backend.[/bold red]")
        raise typer.Exit(code=1)
        
    # Save Report
    report_file = None
    if save:
        report_file = save_report(result)
        
    # Render scorecard panel
    score = result.get("overall_score", 100)
    grade = "A"
    color = "green"
    if score < 50:
        grade = "F"
        color = "red"
    elif score < 70:
        grade = "D"
        color = "orange3"
    elif score < 85:
        grade = "C"
        color = "yellow"
    elif score < 95:
        grade = "B"
        color = "blue"
        
    scorecard_text = f"[bold {color}]Grade: {grade} ({score}/100)[/bold {color}]\n\n"
    scorecard_text += "[bold]Category Breakdown:[/bold]\n"
    for cat, cat_score in result.get("category_scores", {}).items():
        scorecard_text += f"  - {cat.capitalize()}: {cat_score}/100\n"
        
    console.print(Panel(scorecard_text, title="Audit Scorecard", expand=False))
    console.print()
    
    # Executive Summary panel
    summary = result.get("executive_summary", "")
    console.print(Panel(summary, title="Executive Summary & Priorities", expand=True))
    console.print()
    
    # Issues Table
    issues = result.get("issues", [])
    if issues:
        table = Table(title="Detected Issues")
        table.add_column("ID", style="dim", width=8)
        table.add_column("File:Line", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Severity", style="red")
        table.add_column("Title", style="bold")
        
        for iss in issues:
            short_id = iss.get("id", "")[:8] if isinstance(iss, dict) else iss.id[:8]
            file = iss.get("file", "") if isinstance(iss, dict) else iss.file
            line = iss.get("line", 1) if isinstance(iss, dict) else iss.line
            cat = iss.get("category", "") if isinstance(iss, dict) else iss.category
            sev = iss.get("severity", "") if isinstance(iss, dict) else iss.severity
            title = iss.get("title", "") if isinstance(iss, dict) else iss.title
            
            sev_color = "red" if sev in ("CRITICAL", "HIGH") else ("yellow" if sev == "MEDIUM" else "green")
            
            table.add_row(
                short_id,
                f"{file}:{line}",
                cat,
                f"[{sev_color}]{sev}[/{sev_color}]",
                title
            )
            
        console.print(table)
    else:
        console.print("[bold green]No issues detected in your repository! Good job.[/bold green]")
        
    if report_file:
        console.print(f"\n[bold blue]Full report saved to:[/bold blue] {report_file}")
        
        # Output URL link to Web Dashboard (served directly by backend on port 8000!)
        report_id = result.get("report_id")
        web_url = f"http://localhost:8000/?reportId={report_id}"
        console.print(f"[bold blue]Web Dashboard View URL:[/bold blue] {web_url}")
        
        # Open in browser automatically
        try:
            webbrowser.open(web_url)
            console.print("[green]Opened dashboard in your web browser.[/green]")
        except Exception:
            pass

@app.command("config")
def configure():
    """
    Interactively configure LLM settings.
    """
    config = load_config()
    
    console.print("[bold blue]Configure AI Secure Review LLM Provider[/bold blue]\n")
    
    console.print("Select LLM Provider:")
    console.print("  1) OpenAI")
    console.print("  2) Gemini (Google)")
    console.print("  3) Anthropic (Claude)")
    console.print("  4) Ollama (Local)")
    console.print("  5) LM Studio (Local)")
    console.print("  6) Groq (GroqCloud)")
    
    prov_choice = typer.prompt("Choose provider option (1-6)", default="1")
    
    provider_map = {
        "1": ("openai", "https://api.openai.com/v1", "gpt-4o-mini"),
        "2": ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-1.5-flash"),
        "3": ("anthropic", "https://api.anthropic.com", "claude-3-5-sonnet-20241022"),
        "4": ("ollama", "http://localhost:11434", "llama3.1"),
        "5": ("lmstudio", "http://localhost:1234/v1", "llama3.1"),
        "6": ("groq", "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile")
    }
    
    if prov_choice not in provider_map:
        console.print("[bold red]Invalid provider selection.[/bold red]")
        return
        
    prov_name, default_url, default_model = provider_map[prov_choice]
    
    # Prompt logic based on cloud vs local
    if prov_name in ("openai", "gemini", "anthropic", "groq"):
        # Cloud providers
        api_key = typer.prompt(f"Enter {prov_name.upper()} API Key", default=config.api_key if config.provider == prov_name else "", show_default=False)
        model = typer.prompt("Model name", default=config.model if config.provider == prov_name else default_model)
        base_url = default_url
    else:
        # Local providers
        base_url = typer.prompt(f"Enter {prov_name.upper()} Base URL", default=config.base_url if config.provider == prov_name else default_url)
        model = typer.prompt("Model name", default=config.model if config.provider == prov_name else default_model)
        api_key = ""
        
    temp_str = typer.prompt("Temperature (0.0 to 1.0)", default=str(config.temperature))
    try:
        temp = float(temp_str)
    except ValueError:
        temp = 0.2
        
    new_config = LLMConfig(
        provider=prov_name,
        base_url=base_url,
        model=model,
        api_key=api_key,
        temperature=temp
    )
    
    save_config(new_config)
    console.print(f"\n[bold green]✓ Configuration saved locally to {get_config_path()}[/bold green]")

@app.command("providers")
def providers():
    """
    Show current provider details.
    """
    config = load_config()
    console.print("[bold blue]Configured Provider Status:[/bold blue]")
    console.print(f"  Current Provider: [cyan]{config.provider}[/cyan]")
    console.print(f"  Endpoint:         [cyan]{config.base_url}[/cyan]")
    console.print(f"  Model:            [cyan]{config.model}[/cyan]")
    console.print(f"  Config File:      [cyan]{get_config_path()}[/cyan]")

def clean_error_message(e: Exception) -> str:
    err_msg = str(e)
    import re
    # Match single or double quoted message field, allowing newlines and escaped quotes
    match = re.search(r"['\"]message['\"]\s*:\s*['\"]((?:[^'\"]|\\['\"])+)['\"]", err_msg, re.DOTALL)
    if match:
        return match.group(1).replace("\\n", "\n").strip()
    if hasattr(e, "message") and e.message:
        # Check that e.message isn't just the whole structured trace itself
        if "Error code:" not in str(e.message):
            return str(e.message)
    return err_msg

@app.command("doctor")
def doctor():
    """
    Run environment and LLM diagnostic check.
    """
    console.print("[bold blue]Running System Diagnostics...[/bold blue]\n")
    
    # 1. Check Git
    try:
        import git
        git_ver = git.cmd.Git().version()
        console.print(f"  [green]+[/green] Git: Installed ({git_ver})")
    except Exception:
        console.print("  [red]-[/red] Git: Not found or gitpython package missing.")
        
    # 2. Check local tools
    try:
        import bandit
        console.print("  [green]+[/green] Bandit (Python SAST): Installed")
    except Exception:
        console.print("  [yellow]![/yellow] Bandit (Python SAST): Not found (will use regex fallbacks)")
        
    # 3. Check LLM Connectivity
    config = load_config()
    console.print(f"  [*] Attempting to invoke LLM provider '{config.provider}' using model '{config.model}'...")
    try:
        from backend.app.agents.base import get_llm
        llm = get_llm()
        llm.invoke("ping", config={"timeout": 3.0})
        console.print(f"  [green]+[/green] LLM Connection & Quota: Success (Model '{config.model}' is ready and responsive)")
    except Exception as e:
        console.print(f"  [red]-[/red] LLM Connection Failed: {clean_error_message(e)}")

def print_interactive_help():
    console.print("\n[bold cyan]Interactive Console Commands[/bold cyan]:")
    console.print("  [bold green]/review [path][/bold green] : Scan a local codebase folder")
    console.print("  [bold green]/dashboard[/bold green]     : Open the UI dashboard in the web browser")
    console.print("  [bold green]/config[/bold green]        : Configure LLM models and local API keys")
    console.print("  [bold green]/providers[/bold green]     : Show current active LLM provider")
    console.print("  [bold green]/doctor[/bold green]        : Audit local tools and LLM connectivity")
    console.print("  [bold green]/clear[/bold green]         : Clear screen")
    console.print("  [bold green]/exit[/bold green] or [bold green]/quit[/bold green] : Close interactive session")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Main interactive shell entry point for secure-review CLI when run without args.
    """
    if ctx.invoked_subcommand is not None:
        return
        
    # Ensure backend server runs automatically as soon as secure-review starts
    ensure_backend_server()
        
    console.print(Panel(
        "[bold cyan]AI Secure Review Interactive Console[/bold cyan]\n"
        "Multi-agent codebase security & code quality auditor.\n\n"
        "Type [bold green]/help[/bold green] to see available commands.\n"
        "Type [bold red]/exit[/bold red] to quit.",
        title="AI Secure Review",
        expand=False
    ))
    
    while True:
        try:
            # Custom styled shell prompt
            cmd_line = console.input("[bold magenta]secure-review > [/bold magenta]").strip()
            if not cmd_line:
                continue
                
            import shlex
            try:
                tokens = shlex.split(cmd_line, posix=(os.name != 'nt'))
            except Exception:
                tokens = cmd_line.split()
                
            if not tokens:
                continue
                
            cmd = tokens[0].lower()
            args = tokens[1:]
            
            if cmd in ("/exit", "/quit", "exit", "quit", "q"):
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif cmd in ("/help", "help", "?"):
                print_interactive_help()
            elif cmd in ("/review", "review"):
                # Parse args inside interactive shell
                target_path = "."
                path_opt_val = None
                save_report = True
                
                # Check for --no-save
                if "--no-save" in args:
                    save_report = False
                    args = [a for a in args if a != "--no-save"]
                
                # Check for path options
                path_flag = None
                if "-p" in args:
                    path_flag = "-p"
                elif "--path" in args:
                    path_flag = "--path"
                    
                if path_flag:
                    idx = args.index(path_flag)
                    # Collect all following arguments until the next flag starting with '-'
                    path_parts = []
                    for a in args[idx + 1:]:
                        if a.startswith("-"):
                            break
                        path_parts.append(a)
                    if path_parts:
                        path_opt_val = " ".join(path_parts)
                else:
                    # Collect and join all positional arguments with spaces to reconstruct spaces
                    positionals = [a for a in args if not a.startswith("-")]
                    if positionals:
                        target_path = " ".join(positionals)
                    
                try:
                    review(path=target_path, path_opt=path_opt_val, save=save_report)
                except SystemExit:
                    pass
            elif cmd in ("/config", "config"):
                configure()
            elif cmd in ("/providers", "providers"):
                providers()
            elif cmd in ("/doctor", "doctor"):
                doctor()
            elif cmd in ("/dashboard", "dashboard"):
                import webbrowser
                url = "http://localhost:8000/"
                console.print(f"[bold blue]Opening dashboard at:[/bold blue] {url}")
                try:
                    webbrowser.open(url)
                except Exception as e:
                    console.print(f"[bold red]Failed to open web browser: {e}[/bold red]")
            elif cmd in ("/clear", "clear", "cls"):
                os.system('cls' if os.name == 'nt' else 'clear')
            else:
                console.print(f"[red]Unknown command: '{cmd}'. Type [bold]/help[/bold] to list commands.[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

if __name__ == "__main__":
    app()
