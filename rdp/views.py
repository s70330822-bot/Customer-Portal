from django.shortcuts import render
from django.db.models import Q
import subprocess
import re
from datetime import datetime
from django.utils.timezone import make_aware
from .models import RDPLog
import psutil
import getpass
import socket


# ========== RDP LOG LIST PAGE ==========

def read_windows_rdp_events():
    command = [
        r"C:\Windows\System32\wevtutil.exe",
        "qe", "Security",
        '/q:*[System[(EventID=4624 or EventID=4625 or EventID=4647 or EventID=4779)]]',
        "/c:50",
        "/f:text"
    ]
 

    try:
        output = subprocess.check_output(
            command,
            text=True,
            errors='ignore',
            shell=False
        )
    except Exception as e:
        print("⚠️ Unable to read event logs:", e)
        return

    entries = []
    current = {}

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("Event ID:"):
            if current:
                entries.append(current)
                current = {}
            current["event_id"] = re.findall(r"\d+", line)[0]

        elif "Account Name:" in line and "SYSTEM" not in line:
            current["username"] = line.split(":", 1)[1].strip()

        elif "Source Network Address:" in line:
            ip = line.split(":", 1)[1].strip()
            current["ip_address"] = ip if ip else "Local"

        elif "Time Created:" in line:
            raw_time = line.split(":", 1)[1].strip()
            try:
                dt = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                current["event_time"] = make_aware(dt)
            except:
                current["event_time"] = None

    if current:
        entries.append(current)

    # Save to DB
    for e in entries:
        RDPLog.objects.get_or_create(
            event_id=e.get("event_id"),
            username=e.get("username", ""),
            ip_address=e.get("ip_address", ""),
            event_time=e.get("event_time"),
        )

def rdp_list(request):
    read_windows_rdp_events()

    search = request.GET.get("search", "")
    event = request.GET.get("event", "")

    logs = RDPLog.objects.all()

    if search:
        logs = logs.filter(
            Q(username__icontains=search) |
            Q(ip_address__icontains=search)
        )

    if event:
        logs = logs.filter(event_id=event)

    return render(request, "rdp/list.html", {
        "logs": logs,
        "search": search,
        "event": event,
    })
# ========== PARSE OUTPUT OF 'query user' ==========
def parse_query_user_output(output):
    lines = output.strip().splitlines()
    if len(lines) <= 1:
        return []

    rows = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        username = parts[0].lstrip(">") if len(parts) > 0 else ""
        sessionname = parts[1] if len(parts) > 1 else ""
        session_id = parts[2] if len(parts) > 2 else ""
        state = parts[3] if len(parts) > 3 else ""
        idle_time = parts[4] if len(parts) > 4 else ""
        logon_time = " ".join(parts[5:]) if len(parts) > 5 else ""

        rows.append({
            "username": username,
            "sessionname": sessionname,
            "session_id": session_id,
            "state": state,
            "idle_time": idle_time,
            "logon_time": logon_time,
        })

    return rows


# ========== CURRENT ACTIVE USER VIEW ==========
def current_active_users(request):
    try:
        result = subprocess.run(
            ["query", "user"],
            capture_output=True,
            text=True,
            shell=False
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        # --- NEW FIX: Even if returncode = 1, check if valid table came ---
        if "USERNAME" in stdout and "SESSIONNAME" in stdout:
            users = parse_query_user_output(stdout)
            return render(request, "rdp/current_user.html", {
                "users": users,
                "debug": ""
            })

        # Otherwise, true failure
        debug = (
            "QUERY USER FAILED\n"
            f"RETURN CODE: {result.returncode}\n\n"
            f"STDOUT:\n{stdout}\n\n"
            f"STDERR:\n{stderr}"
        )
        return render(request, "rdp/current_user.html", {
            "users": [],
            "debug": debug
        })

    except Exception as e:
        return render(request, "rdp/current_user.html", {
            "users": [],
            "debug": f"EXCEPTION: {str(e)}"
        })

# ========== ACTIVITY STREAM FOR DASHBOARD ==========

def activity_stream():
    # Fetch recent 8 events
    recent_logs = RDPLog.objects.order_by('-event_time')[:8]

    event_labels = {
        4624: "logged in",
        4625: "login failed",
        4647: "logged out",
        4779: "session disconnected",
    }

    activities = []

    for log in recent_logs:
        activities.append({
            "username": log.username or "Unknown",
            "action": event_labels.get(int(log.event_id), "activity"),
            "time": log.event_time,
        })

    return activities

def dashboard(request):
    activities = activity_stream()

    return render(request, "dashboard/dashboard.html", {
        "activities": activities,
    })




# ========== SERVER STATUS (CPU, RAM, USER, PC NAME) ==========
def get_server_status():
    try:
        return {
            "pc_name": socket.gethostname(),
            "username": getpass.getuser(),
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "status": "Online"
        }
    except:
        return {
            "pc_name": "Unknown",
            "username": "Unknown",
            "cpu": 0,
            "memory": 0,
            "status": "Offline"
        }


# ========== CHECK IF SERVER IS ONLINE (RDP ACTIVE) ==========
def is_server_online():
    try:
        result = subprocess.run(
            ["query", "user"],
            capture_output=True,
            text=True,
            shell=False
        )

        stdout = result.stdout.strip()

        if "USERNAME" in stdout:
            return True
        return False

    except:
        return False


# ========== FINAL QUICK LOGIN VIEW ==========
def quick_login_view(request):
    server = get_server_status()

    online = is_server_online()
    server["status"] = "Online" if online else "Offline"

    context = {
        "server_data": server,
    }

    return render(request, "dashboard/dashboard.html", context)

