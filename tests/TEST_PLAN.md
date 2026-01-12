# OmniRun Test Suite - Comprehensive Test Plan

## Test Files

| File | Description | Test Count |
|------|-------------|------------|
| `test_discovery.py` | Core discovery tests (file scanning, language/framework detection) | 30+ |
| `test_frameworks.py` | Framework detection and handling | 25+ |
| `test_environments.py` | Environment and task runner detection | 20+ |
| `test_dependencies.py` | Dependency analysis and resolution | 25+ |
| `test_execution.py` | Program execution, watch mode, profile mode | 20+ |
| `test_reports.py` | HTML, JSON, text report generation | 15+ |
| `test_autofix.py` | Auto-fix functionality (the killer feature) | 30+ |
| `test_cli_config.py` | CLI arguments, configuration, logging | 25+ |
| `conftest.py` | Test fixtures and configuration | - |

## Test Categories

1. **Core Discovery Tests** (`test_discovery.py`)
   - File scanning and detection
   - Language identification
   - Framework detection
   - Environment detection
   - Task runner detection

2. **Framework Detection Tests** (`test_frameworks.py`)
   - Python frameworks (Flask, Django, FastAPI)
   - JavaScript frameworks (Express.js, React, Next.js)
   - Go frameworks (Gin, Echo)
   - Rust frameworks (Actix, Rocket)
   - Java frameworks (Spring, Maven, Gradle)

3. **Environment Detection Tests** (`test_environments.py`)
   - Virtual environment detection
   - Docker detection
   - Task runner detection (npm scripts, make, etc.)

4. **Dependency Analysis Tests** (`test_dependencies.py`)
   - Interpreter availability checks
   - Config file parsing
   - Dependency resolution
   - Auto-fix capability detection

5. **Execution Tests** (`test_execution.py`)
   - Program execution (synchronous)
   - Watch mode (file watching)
   - Profile mode (profiling)
   - Execution with arguments

6. **Report Generation Tests** (`test_reports.py`)
   - HTML report generation
   - JSON report generation
   - Text report generation

7. **Auto-Fix Tests** (`test_autofix.py`) - **Killer Feature**
   - Auto-fix proposal generation
   - Auto-fix execution
   - Dry-run mode
   - Backup creation and rollback
   - Safety features
   - Package manager detection (npm, yarn, pnpm, pip, cargo, maven, gradle)
   - Confirmation prompts

8. **CLI and Configuration Tests** (`test_cli_config.py`)
   - Command-line argument parsing
   - Configuration file loading (YAML, JSON)
   - Configuration options
   - Color output handling
   - Logging functionality
   - Executable patterns

9. **Language-Specific Tests**
   - Python programs
   - JavaScript/TypeScript programs
   - Go programs
   - Rust programs
   - Java programs
   - Ruby programs
   - PHP programs
   - And more...

10. **Edge Case Tests**
    - Empty directories
    - Permission errors
    - Invalid configurations
    - Missing dependencies

### Test Fixtures

The test suite uses the following fixtures:

- **Python Projects**: Simple scripts, Flask apps, Django apps, FastAPI apps
- **JavaScript Projects**: Node.js scripts, React apps, Next.js apps
- **Go Projects**: Simple Go programs, Gin/Echo frameworks
- **Rust Projects**: Cargo projects, Actix/Rocket frameworks
- **Multi-language Projects**: Projects with multiple languages

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/core/
pytest tests/execution/
pytest tests/reports/

# Run with coverage
pytest --cov=omni_run --cov-report=html

# Run specific test
pytest tests/test_discovery.py::test_scan_python_files
```

### Expected Coverage

- Core functionality: 100%
- Dependency analysis: 95%+
- Execution paths: 90%+
- Report generation: 100%
- Error handling: 95%+
- Overall: 90%+

