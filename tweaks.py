"""
Advanced PC Tweaks engine for the Undetected application.
Contains all tweak definitions, categories, and execution logic.
Each tweak stores both 'apply' and 'revert' registry/command payloads.
"""
import ctypes
import json
import os
import subprocess

TWEAKS_STATE_FILE = os.path.join(os.path.expanduser("~"), ".undetected_tweaks_state.json")


def _is_admin() -> bool:
    """Check if running with administrator privileges (Windows)."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except (AttributeError, OSError):
        return os.geteuid() == 0 if hasattr(os, "geteuid") else False


def _run_reg(path: str, name: str, reg_type: str, value: str) -> tuple[bool, str]:
    """Apply a Windows registry tweak."""
    cmd = f'reg add "{path}" /v "{name}" /t {reg_type} /d {value} /f'
    return _run_cmd(cmd)


def _run_cmd(cmd: str) -> tuple[bool, str]:
    """Execute a shell command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip() or f"Exit code: {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def _run_powershell(script: str) -> tuple[bool, str]:
    """Execute a PowerShell script."""
    cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{script}"'
    return _run_cmd(cmd)


def load_tweaks_state() -> dict:
    """Load the state of applied tweaks from disk."""
    if os.path.exists(TWEAKS_STATE_FILE):
        try:
            with open(TWEAKS_STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_tweaks_state(state: dict):
    """Save the current tweak state to disk."""
    try:
        with open(TWEAKS_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except IOError:
        pass


# ---------------------------------------------------------------------------
# Tweak definitions — each is a dict with metadata + apply/revert commands
# ---------------------------------------------------------------------------

TWEAK_CATEGORIES = {
    "performance": {
        "icon": "⚡",
        "label": "Performance",
        "description": "CPU, RAM & disk optimizations",
    },
    "network": {
        "icon": "🌐",
        "label": "Network",
        "description": "TCP/IP & DNS tuning",
    },
    "gaming": {
        "icon": "🎮",
        "label": "Gaming",
        "description": "FPS & input-lag tweaks",
    },
    "privacy": {
        "icon": "🔒",
        "label": "Privacy",
        "description": "Telemetry & tracking control",
    },
    "power": {
        "icon": "🔋",
        "label": "Power",
        "description": "Power plan & throttling",
    },
    "cleanup": {
        "icon": "🧹",
        "label": "Cleanup",
        "description": "Temp files & bloatware removal",
    },
    "visuals": {
        "icon": "🎨",
        "label": "Visuals",
        "description": "Animations & UI effects",
    },
    "memory": {
        "icon": "💾",
        "label": "Memory",
        "description": "RAM & pagefile optimization",
    },
}

ALL_TWEAKS: list[dict] = [
    # ── Performance ──────────────────────────────────────────────
    {
        "id": "perf_svc_split",
        "category": "performance",
        "name": "Split Svchost Services",
        "description": "Force each svchost.exe to host a single service for better resource management.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control" /v SvcHostSplitThresholdInKB /t REG_DWORD /d 0x4000000 /f',
                "revert": 'reg delete "HKLM\\SYSTEM\\CurrentControlSet\\Control" /v SvcHostSplitThresholdInKB /f',
            }
        ],
    },
    {
        "id": "perf_disable_prefetch",
        "category": "performance",
        "name": "Disable Prefetch & Superfetch",
        "description": "Disable Prefetch/Superfetch to reduce disk I/O on SSDs.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v EnablePrefetcher /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v EnablePrefetcher /t REG_DWORD /d 3 /f',
            },
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v EnableSuperfetch /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" /v EnableSuperfetch /t REG_DWORD /d 3 /f',
            },
        ],
    },
    {
        "id": "perf_disable_hpet",
        "category": "performance",
        "name": "Disable HPET Timer",
        "description": "Disable High Precision Event Timer for lower DPC latency.",
        "risk": "medium",
        "commands": [
            {
                "apply": "bcdedit /deletevalue useplatformclock",
                "revert": "bcdedit /set useplatformclock true",
            },
            {
                "apply": "bcdedit /set disabledynamictick yes",
                "revert": "bcdedit /set disabledynamictick no",
            },
        ],
    },
    {
        "id": "perf_proc_scheduling",
        "category": "performance",
        "name": "Optimize Process Scheduling",
        "description": "Prioritize foreground applications and short quantum for responsiveness.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 0x26 /f',
                "revert": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 0x02 /f',
            }
        ],
    },
    {
        "id": "perf_disable_last_access",
        "category": "performance",
        "name": "Disable Last Access Timestamp",
        "description": "Disable NTFS last-access time updates for faster file operations.",
        "risk": "low",
        "commands": [
            {
                "apply": "fsutil behavior set disablelastaccess 1",
                "revert": "fsutil behavior set disablelastaccess 0",
            }
        ],
    },
    {
        "id": "perf_large_system_cache",
        "category": "performance",
        "name": "Enable Large System Cache",
        "description": "Allocate more RAM for system cache, improving file I/O performance.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v LargeSystemCache /t REG_DWORD /d 1 /f',
                "revert": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v LargeSystemCache /t REG_DWORD /d 0 /f',
            }
        ],
    },
    # ── Network ──────────────────────────────────────────────────
    {
        "id": "net_tcp_tweaks",
        "category": "network",
        "name": "Optimize TCP Stack",
        "description": "Enable TCP auto-tuning, disable Nagle algorithm, and optimize congestion control.",
        "risk": "low",
        "commands": [
            {
                "apply": "netsh int tcp set global autotuninglevel=normal",
                "revert": "netsh int tcp set global autotuninglevel=default",
            },
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpNoDelay /t REG_DWORD /d 1 /f',
                "revert": 'reg delete "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpNoDelay /f',
            },
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpAckFrequency /t REG_DWORD /d 1 /f',
                "revert": 'reg delete "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpAckFrequency /f',
            },
        ],
    },
    {
        "id": "net_dns_cloudflare",
        "category": "network",
        "name": "Set DNS to Cloudflare (1.1.1.1)",
        "description": "Switch DNS to Cloudflare for faster and more private resolution.",
        "risk": "low",
        "commands": [
            {
                "apply": 'powershell -NoProfile -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses (\'1.1.1.1\',\'1.0.0.1\') }"',
                "revert": 'powershell -NoProfile -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses }"',
            }
        ],
    },
    {
        "id": "net_dns_google",
        "category": "network",
        "name": "Set DNS to Google (8.8.8.8)",
        "description": "Switch DNS to Google Public DNS for reliable resolution.",
        "risk": "low",
        "commands": [
            {
                "apply": 'powershell -NoProfile -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses (\'8.8.8.8\',\'8.8.4.4\') }"',
                "revert": 'powershell -NoProfile -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses }"',
            }
        ],
    },
    {
        "id": "net_disable_throttle",
        "category": "network",
        "name": "Disable Network Throttling",
        "description": "Remove Windows network throttling index for maximum throughput.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 0xFFFFFFFF /f',
                "revert": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 0x0A /f',
            }
        ],
    },
    {
        "id": "net_disable_wifi_sense",
        "category": "network",
        "name": "Disable Wi-Fi Sense",
        "description": "Prevent Windows from auto-sharing Wi-Fi credentials with contacts.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Microsoft\\WcmSvc\\wifinetworkmanager\\config" /v AutoConnectAllowedOEM /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKLM\\SOFTWARE\\Microsoft\\WcmSvc\\wifinetworkmanager\\config" /v AutoConnectAllowedOEM /t REG_DWORD /d 1 /f',
            }
        ],
    },
    # ── Gaming ───────────────────────────────────────────────────
    {
        "id": "game_mode_enable",
        "category": "gaming",
        "name": "Enable Game Mode & Game Bar",
        "description": "Enable Windows Game Mode for optimized gaming resource allocation.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f',
                "revert": 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 0 /f',
            },
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f',
                "revert": 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 0 /f',
            },
        ],
    },
    {
        "id": "game_gpu_scheduling",
        "category": "gaming",
        "name": "Enable Hardware GPU Scheduling",
        "description": "Let the GPU handle its own scheduling for reduced input latency.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f',
                "revert": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 1 /f',
            }
        ],
    },
    {
        "id": "game_disable_fullscreen_opt",
        "category": "gaming",
        "name": "Disable Fullscreen Optimizations",
        "description": "Disable FSO globally to reduce input lag in fullscreen games.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\System\\GameConfigStore" /v GameDVR_FSEBehaviorMode /t REG_DWORD /d 2 /f',
                "revert": 'reg delete "HKCU\\System\\GameConfigStore" /v GameDVR_FSEBehaviorMode /f',
            },
            {
                "apply": 'reg add "HKCU\\System\\GameConfigStore" /v GameDVR_HonorUserFSEBehaviorMode /t REG_DWORD /d 1 /f',
                "revert": 'reg delete "HKCU\\System\\GameConfigStore" /v GameDVR_HonorUserFSEBehaviorMode /f',
            },
        ],
    },
    {
        "id": "game_disable_game_dvr",
        "category": "gaming",
        "name": "Disable Game DVR / Background Recording",
        "description": "Stop background recording to free up GPU and CPU resources.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 1 /f',
            },
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f',
                "revert": 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" /v AllowGameDVR /f',
            },
        ],
    },
    {
        "id": "game_high_perf_gpu",
        "category": "gaming",
        "name": "Force High-Performance GPU for All Apps",
        "description": "Set the global GPU preference to high performance.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\DirectX\\UserGpuPreferences" /v DirectXUserGlobalSettings /t REG_SZ /d "GpuPreference=2;" /f',
                "revert": 'reg delete "HKCU\\Software\\Microsoft\\DirectX\\UserGpuPreferences" /v DirectXUserGlobalSettings /f',
            }
        ],
    },
    {
        "id": "game_multimedia_priority",
        "category": "gaming",
        "name": "Multimedia / Gaming Priority",
        "description": "Set multimedia scheduling to prioritize games over background tasks.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v Priority /t REG_DWORD /d 6 /f',
                "revert": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v Priority /t REG_DWORD /d 2 /f',
            },
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "Scheduling Category" /t REG_SZ /d High /f',
                "revert": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "Scheduling Category" /t REG_SZ /d Medium /f',
            },
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "SFIO Priority" /t REG_SZ /d High /f',
                "revert": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v "SFIO Priority" /t REG_SZ /d Normal /f',
            },
        ],
    },
    # ── Privacy ──────────────────────────────────────────────────
    {
        "id": "priv_disable_telemetry",
        "category": "privacy",
        "name": "Disable Windows Telemetry",
        "description": "Set telemetry level to Security-only and disable diagnostic data.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 3 /f',
            },
            {
                "apply": "sc config DiagTrack start= disabled",
                "revert": "sc config DiagTrack start= auto",
            },
            {
                "apply": "sc stop DiagTrack",
                "revert": "sc start DiagTrack",
            },
        ],
    },
    {
        "id": "priv_disable_activity_history",
        "category": "privacy",
        "name": "Disable Activity History",
        "description": "Prevent Windows from collecting and uploading activity history.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v EnableActivityFeed /t REG_DWORD /d 0 /f',
                "revert": 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v EnableActivityFeed /f',
            },
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v PublishUserActivities /t REG_DWORD /d 0 /f',
                "revert": 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v PublishUserActivities /f',
            },
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v UploadUserActivities /t REG_DWORD /d 0 /f',
                "revert": 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v UploadUserActivities /f',
            },
        ],
    },
    {
        "id": "priv_disable_ad_id",
        "category": "privacy",
        "name": "Disable Advertising ID",
        "description": "Revoke the per-user advertising identifier used for ad tracking.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 1 /f',
            }
        ],
    },
    {
        "id": "priv_disable_location",
        "category": "privacy",
        "name": "Disable Location Tracking",
        "description": "Turn off system-wide location access for all apps.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v DisableLocation /t REG_DWORD /d 1 /f',
                "revert": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v DisableLocation /t REG_DWORD /d 0 /f',
            }
        ],
    },
    {
        "id": "priv_disable_cortana",
        "category": "privacy",
        "name": "Disable Cortana",
        "description": "Disable Cortana search assistant and its cloud queries.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 1 /f',
            }
        ],
    },
    {
        "id": "priv_disable_feedback",
        "category": "privacy",
        "name": "Disable Feedback Notifications",
        "description": "Stop Windows from asking for feedback and sending usage data.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\Siuf\\Rules" /v NumberOfSIUFInPeriod /t REG_DWORD /d 0 /f',
                "revert": 'reg delete "HKCU\\Software\\Microsoft\\Siuf\\Rules" /v NumberOfSIUFInPeriod /f',
            }
        ],
    },
    # ── Power ────────────────────────────────────────────────────
    {
        "id": "pwr_ultimate_plan",
        "category": "power",
        "name": "Activate Ultimate Performance Plan",
        "description": "Enable the hidden 'Ultimate Performance' power plan for maximum throughput.",
        "risk": "low",
        "commands": [
            {
                "apply": "powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61",
                "revert": 'powershell -NoProfile -Command "$plans = powercfg /list | Select-String \'Ultimate Performance\'; if($plans){ $guid = $plans -replace \'.*?(\\w{8}-\\w{4}-\\w{4}-\\w{4}-\\w{12}).*\',\'$1\'; powercfg /delete $guid }"',
            }
        ],
    },
    {
        "id": "pwr_disable_hibernate",
        "category": "power",
        "name": "Disable Hibernation",
        "description": "Turn off hibernation to reclaim disk space (hiberfil.sys).",
        "risk": "low",
        "commands": [
            {
                "apply": "powercfg /hibernate off",
                "revert": "powercfg /hibernate on",
            }
        ],
    },
    {
        "id": "pwr_disable_sleep_usb",
        "category": "power",
        "name": "Disable USB Selective Suspend",
        "description": "Prevent USB devices from being power-managed (fixes peripherals disconnecting).",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\USB" /v DisableSelectiveSuspend /t REG_DWORD /d 1 /f',
                "revert": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\USB" /v DisableSelectiveSuspend /t REG_DWORD /d 0 /f',
            }
        ],
    },
    {
        "id": "pwr_disable_fast_startup",
        "category": "power",
        "name": "Disable Fast Startup",
        "description": "Disable hybrid shutdown for cleaner boot and fewer driver issues.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 1 /f',
            }
        ],
    },
    # ── Cleanup ──────────────────────────────────────────────────
    {
        "id": "clean_temp_files",
        "category": "cleanup",
        "name": "Clean Temporary Files",
        "description": "Remove Windows temp, user temp, and prefetch files.",
        "risk": "low",
        "commands": [
            {
                "apply": 'powershell -NoProfile -Command "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path C:\\Windows\\Temp\\* -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path C:\\Windows\\Prefetch\\* -Recurse -Force -ErrorAction SilentlyContinue"',
                "revert": "echo Temp files cannot be restored",
            }
        ],
    },
    {
        "id": "clean_dns_cache",
        "category": "cleanup",
        "name": "Flush DNS Cache",
        "description": "Clear the DNS resolver cache to fix stale DNS entries.",
        "risk": "low",
        "commands": [
            {
                "apply": "ipconfig /flushdns",
                "revert": "echo DNS cache rebuilds automatically",
            }
        ],
    },
    {
        "id": "clean_windows_update",
        "category": "cleanup",
        "name": "Clean Windows Update Cache",
        "description": "Clear the Windows Update download cache to free disk space.",
        "risk": "medium",
        "commands": [
            {
                "apply": 'powershell -NoProfile -Command "Stop-Service wuauserv -Force -ErrorAction SilentlyContinue; Remove-Item C:\\Windows\\SoftwareDistribution\\Download\\* -Recurse -Force -ErrorAction SilentlyContinue; Start-Service wuauserv"',
                "revert": "echo Update cache will rebuild automatically",
            }
        ],
    },
    {
        "id": "clean_event_logs",
        "category": "cleanup",
        "name": "Clear Event Logs",
        "description": "Wipe all Windows Event logs.",
        "risk": "medium",
        "commands": [
            {
                "apply": 'powershell -NoProfile -Command "Get-WinEvent -ListLog * -ErrorAction SilentlyContinue | ForEach-Object { [System.Diagnostics.Eventing.Reader.EventLogSession]::GlobalSession.ClearLog($_.LogName) }"',
                "revert": "echo Event logs cannot be restored",
            }
        ],
    },
    # ── Visuals ──────────────────────────────────────────────────
    {
        "id": "vis_disable_animations",
        "category": "visuals",
        "name": "Disable UI Animations",
        "description": "Turn off all window animations for a snappier desktop experience.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f',
                "revert": 'reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 1 /f',
            },
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarAnimations /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarAnimations /t REG_DWORD /d 1 /f',
            },
        ],
    },
    {
        "id": "vis_disable_transparency",
        "category": "visuals",
        "name": "Disable Transparency Effects",
        "description": "Turn off Acrylic/transparency for reduced GPU overhead.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 1 /f',
            }
        ],
    },
    {
        "id": "vis_best_performance",
        "category": "visuals",
        "name": "Set Visual Effects to Best Performance",
        "description": "Disable all visual effects (shadows, smooth fonts, etc.) for maximum speed.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f',
                "revert": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 0 /f',
            }
        ],
    },
    {
        "id": "vis_dark_mode",
        "category": "visuals",
        "name": "Enable System Dark Mode",
        "description": "Switch Windows to dark theme for system and apps.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 1 /f',
            },
            {
                "apply": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f',
                "revert": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 1 /f',
            },
        ],
    },
    # ── Memory ───────────────────────────────────────────────────
    {
        "id": "mem_disable_pagefile_encrypt",
        "category": "memory",
        "name": "Disable Pagefile Encryption",
        "description": "Turn off pagefile encryption for faster virtual memory access.",
        "risk": "medium",
        "commands": [
            {
                "apply": "fsutil behavior set encryptpagingfile 0",
                "revert": "fsutil behavior set encryptpagingfile 1",
            }
        ],
    },
    {
        "id": "mem_ndus",
        "category": "memory",
        "name": "Disable Memory Compression",
        "description": "Turn off Windows memory compression to reduce CPU overhead.",
        "risk": "medium",
        "commands": [
            {
                "apply": 'powershell -NoProfile -Command "Disable-MMAgent -MemoryCompression"',
                "revert": 'powershell -NoProfile -Command "Enable-MMAgent -MemoryCompression"',
            }
        ],
    },
    {
        "id": "mem_svc_host_split",
        "category": "memory",
        "name": "Optimize Svchost Memory Usage",
        "description": "Configure svchost to group services efficiently by setting threshold.",
        "risk": "low",
        "commands": [
            {
                "apply": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control" /v SvcHostSplitThresholdInKB /t REG_DWORD /d 67108864 /f',
                "revert": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control" /v SvcHostSplitThresholdInKB /t REG_DWORD /d 380000 /f',
            }
        ],
    },
]


def apply_tweak(tweak: dict) -> tuple[bool, str]:
    """Apply a single tweak (run all its 'apply' commands)."""
    results = []
    all_ok = True
    for cmd_pair in tweak["commands"]:
        ok, msg = _run_cmd(cmd_pair["apply"])
        results.append(msg)
        if not ok:
            all_ok = False
    if all_ok:
        state = load_tweaks_state()
        state[tweak["id"]] = True
        save_tweaks_state(state)
    return all_ok, " | ".join(results)


def revert_tweak(tweak: dict) -> tuple[bool, str]:
    """Revert a single tweak (run all its 'revert' commands)."""
    results = []
    all_ok = True
    for cmd_pair in tweak["commands"]:
        ok, msg = _run_cmd(cmd_pair["revert"])
        results.append(msg)
        if not ok:
            all_ok = False
    if all_ok:
        state = load_tweaks_state()
        state.pop(tweak["id"], None)
        save_tweaks_state(state)
    return all_ok, " | ".join(results)


def get_tweaks_by_category(category: str) -> list[dict]:
    """Return all tweaks for a given category."""
    return [t for t in ALL_TWEAKS if t["category"] == category]


def get_tweak_by_id(tweak_id: str) -> dict | None:
    """Find a tweak by its unique ID."""
    for t in ALL_TWEAKS:
        if t["id"] == tweak_id:
            return t
    return None
