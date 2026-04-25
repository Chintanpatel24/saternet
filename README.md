<div align=center> <pre>
────────────────────────────────────────────────────────────────────
███████╗ █████╗ ████████╗███████╗██████╗ ███╗   ██╗███████╗████████╗
██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝
███████╗███████║   ██║   █████╗  ██████╔╝██╔██╗ ██║█████╗     ██║   
╚════██║██╔══██║   ██║   ██╔══╝  ██╔══██╗██║╚██╗██║██╔══╝     ██║   
███████║██║  ██║   ██║   ███████╗██║  ██║██║ ╚████║███████╗   ██║   
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   
────────────────────────────────────────────────────────────────────
</pre></div>

- Python virtual environment manager for Linux.

- A clean, professional CLI tool for managing Python virtual environments
across any Linux distribution. No tables, no pipes, no noise.


## features

- list all environments with path, python version, size, and active status
- create new environments anywhere on the filesystem
- show activation and deactivation instructions for any shell
- detailed environment inspection including installed packages
- auto-scan the system for existing virtual environments
- activity log
- app menu shortcut for quick terminal launch
- works on Debian, Ubuntu, Arch, Fedora, openSUSE, and any systemd-based distro


## install

### quick install (recommended)

```bash
git clone https://github.com/Chintanpatel24/saternet.git
cd saternet
bash install.sh
```

For system-wide install:

```bash
sudo bash install.sh
```

### debian / ubuntu (.deb)

```bash
make deb
sudo dpkg -i dist/saternet_1.0.0.deb
```

Or install the dependency manually if needed:

```bash
sudo apt install python3
sudo dpkg -i dist/saternet_1.0.0.deb
```

### arch linux (AUR / manual)

```bash
cd packaging
makepkg -si
```

Or use an AUR helper:

```bash
yay -S saternet
paru -S saternet
```

### fedora / rhel / opensuse

```bash
bash install.sh
```

Installs to `~/.local/bin/saternet` when run without sudo.


## usage

```
saternet                           list all environments
saternet list                      list all environments
saternet activate <name>           show how to activate an environment
saternet deactivate                show how to deactivate
saternet create <name>             create a new environment (interactive)
saternet create <name> --path /dir create at specific path
saternet create <name> --python python3.11
saternet remove <name>             remove from registry
saternet remove <name> --delete    remove from registry and delete files
saternet info <name>               detailed info and installed packages
saternet scan                      scan system for new environments
saternet log                       show activity log
saternet version                   print version
saternet help                      show all commands
```


## note on activation

Shell environments cannot be changed by a subprocess. saternet will print
the exact `source` command to run in your terminal. You can also add an alias:

```bash
alias myenv='source ~/envs/myenv/bin/activate'
```


## update

```bash
cd saternet
bash update.sh
```

The updater fetches the latest changes from the repository and reinstalls.


## uninstall

```bash
cd saternet
bash uninstall.sh
```

Or with sudo for a system install:

```bash
sudo bash uninstall.sh
```


## config

saternet stores its registry and logs at:

```
~/.config/saternet/envs.json
~/.config/saternet/saternet.log
```


## requirements

- python 3.8 or higher
- bash
- any Linux distribution


## license

MIT
