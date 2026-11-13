"""
SysMonitor - Alert Rules Engine
===============================
Evaluates resource thresholds and flags warnings or critical states.
"""

class AlertRuleEngine:
    def __init__(
        self,
        cpu_warn: float = 80.0,
        cpu_crit: float = 90.0,
        mem_warn: float = 80.0,
        mem_crit: float = 92.0,
        disk_warn: float = 85.0,
        disk_crit: float = 95.0,
    ):
        self.cpu_warn = cpu_warn
        self.cpu_crit = cpu_crit
        self.mem_warn = mem_warn
        self.mem_crit = mem_crit
        self.disk_warn = disk_warn
        self.disk_crit = disk_crit

    def evaluate(self, cpu_pct: float, mem_pct: float, disk_pct: float) -> list[dict]:
        """
        Evaluates metrics against alert thresholds.
        Returns a list of alert badges: [{"level": "CRITICAL"|"WARNING"|"OK", "message": "..."}]
        """
        alerts = []

        # CPU Alert
        if cpu_pct >= self.cpu_crit:
            alerts.append({"level": "CRITICAL", "source": "CPU", "msg": f"High CPU: {cpu_pct}%"})
        elif cpu_pct >= self.cpu_warn:
            alerts.append({"level": "WARNING", "source": "CPU", "msg": f"Elevated CPU: {cpu_pct}%"})

        # Memory Alert
        if mem_pct >= self.mem_crit:
            alerts.append({"level": "CRITICAL", "source": "RAM", "msg": f"Critical RAM: {mem_pct}%"})
        elif mem_pct >= self.mem_warn:
            alerts.append({"level": "WARNING", "source": "RAM", "msg": f"High RAM: {mem_pct}%"})

        # Disk Alert
        if disk_pct >= self.disk_crit:
            alerts.append({"level": "CRITICAL", "source": "DISK", "msg": f"Disk Near Full: {disk_pct}%"})
        elif disk_pct >= self.disk_warn:
            alerts.append({"level": "WARNING", "source": "DISK", "msg": f"Low Disk Space: {disk_pct}%"})

        if not alerts:
            alerts.append({"level": "OK", "source": "SYSTEM", "msg": "All resources within normal operational thresholds."})

        return alerts

