"""
SysMonitor - GPU Metric Collector
=================================
Probes for NVIDIA/AMD GPUs using system commands.
"""
import subprocess
import shutil

class GPUCollector:
    def __init__(self):
        self.has_nvidia = shutil.which("nvidia-smi") is not None

    def get_stats(self) -> dict:
        """
        Queries nvidia-smi for VRAM and temperature if an NVIDIA GPU is present.
        """
        if self.has_nvidia:
            try:
                cmd = [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used,temperature.gpu,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ]
                output = subprocess.check_output(cmd, encoding="utf-8", timeout=1).strip()
                if output:
                    parts = [p.strip() for p in output.split(",")]
                    return {
                        "available": True,
                        "name": parts[0],
                        "total_vram_mb": int(parts[1]),
                        "used_vram_mb": int(parts[2]),
                        "temp_c": int(parts[3]),
                        "utilization_percent": int(parts[4]),
                    }
            except Exception:
                pass

        return {
            "available": False,
            "name": "No Dedicated GPU / Integrated",
            "total_vram_mb": 0,
            "used_vram_mb": 0,
            "temp_c": 0,
            "utilization_percent": 0,
        }

