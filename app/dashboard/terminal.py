"""Terminal dashboard rendering for SysMonitor using Rich or ANSI fallback."""
import sys

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.progress_bar import ProgressBar
    from rich.table import Table
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def get_color_for_pct(pct: float) -> str:
    if pct >= 85.0:
        return "bold red"
    if pct >= 65.0:
        return "bold yellow"
    return "bold green"


class TerminalDashboard:
    def __init__(self):
        self.console = Console() if HAS_RICH else None

    def _render_ascii_bar(self, pct: float, length: int = 20) -> str:
        clamped = max(0.0, min(100.0, pct))
        filled = int((clamped / 100.0) * length)
        return "■" * filled + "·" * (length - filled)

    def generate_rich_layout(self, data: dict) -> "Layout":
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=7),
        )
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1),
        )

        host = data["host"]
        header_text = Text()
        header_text.append("SysMonitor Telemetry  ", style="bold white")
        header_text.append(f"Host: {host['os']} ({host['arch']})  ", style="dim")
        header_text.append(f"Cores: {data['cpu']['cores']}  ", style="dim")
        header_text.append(f"Uptime: {host['uptime']}", style="dim")
        layout["header"].update(Panel(header_text, style="dim"))

        left_table = Table.grid(padding=(0, 1))
        left_table.add_column("Metric", style="white", width=14)
        left_table.add_column("Bar", width=22)
        left_table.add_column("Details", style="dim")

        cpu = data["cpu"]
        c_pct = cpu["usage_percent"]
        c_col = get_color_for_pct(c_pct)
        left_table.add_row(
            "CPU",
            ProgressBar(total=100, completed=c_pct, width=20, complete_style=c_col),
            f"[{c_col}]{c_pct}%[/] ({cpu['model'][:28]})",
        )

        mem = data["memory"]
        m_pct = mem["usage_percent"]
        m_col = get_color_for_pct(m_pct)
        left_table.add_row(
            "RAM",
            ProgressBar(total=100, completed=m_pct, width=20, complete_style=m_col),
            f"[{m_col}]{mem['used_gb']}G / {mem['total_gb']}G ({m_pct}%)[/]",
        )

        s_pct = mem["swap_percent"]
        s_col = get_color_for_pct(s_pct)
        left_table.add_row(
            "Swap",
            ProgressBar(total=100, completed=s_pct, width=20, complete_style=s_col),
            f"[{s_col}]{mem['swap_used_gb']}G / {mem['swap_total_gb']}G[/]",
        )

        disk = data["disk"]
        d_pct = disk["usage_percent"]
        d_col = get_color_for_pct(d_pct)
        left_table.add_row(
            "Disk (/)",
            ProgressBar(total=100, completed=d_pct, width=20, complete_style=d_col),
            f"[{d_col}]{disk['used_gb']}G / {disk['total_gb']}G ({d_pct}%)[/]",
        )

        layout["left"].update(Panel(left_table, title="Resources", border_style="dim"))

        right_table = Table.grid(padding=(0, 1))
        right_table.add_column("Property", style="white", width=14)
        right_table.add_column("Value", style="dim")

        net = data["network"]
        right_table.add_row("Network In", f"{net['download_kbps']} KB/s (Total: {net['total_rx_mb']} MB)")
        right_table.add_row("Network Out", f"{net['upload_kbps']} KB/s (Total: {net['total_tx_mb']} MB)")
        right_table.add_row("Load Avg", f"{cpu['load_1m']} (1m)  {cpu['load_5m']} (5m)  {cpu['load_15m']} (15m)")

        gpu = data["gpu"]
        if gpu["available"]:
            g_col = get_color_for_pct(gpu["utilization_percent"])
            right_table.add_row("GPU", f"[{g_col}]{gpu['name']} ({gpu['temp_c']}°C, {gpu['utilization_percent']}%)[/]")
        else:
            right_table.add_row("GPU", "Integrated / No dedicated accelerator")

        alert_parts = []
        for a in data["alerts"]:
            if a["level"] == "CRITICAL":
                alert_parts.append(f"[bold red]CRITICAL: {a['msg']}[/]")
            elif a["level"] == "WARNING":
                alert_parts.append(f"[bold yellow]WARN: {a['msg']}[/]")
            else:
                alert_parts.append("[green]Normal[/]")
        right_table.add_row("Health", " | ".join(alert_parts))

        layout["right"].update(Panel(right_table, title="System Telemetry", border_style="dim"))

        proc_table = Table(box=None, expand=True)
        proc_table.add_column("PID", style="cyan", width=8)
        proc_table.add_column("Command", style="white", ratio=2)
        proc_table.add_column("State", style="dim", width=8)
        proc_table.add_column("RSS Memory", style="yellow", justify="right", width=14)

        for p in data["processes"]:
            proc_table.add_row(str(p["pid"]), p["name"], p["status"], f"{p['mem_mb']} MB")

        layout["footer"].update(Panel(proc_table, title="Active Processes (by Memory)", border_style="dim"))
        return layout

    def render_ansi_fallback(self, data: dict):
        sys.stdout.write("\033[H\033[J")
        host = data["host"]
        print("=" * 64)
        print(f"SysMonitor Telemetry | {host['os']} ({host['arch']}) | Cores: {data['cpu']['cores']} | Uptime: {host['uptime']}")
        print("=" * 64)

        cpu = data["cpu"]
        c_bar = self._render_ascii_bar(cpu["usage_percent"])
        print(f" CPU Usage   : [{c_bar}] {cpu['usage_percent']}% ({cpu['model'][:24]})")

        mem = data["memory"]
        m_bar = self._render_ascii_bar(mem["usage_percent"])
        print(f" Memory (RAM): [{m_bar}] {mem['usage_percent']}% ({mem['used_gb']}G / {mem['total_gb']}G)")

        disk = data["disk"]
        d_bar = self._render_ascii_bar(disk["usage_percent"])
        print(f" Disk Space  : [{d_bar}] {disk['usage_percent']}% ({disk['used_gb']}G / {disk['total_gb']}G)")

        net = data["network"]
        print(f" Network I/O : In {net['download_kbps']} KB/s | Out {net['upload_kbps']} KB/s")
        print("-" * 64)
        print(" System Alert: " + ", ".join([a["msg"] for a in data["alerts"]]))
        print("-" * 64)
        print(f" {'PID':<8} {'Command':<28} {'State':<8} {'Memory':>10}")
        for p in data["processes"]:
            print(f" {p['pid']:<8} {p['name']:<28} {p['status']:<8} {p['mem_mb']:>8} MB")
        print("=" * 64)
        print("Ctrl + C to terminate.")
        sys.stdout.flush()
