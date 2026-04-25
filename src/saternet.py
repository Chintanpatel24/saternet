"""
saternet - Python Environment Manager for Linux
A clean, professional CLI tool for managing Python virtual environments.
"""

import os
import sys
import json
import shutil
import signal
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# ──────────────────────────────────────────────
# VERSION & CONFIG
# ──────────────────────────────────────────────

VERSION = "1.0.0"
CONFIG_DIR = Path.home() / ".config" / "saternet"
CONFIG_FILE = CONFIG_DIR / "envs.json"
LOG_FILE = CONFIG_DIR / "saternet.log"

BANNER = r"""
────────────────────────────────────────────────────────────────────
███████╗ █████╗ ████████╗███████╗██████╗ ███╗   ██╗███████╗████████╗
██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝
███████╗███████║   ██║   █████╗  ██████╔╝██╔██╗ ██║█████╗     ██║   
╚════██║██╔══██║   ██║   ██╔══╝  ██╔══██╗██║╚██╗██║██╔══╝     ██║   
███████║██║  ██║   ██║   ███████╗██║  ██║██║ ╚████║███████╗   ██║   
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   
────────────────────────────────────────────────────────────────────

  python environment manager  v{version}
""".format(version=VERSION)


# ──────────────────────────────────────────────
# SIGNAL HANDLER
# ──────────────────────────────────────────────

def handle_exit(sig, frame):
    print("\nsaternet  exiting")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


# ──────────────────────────────────────────────
# CONFIG MANAGEMENT
# ──────────────────────────────────────────────

def ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps({"envs": [], "active": None}, indent=2))

def load_config():
    ensure_config()
    try:
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        return {"envs": [], "active": None}

def save_config(data):
    ensure_config()
    CONFIG_FILE.write_text(json.dumps(data, indent=2))

def log(message):
    ensure_config()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {message}\n")


# ──────────────────────────────────────────────
# ENVIRONMENT DETECTION
# ──────────────────────────────────────────────

def is_venv(path):
    p = Path(path)
    return (
        (p / "bin" / "python").exists() or
        (p / "bin" / "python3").exists()
    ) and (
        (p / "pyvenv.cfg").exists() or
        (p / "bin" / "activate").exists()
    )

def get_python_version(env_path):
    python_bin = Path(env_path) / "bin" / "python"
    if not python_bin.exists():
        python_bin = Path(env_path) / "bin" / "python3"
    if python_bin.exists():
        try:
            result = subprocess.run(
                [str(python_bin), "--version"],
                capture_output=True, text=True, timeout=3
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception:
            return "unknown"
    return "unknown"

def get_env_size(env_path):
    try:
        result = subprocess.run(
            ["du", "-sh", str(env_path)],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.split()[0]
    except Exception:
        pass
    return "?"

def get_active_env():
    return os.environ.get("VIRTUAL_ENV", None)

def scan_system_envs():
    """Scan common locations for virtual environments."""
    search_paths = [
        Path.home(),
        Path.home() / "envs",
        Path.home() / "venvs",
        Path.home() / ".virtualenvs",
        Path.home() / "projects",
        Path.home() / "dev",
        Path("/opt"),
    ]
    found = []
    seen = set()

    for base in search_paths:
        if not base.exists():
            continue
        # Check base itself
        if is_venv(base):
            rp = str(base.resolve())
            if rp not in seen:
                seen.add(rp)
                found.append(rp)
        # Check one level deep
        try:
            for child in base.iterdir():
                if child.is_dir() and not child.name.startswith('.'):
                    if is_venv(child):
                        rp = str(child.resolve())
                        if rp not in seen:
                            seen.add(rp)
                            found.append(rp)
        except PermissionError:
            continue

    return found

def merge_envs(config_envs, scanned_envs):
    """Merge tracked and auto-detected envs, dedup by path."""
    all_paths = set()
    result = []
    for e in config_envs:
        p = e.get("path", "")
        if p and p not in all_paths:
            all_paths.add(p)
            result.append(e)
    for p in scanned_envs:
        if p not in all_paths:
            all_paths.add(p)
            result.append({"path": p, "name": Path(p).name})
    return result


# ──────────────────────────────────────────────
# OUTPUT HELPERS
# ──────────────────────────────────────────────

def print_banner():
    print(BANNER)

def section(title):
    print(f"\n  {title.upper()}")
    print(f"  {'─' * len(title)}")

def info(label, value):
    print(f"    {label:<18} {value}")

def msg(text):
    print(f"  {text}")

def ok(text):
    print(f"  ok   {text}")

def err(text):
    print(f"  err  {text}", file=sys.stderr)

def warn(text):
    print(f"  warn {text}")


# ──────────────────────────────────────────────
# COMMANDS
# ──────────────────────────────────────────────

def cmd_list(args):
    """List all known and detected environments."""
    print_banner()

    config = load_config()
    scanned = scan_system_envs()
    envs = merge_envs(config.get("envs", []), scanned)
    active_path = get_active_env()

    if not envs:
        section("environments")
        msg("no environments found")
        msg("use  saternet create  to make a new one")
        return

    section(f"environments  ({len(envs)} found)")
    print()

    for i, env in enumerate(envs):
        path = env.get("path", "")
        name = env.get("name", Path(path).name if path else "unnamed")
        exists = Path(path).exists() if path else False

        is_active = (active_path and Path(active_path).resolve() == Path(path).resolve()) if path else False
        status = "active" if is_active else ("ok" if exists else "missing")

        py_ver = get_python_version(path) if exists else "n/a"
        size = get_env_size(path) if exists else "n/a"

        print(f"  [{i+1}]  {name}")
        info("path", path or "n/a")
        info("python", py_ver)
        info("size", size)
        info("status", status)
        print()

    if active_path:
        msg(f"currently active  {active_path}")


def cmd_activate(args):
    """Print activation instructions (shells must source, not exec)."""
    env_name = args.env_name
    config = load_config()
    scanned = scan_system_envs()
    envs = merge_envs(config.get("envs", []), scanned)

    match = None
    for env in envs:
        name = env.get("name", Path(env.get("path","")).name)
        if name == env_name or env.get("path","") == env_name:
            match = env
            break

    if not match:
        err(f"environment not found: {env_name}")
        msg("run  saternet list  to see available environments")
        sys.exit(1)

    path = match.get("path","")
    activate_script = Path(path) / "bin" / "activate"

    if not activate_script.exists():
        err(f"activate script missing at {activate_script}")
        sys.exit(1)

    print_banner()
    section("activate")
    print()
    msg(f"environment  {env_name}")
    info("path", path)
    print()
    msg("run this command to activate the environment in your shell:")
    print()
    print(f"    source {activate_script}")
    print()
    msg("or add this alias to your .bashrc / .zshrc for quick access:")
    print()
    print(f"    alias {env_name}='source {activate_script}'")
    print()

    # Write a helper script to /tmp that the user can source
    helper = Path(f"/tmp/saternet_activate_{env_name}.sh")
    helper.write_text(f"source {activate_script}\n")
    helper.chmod(0o755)
    msg(f"quick-source script written to  {helper}")
    msg("run:  source " + str(helper))

    log(f"activate requested: {env_name} at {path}")


def cmd_deactivate(args):
    """Deactivate the current environment."""
    print_banner()
    active = get_active_env()
    section("deactivate")
    print()
    if not active:
        msg("no environment is currently active")
        return

    msg(f"active environment  {active}")
    print()
    msg("to deactivate, run:")
    print()
    print("    deactivate")
    print()
    msg("this must be run directly in your shell (cannot be done by a subprocess)")

    helper = Path("/tmp/saternet_deactivate.sh")
    helper.write_text("deactivate\n")
    helper.chmod(0o755)
    log(f"deactivate requested for: {active}")


def cmd_create(args):
    """Create a new virtual environment."""
    print_banner()
    section("create environment")
    print()

    name = args.name
    if args.path:
        target_path = Path(args.path) / name
    else:
        print("  enter the directory where you want to create the environment")
        print(f"  leave blank to use  {Path.home() / 'envs' / name}")
        print()
        user_input = input("  path: ").strip()
        if user_input:
            target_path = Path(user_input) / name
        else:
            target_path = Path.home() / "envs" / name

    target_path = target_path.expanduser().resolve()

    if target_path.exists():
        err(f"path already exists: {target_path}")
        sys.exit(1)

    py_bin = args.python or "python3"
    which = shutil.which(py_bin)
    if not which:
        err(f"python interpreter not found: {py_bin}")
        sys.exit(1)

    msg(f"name        {name}")
    info("location", str(target_path))
    info("python", py_bin)
    print()
    msg("creating environment ...")

    try:
        result = subprocess.run(
            [py_bin, "-m", "venv", str(target_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            err("failed to create environment")
            if result.stderr:
                print(f"\n  {result.stderr.strip()}")
            sys.exit(1)
    except FileNotFoundError:
        err(f"python not found: {py_bin}")
        sys.exit(1)

    # Register in config
    config = load_config()
    envs = config.get("envs", [])
    envs.append({"name": name, "path": str(target_path)})
    config["envs"] = envs
    save_config(config)

    ok(f"environment created at  {target_path}")
    print()
    msg("to activate:")
    print(f"    source {target_path}/bin/activate")
    log(f"created environment: {name} at {target_path}")


def cmd_remove(args):
    """Remove a registered environment (optionally delete files)."""
    print_banner()
    env_name = args.env_name
    config = load_config()
    envs = config.get("envs", [])

    match = None
    for env in envs:
        name = env.get("name", Path(env.get("path","")).name)
        if name == env_name or env.get("path","") == env_name:
            match = env
            break

    if not match:
        err(f"environment not found in registry: {env_name}")
        msg("only tracked environments can be removed")
        sys.exit(1)

    path = match.get("path","")
    section("remove environment")
    print()
    msg(f"name    {env_name}")
    info("path", path)
    print()

    if args.delete:
        if Path(path).exists():
            confirm = input("  this will permanently delete the environment files. confirm [yes/no]: ").strip().lower()
            if confirm != "yes":
                msg("aborted")
                return
            shutil.rmtree(path)
            ok(f"deleted files at  {path}")
        else:
            warn(f"path does not exist, skipping file deletion")

    config["envs"] = [e for e in envs if e != match]
    save_config(config)
    ok(f"removed {env_name} from registry")
    log(f"removed environment: {env_name} at {path} (delete={args.delete})")


def cmd_info(args):
    """Show detailed info about a specific environment."""
    print_banner()
    env_name = args.env_name
    config = load_config()
    scanned = scan_system_envs()
    envs = merge_envs(config.get("envs", []), scanned)
    active_path = get_active_env()

    match = None
    for env in envs:
        name = env.get("name", Path(env.get("path","")).name)
        if name == env_name or env.get("path","") == env_name:
            match = env
            break

    if not match:
        err(f"environment not found: {env_name}")
        sys.exit(1)

    path = match.get("path","")
    p = Path(path)
    exists = p.exists()
    is_active = (active_path and Path(active_path).resolve() == p.resolve()) if path else False

    section(f"info  {env_name}")
    print()
    info("name", env_name)
    info("path", path)
    info("exists", "yes" if exists else "no")
    info("status", "active" if is_active else "inactive")

    if exists:
        info("python", get_python_version(path))
        info("size", get_env_size(path))

        pycfg = p / "pyvenv.cfg"
        if pycfg.exists():
            print()
            msg("pyvenv.cfg")
            for line in pycfg.read_text().splitlines():
                if line.strip():
                    print(f"    {line.strip()}")

        pip_bin = p / "bin" / "pip"
        if pip_bin.exists():
            print()
            msg("installed packages")
            try:
                result = subprocess.run(
                    [str(pip_bin), "list", "--format=columns"],
                    capture_output=True, text=True, timeout=10
                )
                lines = result.stdout.strip().splitlines()
                # Skip header lines
                for line in lines[2:]:
                    print(f"    {line}")
            except Exception:
                msg("could not retrieve package list")


def cmd_scan(args):
    """Rescan and update the environment registry."""
    print_banner()
    section("scanning system")
    print()
    msg("searching for virtual environments ...")
    found = scan_system_envs()
    config = load_config()
    old_envs = config.get("envs", [])
    merged = merge_envs(old_envs, found)
    config["envs"] = merged
    save_config(config)
    ok(f"scan complete  {len(found)} environments found  {len(merged)} total in registry")
    log(f"scan complete: {len(found)} found, {len(merged)} in registry")


def cmd_version(args):
    print(f"saternet {VERSION}")


def cmd_log(args):
    """Show the saternet log file."""
    print_banner()
    section("log")
    print()
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text().splitlines()
        if not lines:
            msg("log is empty")
        else:
            for line in lines[-50:]:
                print(f"  {line}")
    else:
        msg("no log file found")


def cmd_help(args=None):
    print_banner()
    print("  usage:  saternet <command> [options]")
    print()
    print("  commands:")
    print()
    print("    list                       list all environments with paths and status")
    print("    activate <name>            show how to activate an environment")
    print("    deactivate                 show how to deactivate the current environment")
    print("    create <name>              create a new virtual environment")
    print("    remove <name>              remove environment from registry")
    print("    info <name>                show detailed info and packages for an environment")
    print("    scan                       scan system for new environments")
    print("    log                        show saternet activity log")
    print("    version                    print version")
    print("    help                       show this help")
    print()
    print("  create options:")
    print()
    print("    --path <dir>               directory to create the environment in")
    print("    --python <interpreter>     python interpreter to use  (default: python3)")
    print()
    print("  remove options:")
    print()
    print("    --delete                   also delete environment files from disk")
    print()
    print("  examples:")
    print()
    print("    saternet list")
    print("    saternet create myenv")
    print("    saternet create myenv --path ~/projects --python python3.11")
    print("    saternet activate myenv")
    print("    saternet deactivate")
    print("    saternet info myenv")
    print("    saternet remove myenv")
    print("    saternet remove myenv --delete")
    print("    saternet scan")
    print()
    print("  note:")
    print()
    print("    activation must be done by sourcing the script in your shell.")
    print("    saternet activate will print the exact command to run.")
    print()
    print("  config:  ~/.config/saternet/")
    print("  log:     ~/.config/saternet/saternet.log")
    print()


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    if len(sys.argv) == 1:
        cmd_list(None)
        return

    parser = argparse.ArgumentParser(
        prog="saternet",
        description="saternet - python environment manager",
        add_help=False
    )
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="list all environments")

    # activate
    p_act = subparsers.add_parser("activate", help="activate an environment")
    p_act.add_argument("env_name", help="environment name")

    # deactivate
    subparsers.add_parser("deactivate", help="deactivate current environment")

    # create
    p_create = subparsers.add_parser("create", help="create new environment")
    p_create.add_argument("name", help="environment name")
    p_create.add_argument("--path", help="parent directory for the environment")
    p_create.add_argument("--python", help="python interpreter (default: python3)")

    # remove
    p_remove = subparsers.add_parser("remove", help="remove an environment")
    p_remove.add_argument("env_name", help="environment name")
    p_remove.add_argument("--delete", action="store_true", help="delete files from disk")

    # info
    p_info = subparsers.add_parser("info", help="show environment info")
    p_info.add_argument("env_name", help="environment name")

    # scan
    subparsers.add_parser("scan", help="scan system for environments")

    # log
    subparsers.add_parser("log", help="show activity log")

    # version
    subparsers.add_parser("version", help="print version")

    # help
    subparsers.add_parser("help", help="show help")

    args = parser.parse_args()

    dispatch = {
        "list": cmd_list,
        "activate": cmd_activate,
        "deactivate": cmd_deactivate,
        "create": cmd_create,
        "remove": cmd_remove,
        "info": cmd_info,
        "scan": cmd_scan,
        "log": cmd_log,
        "version": cmd_version,
        "help": cmd_help,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        cmd_help()


if __name__ == "__main__":
    main()
