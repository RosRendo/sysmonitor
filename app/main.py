"""Main process orchestrator and telemetry loop for SysMonitor."""
import os
import platform
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.alerts.rules import AlertRuleEngine
from app.collectors.cpu import CPUCollector
from app.collectors.disk import DiskCollector
from app.collectors.gpu import GPUCollector
from app.collectors.memory import MemoryCollector
from app.collectors.network import NetworkCollector
from app.collectors.processes import ProcessCollector
from app.dashboard.terminal import HAS_RICH, TerminalDashboard

if HAS_RICH:
    from rich.live import Live


def get_uptime_str() -> str:
    try:
        with open("/proc/uptime", "r") as f:
            total_seconds = float(f.read().split()[0])
            hours, rem = divmod(int(total_seconds), 3600)
            mins, secs = divmod(rem, 60)
            return f"{hours}h {mins}m {secs}s"
    except (FileNotFoundError, PermissionError, ValueError):
        return "n/a"


def main():
    cpu_col = CPUCollector()
    mem_col = MemoryCollector()
    disk_col = DiskCollector(mount_point="/")
    net_col = NetworkCollector()
    proc_col = ProcessCollector()
    gpu_col = GPUCollector()
    alert_engine = AlertRuleEngine()
    dashboard = TerminalDashboard()

    time.sleep(0.2)

    def fetch_all_data() -> dict:
        cpu_data = cpu_col.get_info()
        mem_data = mem_col.get_stats()
        disk_data = disk_col.get_stats()
        net_data = net_col.get_bandwidth()
        proc_data = proc_col.get_summary_and_top(limit=5)
        gpu_data = gpu_col.get_stats()

        alerts = alert_engine.evaluate(
            cpu_pct=cpu_data["usage_percent"],
            mem_pct=mem_data["usage_percent"],
            disk_pct=disk_data["usage_percent"],
        )

        return {
            "host": {
                "os": platform.system(),
                "release": platform.release(),
                "arch": platform.machine(),
                "uptime": get_uptime_str(),
            },
            "cpu": cpu_data,
            "memory": mem_data,
            "disk": disk_data,
            "network": net_data,
            "processes": proc_data["top"],
            "process_summary": {
                "total": proc_data["total"],
                "running": proc_data["running"],
                "sleeping": proc_data["sleeping"],
                "zombie": proc_data["zombie"],
            },
            "gpu": gpu_data,
            "alerts": alerts,
        }

    try:
        if HAS_RICH:
            with Live(dashboard.generate_rich_layout(fetch_all_data()), refresh_per_second=2, screen=True) as live:
                while True:
                    time.sleep(1.0)
                    live.update(dashboard.generate_rich_layout(fetch_all_data()))
        else:
            while True:
                dashboard.render_ansi_fallback(fetch_all_data())
                time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nSysMonitor terminated.")
        sys.exit(0)


if __name__ == "__main__":
    main()
