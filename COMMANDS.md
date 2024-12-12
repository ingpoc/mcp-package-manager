# Package Manager Commands

## UV Package Commands

### Add Packages
```json
Tool: "add"
Input: {
    "path": "project-path",
    "args": ["-r", "requirements.txt"]  // or ["package-name"]
}
```

### Install Package
```json
Tool: "install"
Input: {
    "package": "package-name or -r requirements.txt",
    "manager": "uv",
    "path": "project-path"
}
```

### Uninstall Package
```json
Tool: "uninstall"
Input: {
    "package": "package-name",
    "manager": "uv",
    "path": "project-path"
}
```

### Initialize Project
```json
Tool: "init"
Input: {
    "manager": "uv",
    "path": "project-path"
}
```

### Create Virtual Environment
```json
Tool: "create_venv"
Input: {
    "path": "project-path",
    "venv_name": ".venv"  // optional
}
```

## Notes
- Use `add` specifically for `uv add` commands
- All paths must be within project directory
- Packages are verified against whitelist if configured