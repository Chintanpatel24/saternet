<div align=center> 
<img alt="saternet" src="https://github.com/user-attachments/assets/4332cd49-a3e0-410d-b534-ee41b86cb67f"  width="250" />
</div>

# Saternet 
>- Python virtual environment manager for Linux.
>- A clean, professional CLI tool for managing Python virtual environments
across any Linux distribution. No tables, no pipes, no noise.

---

## Features

- list all environments with path, python version, size, and active status
- create new environments anywhere on the filesystem
- show activation and deactivation instructions for any shell
- detailed environment inspection including installed packages
- auto-scan the system for existing virtual environments
- activity log
- app menu shortcut for quick terminal launch
- works on Debian, Ubuntu, Arch, Fedora, openSUSE, and any systemd-based distro

---

## Install

### quick install (recommended)

```bash
git clone https://github.com/Chintanpatel24/saternet.git
cd saternet
bash install.sh
saternet help
saternet
```
---

## Usage

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

---

>##  Foot(Terminal) screenshots !!

<details>       
  <summary>Tap to view ⤥ </summary>
       

<img width="694" height="583" alt="foot" src="https://github.com/user-attachments/assets/0880d91b-1c39-4b70-bb6a-ea8bac1f3f3c" />
<img width="628" height="130" alt="scan" src="https://github.com/user-attachments/assets/47997d00-5308-4667-95b5-f343b401add2" />
<img width="968" height="670" alt="h1" src="https://github.com/user-attachments/assets/aa6cf0aa-5bd7-4833-9597-5d2d5f355267" />
<img width="590" height="594" alt="info" src="https://github.com/user-attachments/assets/c501fd3a-1119-4fcc-9f85-c57fa556621d" />
<img width="735" height="527" alt="h2" src="https://github.com/user-attachments/assets/355b77a7-8b6d-4115-902b-9fdab1d4d78e" />


</details>   

## Note on activation

Shell environments cannot be changed by a subprocess. saternet will print
the exact `source` command to run in your terminal. You can also add an alias:

```bash
alias myenv='source ~/envs/myenv/bin/activate'
```

---

## Update

```bash
cd saternet
bash update.sh
```
The updater fetches the latest changes from the repository and reinstalls.

---

## Config

saternet stores its registry and logs at:

```
~/.config/saternet/envs.json
~/.config/saternet/saternet.log
```


## Requirements

- python 3.8 or higher
- bash
- any Linux distribution


## License

MIT
