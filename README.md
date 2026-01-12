# OmniRun v3.0

🚀 **Ultimate Multi-Platform Executable Discovery and Management System**

[![PyPI version](https://badge.fury.io/py/omni-run.svg)](https://pypi.org/project/omni-run/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/Throthgare/omni-run/blob/main/LICENSE)

OmniRun is an intelligent tool that automatically discovers, analyzes, and executes programs across multiple programming languages and frameworks. It features auto-dependency fixing, environment detection, and advanced execution modes.

## ✨ Features

### 🔍 Smart Discovery
- **Multi-language support**: Python, JavaScript, TypeScript, Go, Rust, Java, C#, Ruby, PHP, Swift, Kotlin, Scala, R, Julia, Perl, Lua, Haskell, Elixir, Clojure, Dart
- **Framework detection**: Django, Flask, FastAPI, React, Next.js, Vue.js, Angular, Gin, Echo, Actix, Rocket, Rails, Laravel, Spring Boot, Quarkus, Micronaut, and more
- **Entrypoint ranking**: Intelligent scoring system to identify main executable files
- **Environment awareness**: Detects venv, conda, Docker, and docker-compose setups

### 🔧 Auto-Fix & Safety
- **Dependency auto-fixing**: Automatically installs missing dependencies with beautiful command preview
- **Dry-run mode**: Preview changes without execution (`--dry-run`)
- **Backup & rollback**: Automatic git stash or file backup with rollback on failure
- **Confirmation prompts**: Optional per-command confirmation with `--yes`/`--no-confirm` flags
- **Safe defaults**: Prefer user-scoped installations and isolated environments

### 🚀 One-Click Execution
- **Run with arguments**: Pass command-line arguments to programs
- **Watch mode**: Auto-restart on file changes (requires watchdog) (`--watch`)
- **Profile mode**: Performance profiling with cProfile (`--profile`)
- **Preferred commands**: Store and recall frequently used commands per project

### 🎯 Advanced Task Runner Support
- **Multiple task runners**: Makefile, Justfile, npm scripts, Cargo tasks, Gradle, Maven
- **Task descriptions**: Parse comments from Makefiles and Justfiles
- **Framework commands**: Auto-detect dev, build, test, and production commands
- **Best command selection**: Automatically choose development vs production commands

### 📊 Rich Reporting & UX
- **Beautiful HTML reports**: Interactive reports with Tailwind CSS, copy-to-clipboard, and collapsible sections
- **JSON reports**: Machine-readable output for CI/CD integration
- **Real-time progress**: Live execution feedback with emojis and status indicators
- **Interactive mode**: Enhanced CLI with command history and smart suggestions
- **Rich TUI mode**: Beautiful terminal interface with `--tui` flag

### 🐳 Container & Environment Support
- **Docker detection**: Offers `docker build` and `docker run` commands
- **Docker Compose**: Suggests `docker-compose up` as primary command
- **Virtual environments**: Detects and suggests venv, conda, and pipenv
- **Multi-environment**: Support for complex project setups

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install omni-run
```

### From Source
```bash
git clone https://github.com/Throthgare/omni-run.git
cd omni-run
pip install -e .
```

### Standalone Binaries (Coming Soon)
Download from [releases page](https://github.com/yourusername/smart-launcher/releases)

## 🚀 Quick Start

### Basic Usage
```bash
# Interactive mode
python smart_launcher.py

# Direct execution with auto-fix
python smart_launcher.py --auto-fix

# Generate beautiful HTML report
python smart_launcher.py --html report.html

# CI/CD mode (no prompts)
python smart_launcher.py --yes --auto-fix --json results.json
```

### Advanced Execution Modes
```bash
# Run with arguments
python smart_launcher.py --args --port 8080 --debug

# Watch mode (auto-restart on changes)
python smart_launcher.py --watch

# Profile mode (performance analysis)
python smart_launcher.py --profile

# Dry run (see what would happen)
python smart_launcher.py --dry-run
```

### Interactive Mode Commands
```
Available Commands:
  [number]              - Execute program
  [number] -- arg1 arg2 - Execute with arguments
  w [num]               - Execute in watch mode
  p [num]               - Execute with profiling
  d [num]               - Show detailed info
  f [num]               - Auto-fix dependencies
  t [num]               - Show task runners
  html [file]           - Generate HTML report
  json [file]           - Generate JSON report
  r                     - Generate text report
  s                     - Rescan directory
  q                     - Quit
```

## ⚙️ Configuration

### Project-Specific Config (.smartlauncher.yaml)
```yaml
auto_fix: true
enable_backup: true
auto_rollback: true
confirm_each_command: false
enable_docker: true
enable_venv: true
max_depth: 5
timeout: 300
preferred_commands:
  "Python:app.py": "python app.py --dev"
  "JavaScript:server.js": "npm start"
```

### Global Config (~/.smartlauncher.yaml)
```yaml
auto_fix: false
confirm_each_command: true
enable_backup: true
preferred_commands: {}
```

## 🔧 Supported Languages & Frameworks

### Python
- **Frameworks**: Django, Flask, FastAPI, Pyramid
- **Tools**: pip, pipenv, poetry, conda
- **Commands**: Auto-detects manage.py, app.py, main.py

### JavaScript/TypeScript
- **Frameworks**: React, Next.js, Express, NestJS, Vue.js, Angular, Svelte, Nuxt.js
- **Tools**: npm, yarn, pnpm
- **Commands**: dev, build, start, test scripts

### Go
- **Frameworks**: Gin, Echo, Fiber
- **Tools**: go mod
- **Commands**: go run, go build, go test

### Rust
- **Frameworks**: Actix, Rocket, Warp
- **Tools**: cargo
- **Commands**: cargo run, cargo build, cargo test

### Java
- **Frameworks**: Spring Boot, Quarkus, Micronaut
- **Tools**: Maven, Gradle
- **Commands**: mvn spring-boot:run, gradle bootRun

### Ruby
- **Frameworks**: Ruby on Rails, Sinatra
- **Tools**: bundler
- **Commands**: rails server, rails console

### PHP
- **Frameworks**: Laravel, Symfony
- **Tools**: composer
- **Commands**: php artisan serve

### And 10+ more languages...

## 🐳 Container Support

OmniRun detects containerized setups:

### Dockerfile Projects
```bash
# Detected commands:
docker build -t myapp .
docker run myapp
```

### Docker Compose Projects
```bash
# Primary command:
docker-compose up
```

## 🔒 Safety Features

### Auto-Fix with Confirmation
```bash
$ python omni_run.py
🔧 DEPENDENCY AUTO-FIX PROPOSAL
============================================================
Program: server.js
Location: examples/node_app/server.js
Framework: Express.js
Missing Dependencies: 1
============================================================

📋 PROPOSED COMMANDS:
  1. node_modules - 🔧 Auto-fixable
     Command: cd /path/to/project && npm install
     Info: Dependencies NOT installed

Execute these 1 commands? [y/N]: y

✅ Auto-confirmed (--yes flag)
📦 Backup created
⚡ EXECUTING AUTO-FIX...
[1/1] Running: cd /path/to/project && npm install
  ✅ Fixed: node_modules
============================================================
🎉 ALL DEPENDENCIES FIXED SUCCESSFULLY!
============================================================
```

### Backup & Rollback
- **Git projects**: Creates stash before changes
- **File backup**: Copies dependency files to temp directory
- **Auto-rollback**: Restores state on failure

## 🎬 Demo

### Auto-Fix Workflow Demo
Watch Smart Launcher in action:

1. **Discovery**: Scans project and identifies programs with missing dependencies
2. **Safety Preview**: Shows beautiful command preview with backup/rollback options
3. **Auto-Fix**: Installs dependencies with progress indicators and error handling
4. **Verification**: Confirms all dependencies are resolved
5. **Execution**: Runs the program with watch mode for development

**Demo Video**: [Watch on YouTube](https://youtube.com/watch?v=demo-link) | **Demo GIF**: [View GIF](demo.gif)

### Key Demo Highlights
- ⚡ **Lightning Fast**: Discovers and analyzes projects in seconds
- 🔒 **Safe by Default**: Backup creation and rollback on failure
- 🎨 **Beautiful UI**: Rich terminal output with emojis and progress bars
- 🚀 **One-Click Fix**: Auto-resolves common dependency issues
- 📊 **Rich Reports**: Generates interactive HTML reports with Tailwind CSS

## 🚀 Real-World Usage

### Development Workflow
1. **Discover**: `python omni_run.py` scans and shows all programs
2. **Fix**: `f 1` auto-fixes dependencies with beautiful preview
3. **Run**: `1` executes the program
4. **Watch**: `w 1` for development with auto-restart
5. **Report**: `html report.html` generates beautiful documentation

### CI/CD Integration
```yaml
# .github/workflows/omni-run.yml
name: OmniRun Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python omni_run.py --yes --auto-fix --json results.json
      - run: |
          # Parse results and fail if issues found
          python -c "
          import json
          with open('results.json') as f:
              report = json.load(f)
          issues = [p for p in report['programs'] if any(d['required'] and not d['available'] for d in p['dependencies'])]
          if issues:
              print(f'❌ Found {len(issues)} programs with dependency issues')
              exit(1)
          print('✅ All dependencies resolved')
          "
```

## 🎯 Roadmap

### ✅ Completed (v3.0)
- Enhanced auto-fix with safety features
- 20+ framework detection
- Beautiful HTML reports with Tailwind CSS
- Watch and profile modes
- Preferred command storage
- Container awareness

### 🔄 In Progress
- PyPI packaging
- Standalone binaries (PyInstaller)
- VS Code extension
- GitHub Action

### 🚀 Future (v4.0)
- AI-powered codebase summaries
- Dependency graph visualization
- Security scanning integration
- Version pinning warnings
- Rich TUI interface

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

### Adding New Frameworks
```python
# In detect_framework method
elif 'your-framework' in deps:
    return Framework(
        name='Your Framework',
        version=deps.get('your-framework'),
        commands={
            'dev': 'your dev command',
            'build': 'your build command',
            'start': 'your start command'
        }
    )
```

## 🎯 Ready-to-Use Commands

After installation, OmniRun provides these commands:

```bash
# Install from PyPI
pip install omni-run

# Use the tool
omni-run --help                    # Show help
omni-run --list-commands          # List all available programs
omni-run --tui                    # Launch beautiful TUI interface
omni-run --html report.html       # Generate HTML report
omni-run --json report.json       # Generate JSON report
omni-run --ask-each               # Ask before each auto-fix
omni-run --yes                    # Auto-confirm all prompts
omni-run                         # Interactive mode
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with Python's amazing ecosystem and inspired by tools like `yarn`, `cargo`, and `pipenv`. Special thanks to the open-source community for the frameworks and tools that make development amazing.

---

**Making development faster, safer, and more enjoyable** ✨</content>
<parameter name="filePath">README.md