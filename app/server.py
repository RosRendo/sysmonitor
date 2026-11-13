"""
SysMonitor Local Telemetry Web Server
=====================================
Serves dashboard.html and streams real Linux kernel metrics via /api/metrics.
Zero external dependencies (uses Python standard library).
"""
import http.server
import json
import os
import platform
import sys
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.alerts.rules import AlertRuleEngine
from app.collectors.cpu import CPUCollector
from app.collectors.disk import DiskCollector
from app.collectors.gpu import GPUCollector
from app.collectors.memory import MemoryCollector
from app.collectors.network import NetworkCollector
from app.collectors.processes import ProcessCollector

cpu_col = CPUCollector()
mem_col = MemoryCollector()
disk_col = DiskCollector(mount_point="/")
net_col = NetworkCollector()
proc_col = ProcessCollector()
gpu_col = GPUCollector()
alert_engine = AlertRuleEngine()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_uptime_seconds() -> float:
    try:
        with open("/proc/uptime", "r") as f:
            return float(f.read().split()[0])
    except Exception:
        return 0.0


def collect_real_telemetry() -> dict:
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

    uptime_sec = get_uptime_seconds()
    days = int(uptime_sec // 86400)
    hours = int((uptime_sec % 86400) // 3600)
    uptime_str = f"{days}d {hours}h" if days > 0 else f"{hours}h {int((uptime_sec % 3600)//60)}m"

    return {
        "timestamp": time.time(),
        "timestamp_str": time.strftime("%H:%M:%S"),
        "host": {
            "os": platform.system(),
            "release": platform.release(),
            "arch": platform.machine(),
            "uptime": uptime_str,
            "uptime_seconds": int(uptime_sec),
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


class TelemetryHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/stress"):
            # Trigger real 3-second CPU burst in a daemon worker
            def stress_worker():
                t_end = time.time() + 3.0
                while time.time() < t_end:
                    _ = [x * x for x in range(80000)]
            for _ in range(2):
                threading.Thread(target=stress_worker, daemon=True).start()

            resp = json.dumps({"status": "active", "duration_seconds": 3}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp)
            return

        if self.path == "/api/metrics":
            data = collect_real_telemetry()
            payload = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path == "/" or self.path == "/index.html":
            self.path = "/dashboard.html"

        return super().do_GET()

    def log_message(self, format, *args):
        # Quiet logger to avoid terminal spam
        pass


def run_server(port: int = 8080):
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), TelemetryHandler)
    print("=" * 60)
    print(f"  SysMonitor Web Telemetry Server Running")
    print(f"  URL: http://localhost:{port}/")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)

