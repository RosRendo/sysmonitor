# SysMonitor 🐧📊

**SysMonitor** is an enterprise-grade, modular Linux telemetry cockpit and system monitoring tool built from scratch in Python, Bash, and Linux system internals (`/proc`).

It features both a rich **Terminal UI** (powered by Python Rich) and a high-performance **Living Telemetry Web Cockpit** (inspired by macOS Stats & Grafana, streaming real-time kernel metrics at 60 FPS).

---

## Architecture Overview

```
sysmonitor/
├── app/
│   ├── __init__.py
│   ├── main.py              # CLI terminal telemetry orchestrator
│   ├── server.py            # Zero-dependency local HTTP telemetry server (/api/metrics)
│   ├── collectors/          # Pure Linux metric extractors (/proc parsers)
│   │   ├── __init__.py
│   │   ├── cpu.py           # /proc/stat, /proc/loadavg, CFS scheduler
│   │   ├── memory.py        # /proc/meminfo, swap, buffers, page cache
│   │   ├── disk.py          # /proc/diskstats, statvfs, I/O rates
│   │   ├── network.py       # /proc/net/dev, rx/tx bandwidth
│   │   ├── processes.py     # /proc/[pid]/*, memory RSS, thread states
│   │   └── gpu.py           # Hardware accelerator & thermal sensors
│   ├── dashboard/           # Visual presentation layer (Terminal)
│   │   ├── __init__.py
│   │   └── terminal.py      # Rich terminal dashboard
│   └── alerts/              # Rule engine and threshold monitoring
│       ├── __init__.py
│       └── rules.py
├── dashboard.html           # Living 60-FPS Web Cockpit (macOS & Grafana inspired)
├── scripts/                 # Bash automation, cron tasks, systemd units
├── tests/                   # Pytest suite with mock /proc fixtures
├── requirements.txt         # Minimal production dependencies
└── README.md
```

---

## Features

- **Direct Kernel Ingestion**: Reads directly from Linux `/proc/stat`, `/proc/meminfo`, `/proc/diskstats`, `/proc/net/dev`, and `/proc/[pid]/status`.
- **Living 60-FPS Web Cockpit**:
  - Radial gradient dials for CPU, RAM, Disk, Thermal, Network, and GPU.
  - Multi-colored segmented memory composition bar (`App`, `Wired`, `Cached`, `Free`).
  - Full-size multi-series Line Chart with live magnetic crosshairs and Grafana summary table (`Min`, `Max`, `Avg`, `Current`).
  - Storage partitions vertical bar chart with capacity threshold styling.
  - Real active tasks inspector from `/proc`.
- **Terminal Cockpit**: High-contrast, responsive terminal monitoring using Python Rich.
- **Zero Heavy Dependencies**: Uses Python standard library for the telemetry backend server.

---

## Quickstart

### 1. Web Telemetry Cockpit
Start the local server in your Linux environment:
```bash
python3 app/server.py
```
Open your browser at `http://localhost:8080/` to view the live cockpit.

### 2. Terminal UI
Run the interactive terminal dashboard:
```bash
python3 app/main.py
```

---

## License
MIT License


