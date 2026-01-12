# OmniRun Examples

This directory contains example projects demonstrating OmniRun's capabilities across different languages and frameworks.

## Examples Overview

### 1. Flask App (`flask_app/`)
A simple Python Flask web application.

**Files:**
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies

**Try it:**
```bash
cd examples/flask_app
python ../../omni_run.py
# Select option 1 to run the Flask app
```

### 2. Node.js App (`node_app/`)
An Express.js web server.

**Files:**
- `server.js` - Express server implementation
- `package.json` - Node.js dependencies and scripts

**Try it:**
```bash
cd examples/node_app
python ../../omni_run.py
# OmniRun will detect missing dependencies and offer to install them
```

### 3. Go App (`go_app/`)
A basic Go HTTP server.

**Files:**
- `main.go` - Go HTTP server
- `go.mod` - Go module definition

**Try it:**
```bash
cd examples/go_app
python ../../omni_run.py
# Select option 1 to run the Go server
```

## Usage Examples

### Basic Discovery
```bash
# Scan current directory
python omni_run.py

# Scan specific directory
python omni_run.py /path/to/project

# Generate HTML report
python omni_run.py examples/flask_app --html flask_report.html
```

### Auto-Fix Dependencies
```bash
# Interactive auto-fix
python omni_run.py examples/node_app --auto-fix

# Dry-run mode (see what would happen)
python omni_run.py examples/node_app --dry-run
```

### Advanced Execution Modes
```bash
# Run with arguments
python omni_run.py examples/flask_app --args --port 8080 --debug

# Watch mode (auto-restart on changes)
python omni_run.py examples/flask_app --watch

# Profile mode (performance analysis)
python omni_run.py examples/flask_app --profile
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

## Configuration Examples

### Project-Specific Config
Create a `.omnirun.yaml` in your project:

```yaml
auto_fix: true
enable_backup: true
max_depth: 5
exclude_dirs:
  - node_modules
  - __pycache__
  - .git
```

### Global Config
Create `~/.omnirun.yaml`:

```yaml
auto_fix: false
confirm_each_command: true
enable_docker: true
preferred_commands:
  python: "python -m pytest"
  node: "npm test"
```

## Framework Detection

OmniRun automatically detects:

- **Python**: Django (`manage.py`), Flask (`app.py`), FastAPI (`main.py`)
- **JavaScript**: React (`package.json` with react), Next.js (`next` in deps)
- **Go**: Gin/Echo (`main.go` with framework imports)
- **And many more...**

## Container Examples

### Docker Setup
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
```

OmniRun will detect these files and suggest appropriate commands.

## Safety Features Demo

### Backup & Rollback
```bash
# OmniRun creates backups before making changes
python omni_run.py examples/node_app --auto-fix

# If something goes wrong, it can rollback automatically
```

### Confirmation Prompts
```bash
# Enable confirmation for each command
echo "confirm_each_command: true" > ~/.omnirun.yaml
python omni_run.py examples/node_app --auto-fix
```

## Report Generation

### HTML Report
```bash
python omni_run.py examples --html examples_report.html
# Open examples_report.html in your browser
```

### JSON Report (for CI/CD)
```bash
python omni_run.py examples --json examples_report.json
# Parse with jq or your CI system
```

## Real-World Usage

### Development Workflow
1. **Discover**: `python omni_run.py` to see all runnable programs
2. **Fix**: `f 1` to auto-fix dependencies for the first program
3. **Run**: `1` to execute the program
4. **Watch**: `w 1` for development with auto-restart

### CI/CD Integration
```yaml
# .github/workflows/omnirun.yml
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
      - run: python omni_run.py --json report.json
      - run: |
          # Parse report and check for issues
          python -c "
          import json
          with open('report.json') as f:
              report = json.load(f)
          issues = [p for p in report['programs'] if any(d['required'] and not d['available'] for d in p['dependencies'])]
          if issues:
              print(f'Found {len(issues)} programs with issues')
              exit(1)
          "
```

## Troubleshooting

### Common Issues

**"No programs found"**
- Check if files have proper extensions
- Ensure executables are in scanned directories
- Try increasing `--max-depth`

**"Command not found"**
- Install missing interpreters (python, node, go, etc.)
- Check PATH environment variable

**"Permission denied"**
- Make scripts executable: `chmod +x script.py`
- Check file permissions

**"Dependencies not auto-fixed"**
- Some dependencies require manual installation
- Check error messages for specific requirements

### Debug Mode
```bash
python omni_run.py --verbose --max-depth 10
```

## Next Steps

- Explore the main OmniRun features
- Try creating your own example projects
- Check the [README.md](../README.md) for complete documentation
- Contribute new language/framework support!</content>
<parameter name="filePath">/home/master/Desktop/temp3/examples/README.md