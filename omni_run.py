#!/usr/bin/env python3
"""
OmniRun v3.0 - Ultimate Multi-Platform Executable Discovery and Management System
Author: The Aetherial Team
Version: 3.0

New in v3.0:
- Auto-fix missing dependencies (THE KILLER FEATURE!)
- Environment isolation (venv, conda, docker)
- Task runner detection (Makefile, Justfile, package.json scripts)
- Framework detection (Django, Flask, React, Next.js, etc.)
- Advanced execution (args passing, watch mode, profiling)
- HTML/JSON reports
- Configuration file support
"""

import os
import sys
import platform
import subprocess
import json
import shutil
import time
import yaml
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
import re
import argparse
import hashlib

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def disable():
        """Disable colors for Windows or piped output."""
        for attr in dir(Colors):
            if not attr.startswith('_') and attr != 'disable':
                setattr(Colors, attr, '')

class ExecutionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"
    FIXED = "FIXED"

@dataclass
class DependencyCheck:
    """Represents a dependency check result."""
    name: str
    required: bool
    available: bool
    version: Optional[str] = None
    message: Optional[str] = None
    fix_command: Optional[str] = None
    can_auto_fix: bool = False

@dataclass
class Environment:
    """Represents a detected development environment."""
    type: str  # venv, conda, docker, system
    path: Optional[Path] = None
    active: bool = False
    python_version: Optional[str] = None
    activation_command: Optional[str] = None

@dataclass
class TaskRunner:
    """Represents a detected task runner."""
    type: str  # make, just, npm, cargo, gradle
    file: Path
    tasks: List[str] = field(default_factory=list)
    
@dataclass
class Framework:
    """Represents a detected framework."""
    name: str  # Django, Flask, React, Next.js, etc.
    version: Optional[str] = None
    entry_point: Optional[Path] = None
    commands: Dict[str, str] = field(default_factory=dict)

@dataclass
class ExecutableProgram:
    """Represents a discovered executable program."""
    path: Path
    name: str
    relative_path: str
    type: str
    interpreters: List[str]
    score: int
    dependencies: List[DependencyCheck]
    has_config: bool
    config_files: List[str]
    estimated_complexity: str
    environment: Optional[Environment] = None
    framework: Optional[Framework] = None
    task_runners: List[TaskRunner] = field(default_factory=list)
    
@dataclass
class ExecutionResult:
    """Represents the result of a program execution."""
    program: ExecutableProgram
    status: ExecutionStatus
    start_time: datetime
    end_time: datetime
    duration: float
    return_code: Optional[int]
    stdout: str
    stderr: str
    error_message: Optional[str]
    args: List[str] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)

class OmniRun:
    """Enhanced OmniRun with auto-fix and advanced features."""
    
    def __init__(self, base_path: str = ".", verbose: bool = False, config_file: Optional[str] = None):
        self.base_path = Path(base_path).resolve()
        self.system = platform.system()
        self.verbose = verbose
        self.discovered_programs: List[ExecutableProgram] = []
        self.execution_history: List[ExecutionResult] = []
        self.config = self._load_config(config_file)
        
        # Disable colors on Windows unless in a compatible terminal
        if self.system == 'Windows' and not os.environ.get('WT_SESSION'):
            Colors.disable()
        
        # Remember last-used command per project
        self.preferred_commands = self.config.get('preferred_commands', {})
        self.executable_patterns = {
            'Python': {
                'extensions': ['.py', '.pyw', '.pyc'],
                'interpreters': ['python3', 'python'],
                'config_files': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'poetry.lock', 'environment.yml'],
                'dependency_managers': ['pip', 'pipenv', 'poetry', 'conda'],
                'frameworks': ['Django', 'Flask', 'FastAPI', 'Pyramid']
            },
            'JavaScript': {
                'extensions': ['.js', '.mjs', '.cjs'],
                'interpreters': ['node'],
                'config_files': ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'],
                'dependency_managers': ['npm', 'yarn', 'pnpm'],
                'frameworks': ['React', 'Next.js', 'Express', 'NestJS', 'Vue', 'Angular']
            },
            'TypeScript': {
                'extensions': ['.ts', '.tsx'],
                'interpreters': ['ts-node', 'deno', 'bun'],
                'config_files': ['tsconfig.json', 'package.json'],
                'dependency_managers': ['npm', 'yarn', 'pnpm'],
                'frameworks': ['React', 'Next.js', 'NestJS', 'Angular']
            },
            'Go': {
                'extensions': ['.go'],
                'interpreters': ['go'],
                'config_files': ['go.mod', 'go.sum'],
                'dependency_managers': ['go'],
                'frameworks': ['Gin', 'Echo', 'Fiber']
            },
            'Rust': {
                'extensions': ['.rs'],
                'interpreters': ['cargo'],
                'config_files': ['Cargo.toml', 'Cargo.lock'],
                'dependency_managers': ['cargo'],
                'frameworks': ['Actix', 'Rocket', 'Warp']
            },
            'Java': {
                'extensions': ['.java'],
                'interpreters': ['java', 'javac'],
                'config_files': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
                'dependency_managers': ['maven', 'gradle'],
                'frameworks': ['Spring', 'Quarkus', 'Micronaut']
            },
            'C#': {
                'extensions': ['.cs'],
                'interpreters': ['dotnet'],
                'config_files': ['*.csproj', '*.sln'],
                'dependency_managers': ['nuget'],
                'frameworks': ['ASP.NET', '.NET MAUI', 'Blazor']
            },
            'Ruby': {
                'extensions': ['.rb'],
                'interpreters': ['ruby'],
                'config_files': ['Gemfile', 'Gemfile.lock'],
                'dependency_managers': ['bundler'],
                'frameworks': ['Rails', 'Sinatra', 'Hanami']
            },
            'PHP': {
                'extensions': ['.php'],
                'interpreters': ['php'],
                'config_files': ['composer.json', 'composer.lock'],
                'dependency_managers': ['composer'],
                'frameworks': ['Laravel', 'Symfony', 'CodeIgniter']
            },
            'Swift': {
                'extensions': ['.swift'],
                'interpreters': ['swift'],
                'config_files': ['Package.swift'],
                'dependency_managers': ['swiftpm'],
                'frameworks': ['Vapor', 'Perfect', 'Kitura']
            },
            'Kotlin': {
                'extensions': ['.kt', '.kts'],
                'interpreters': ['kotlin'],
                'config_files': ['build.gradle.kts', 'pom.xml'],
                'dependency_managers': ['gradle', 'maven'],
                'frameworks': ['Ktor', 'Spring Boot', 'Exposed']
            },
            'Scala': {
                'extensions': ['.scala'],
                'interpreters': ['scala'],
                'config_files': ['build.sbt', 'pom.xml'],
                'dependency_managers': ['sbt', 'maven'],
                'frameworks': ['Play', 'Akka', 'Lift']
            },
            'R': {
                'extensions': ['.r', '.R'],
                'interpreters': ['Rscript'],
                'config_files': ['DESCRIPTION', 'renv.lock'],
                'dependency_managers': ['renv'],
                'frameworks': ['Shiny', 'Plumber']
            },
            'Julia': {
                'extensions': ['.jl'],
                'interpreters': ['julia'],
                'config_files': ['Project.toml', 'Manifest.toml'],
                'dependency_managers': ['julia'],
                'frameworks': ['Genie', 'Dash']
            },
            'Perl': {
                'extensions': ['.pl', '.pm'],
                'interpreters': ['perl'],
                'config_files': ['cpanfile'],
                'dependency_managers': ['cpanm'],
                'frameworks': ['Mojolicious', 'Dancer']
            },
            'Lua': {
                'extensions': ['.lua'],
                'interpreters': ['lua'],
                'config_files': ['rockspec'],
                'dependency_managers': ['luarocks'],
                'frameworks': ['Lapis', 'OpenResty']
            },
            'Haskell': {
                'extensions': ['.hs'],
                'interpreters': ['ghc', 'runghc'],
                'config_files': ['package.yaml', 'stack.yaml'],
                'dependency_managers': ['stack', 'cabal'],
                'frameworks': ['Yesod', 'Servant', 'Scotty']
            },
            'Elixir': {
                'extensions': ['.ex', '.exs'],
                'interpreters': ['elixir'],
                'config_files': ['mix.exs'],
                'dependency_managers': ['mix'],
                'frameworks': ['Phoenix', 'Plug']
            },
            'Clojure': {
                'extensions': ['.clj', '.cljs'],
                'interpreters': ['clojure'],
                'config_files': ['project.clj', 'deps.edn'],
                'dependency_managers': ['lein', 'deps'],
                'frameworks': ['Ring', 'Compojure']
            },
            'Dart': {
                'extensions': ['.dart'],
                'interpreters': ['dart'],
                'config_files': ['pubspec.yaml'],
                'dependency_managers': ['pub'],
                'frameworks': ['Flutter', 'Aqueduct']
            },
            'Executable': {
                'extensions': [],
                'interpreters': [],
                'config_files': [],
                'dependency_managers': [],
                'frameworks': []
            }
        }
        
        self.main_file_patterns = [
            r'^main\.', r'^app\.', r'^index\.', r'^start\.', r'^run\.',
            r'^launcher\.', r'^entry\.', r'^__main__\.', r'^server\.', r'^cli\.',
            r'^manage\.', r'^wsgi\.', r'^asgi\.'
        ]
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            'auto_fix': False,
            'exclude_dirs': ['node_modules', '__pycache__', '.git', 'venv', 'env', 'build', 'dist'],
            'max_depth': 10,
            'timeout': 300,
            'enable_docker': True,
            'enable_venv': True,
            'enable_backup': True,
            'auto_rollback': True,
            'confirm_each_command': False,
            'preferred_commands': {},  # Store per-project preferred commands
            'watch_mode': False,
            'profile_mode': False,
            'rich_ui': False,
            'gui_mode': False,
            'ai_summary': False,
            'security_scan': False,
            'version_pinning': False
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                        user_config = yaml.safe_load(f)
                    else:
                        user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.log(f"Error loading config: {e}", "WARNING")
        
        # Also check for ~/.smartlauncher.yaml
        home_config = Path.home() / '.smartlauncher.yaml'
        if home_config.exists():
            try:
                with open(home_config, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except:
                pass
        
        return default_config
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp and level."""
        if self.verbose or level in ["ERROR", "WARNING", "SUCCESS"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            color = {
                "INFO": Colors.OKBLUE,
                "SUCCESS": Colors.OKGREEN,
                "WARNING": Colors.WARNING,
                "ERROR": Colors.FAIL,
                "FIX": Colors.OKCYAN
            }.get(level, "")
            print(f"{color}[{timestamp}] [{level}] {message}{Colors.ENDC}")
    
    def detect_environment(self, path: Path) -> Optional[Environment]:
        """Detect virtual environments, conda environments, or Docker with enhanced container support."""
        # Check for Python venv/virtualenv
        venv_paths = [
            path / 'venv', path / 'env', path / '.venv',
            path / 'virtualenv', path / '.env'
        ]
        
        for venv_path in venv_paths:
            if venv_path.exists():
                python_exe = venv_path / 'bin' / 'python' if self.system != 'Windows' else venv_path / 'Scripts' / 'python.exe'
                if python_exe.exists():
                    try:
                        result = subprocess.run(
                            [str(python_exe), '--version'],
                            capture_output=True, text=True, timeout=5
                        )
                        version = result.stdout.strip()
                        activation = f"source {venv_path}/bin/activate" if self.system != 'Windows' else f"{venv_path}\\Scripts\\activate"
                        
                        return Environment(
                            type='venv',
                            path=venv_path,
                            active=False,
                            python_version=version,
                            activation_command=activation
                        )
                    except:
                        pass
        
        # Check for conda environment
        conda_env = path / 'environment.yml'
        if conda_env.exists():
            return Environment(
                type='conda',
                path=path,
                active=False,
                activation_command=f"conda env create -f {conda_env}"
            )
        
        # Enhanced Docker detection
        dockerfile = path / 'Dockerfile'
        docker_compose = path / 'docker-compose.yml' or path / 'docker-compose.yaml'
        
        if docker_compose.exists():
            return Environment(
                type='docker-compose',
                path=docker_compose,
                active=False,
                activation_command=f"docker-compose up"
            )
        elif dockerfile.exists() and self.config.get('enable_docker', True):
            return Environment(
                type='docker',
                path=dockerfile,
                active=False,
                activation_command=f"docker build -t app {path} && docker run app"
            )
        
        return None
    
    def detect_task_runners(self, path: Path) -> List[TaskRunner]:
        """Detect task runners like Makefile, Justfile, etc."""
        runners = []
        
        # Makefile
        makefile = path / 'Makefile'
        if makefile.exists():
            tasks = self._parse_makefile(makefile)
            runners.append(TaskRunner(type='make', file=makefile, tasks=tasks))
        
        # Justfile
        justfile = path / 'justfile' or path / 'Justfile'
        if justfile.exists():
            tasks = self._parse_justfile(justfile)
            runners.append(TaskRunner(type='just', file=justfile, tasks=tasks))
        
        # package.json scripts
        package_json = path / 'package.json'
        if package_json.exists():
            tasks = self._parse_package_json_scripts(package_json)
            if tasks:
                runners.append(TaskRunner(type='npm', file=package_json, tasks=tasks))
        
        # Taskfile.yml
        taskfile = path / 'Taskfile.yml'
        if taskfile.exists():
            tasks = self._parse_taskfile(taskfile)
            runners.append(TaskRunner(type='task', file=taskfile, tasks=tasks))
        
        return runners
    
    def _parse_makefile(self, makefile: Path) -> List[str]:
        """Parse Makefile to extract targets with descriptions."""
        tasks = []
        try:
            with open(makefile, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    # Match targets (lines that start with word followed by :)
                    match = re.match(r'^([a-zA-Z0-9_-]+):', line)
                    if match and not match.group(1).startswith('.'):
                        task_name = match.group(1)
                        # Look for comment on the same line or next line
                        description = ""
                        if '#' in line:
                            description = line.split('#', 1)[1].strip()
                        elif i + 1 < len(lines) and lines[i + 1].strip().startswith('#'):
                            description = lines[i + 1].strip()[1:].strip()
                        
                        tasks.append(f"{task_name}: {description}" if description else task_name)
        except:
            pass
        return tasks
    
    def _parse_justfile(self, justfile: Path) -> List[str]:
        """Parse Justfile to extract recipes."""
        tasks = []
        try:
            with open(justfile, 'r') as f:
                for line in f:
                    # Match recipes (similar to Makefile)
                    match = re.match(r'^([a-zA-Z0-9_-]+):', line)
                    if match:
                        tasks.append(match.group(1))
        except:
            pass
        return tasks
    
    def _parse_package_json_scripts(self, package_json: Path) -> List[str]:
        """Parse package.json to extract npm scripts."""
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
                return list(data.get('scripts', {}).keys())
        except:
            return []
    
    def _parse_taskfile(self, taskfile: Path) -> List[str]:
        """Parse Taskfile.yml to extract tasks."""
        try:
            with open(taskfile, 'r') as f:
                data = yaml.safe_load(f)
                return list(data.get('tasks', {}).keys())
        except:
            return []
    
    def detect_framework(self, path: Path, prog_type: str) -> Optional[Framework]:
        """Detect web frameworks and their entry points with enhanced support."""
        
        # Django detection
        manage_py = path / 'manage.py'
        if manage_py.exists():
            return Framework(
                name='Django',
                entry_point=manage_py,
                commands={
                    'runserver': 'python manage.py runserver',
                    'migrate': 'python manage.py migrate',
                    'shell': 'python manage.py shell',
                    'test': 'python manage.py test'
                }
            )
        
        # Flask detection
        if prog_type == 'Python':
            for file in path.glob('*.py'):
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'from flask import' in content or 'import flask' in content:
                            return Framework(
                                name='Flask',
                                entry_point=file,
                                commands={'run': f'python {file.name}', 'test': f'python -m pytest'}
                            )
                except:
                    pass
        
        # FastAPI detection
        if prog_type == 'Python':
            for file in path.glob('*.py'):
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'from fastapi import' in content or 'import fastapi' in content:
                            return Framework(
                                name='FastAPI',
                                entry_point=file,
                                commands={'run': f'uvicorn {file.stem}:app --reload', 'test': f'python -m pytest'}
                            )
                except:
                    pass
        
        # Next.js / React detection
        package_json = path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'next' in deps:
                        return Framework(
                            name='Next.js',
                            version=deps.get('next'),
                            commands={
                                'dev': 'npm run dev',
                                'build': 'npm run build',
                                'start': 'npm start',
                                'export': 'npm run export'
                            }
                        )
                    elif 'react' in deps:
                        return Framework(
                            name='React',
                            version=deps.get('react'),
                            commands={'start': 'npm start', 'build': 'npm run build', 'test': 'npm test'}
                        )
                    elif 'vue' in deps:
                        return Framework(
                            name='Vue.js',
                            version=deps.get('vue'),
                            commands={'serve': 'npm run serve', 'build': 'npm run build'}
                        )
                    elif 'angular' in deps.get('dependencies', {}):
                        return Framework(
                            name='Angular',
                            version=deps.get('dependencies', {}).get('@angular/core'),
                            commands={'serve': 'ng serve', 'build': 'ng build', 'test': 'ng test'}
                        )
                    elif 'svelte' in deps:
                        return Framework(
                            name='Svelte',
                            version=deps.get('svelte'),
                            commands={'dev': 'npm run dev', 'build': 'npm run build'}
                        )
                    elif 'nuxt' in deps:
                        return Framework(
                            name='Nuxt.js',
                            version=deps.get('nuxt'),
                            commands={'dev': 'npm run dev', 'build': 'npm run build', 'generate': 'npm run generate'}
                        )
                    elif 'express' in deps:
                        return Framework(
                            name='Express.js',
                            version=deps.get('express'),
                            commands={'start': 'npm start', 'dev': 'npm run dev'}
                        )
                    elif 'nest' in deps.get('dependencies', {}):
                        return Framework(
                            name='NestJS',
                            version=deps.get('dependencies', {}).get('@nestjs/core'),
                            commands={'start': 'npm run start', 'build': 'npm run build', 'test': 'npm run test'}
                        )
            except:
                pass
        
        # Ruby on Rails detection
        if prog_type == 'Ruby':
            gemfile = path / 'Gemfile'
            if gemfile.exists():
                try:
                    with open(gemfile, 'r') as f:
                        content = f.read()
                        if 'rails' in content:
                            return Framework(
                                name='Ruby on Rails',
                                commands={'server': 'rails server', 'console': 'rails console', 'test': 'rails test'}
                            )
                except:
                    pass
        
        # Laravel detection
        if prog_type == 'PHP':
            composer_json = path / 'composer.json'
            if composer_json.exists():
                try:
                    with open(composer_json, 'r') as f:
                        data = json.load(f)
                        deps = data.get('require', {})
                        if 'laravel/framework' in deps:
                            return Framework(
                                name='Laravel',
                                version=deps.get('laravel/framework'),
                                commands={'serve': 'php artisan serve', 'test': 'php artisan test'}
                            )
                except:
                    pass
        
        # Spring Boot detection
        if prog_type == 'Java':
            pom_xml = path / 'pom.xml'
            if pom_xml.exists():
                try:
                    with open(pom_xml, 'r') as f:
                        content = f.read()
                        if 'spring-boot' in content:
                            return Framework(
                                name='Spring Boot',
                                commands={'run': 'mvn spring-boot:run', 'test': 'mvn test'}
                            )
                except:
                    pass
        
        # Quarkus detection
        if prog_type == 'Java':
            if pom_xml.exists():
                try:
                    with open(pom_xml, 'r') as f:
                        content = f.read()
                        if 'quarkus' in content:
                            return Framework(
                                name='Quarkus',
                                commands={'dev': 'mvn quarkus:dev', 'test': 'mvn test'}
                            )
                except:
                    pass
        
        # Micronaut detection
        if prog_type == 'Java':
            if pom_xml.exists():
                try:
                    with open(pom_xml, 'r') as f:
                        content = f.read()
                        if 'micronaut' in content:
                            return Framework(
                                name='Micronaut',
                                commands={'run': 'mvn mn:run', 'test': 'mvn test'}
                            )
                except:
                    pass
        
        # Go frameworks
        if prog_type == 'Go':
            go_mod = path / 'go.mod'
            if go_mod.exists():
                try:
                    with open(go_mod, 'r') as f:
                        content = f.read()
                        if 'gin' in content:
                            return Framework(
                                name='Gin',
                                commands={'run': 'go run .', 'build': 'go build', 'test': 'go test'}
                            )
                        elif 'echo' in content:
                            return Framework(
                                name='Echo',
                                commands={'run': 'go run .', 'build': 'go build', 'test': 'go test'}
                            )
                except:
                    pass
        
        # Rust frameworks
        if prog_type == 'Rust':
            cargo_toml = path / 'Cargo.toml'
            if cargo_toml.exists():
                try:
                    with open(cargo_toml, 'r') as f:
                        content = f.read()
                        if 'actix' in content:
                            return Framework(
                                name='Actix',
                                commands={'run': 'cargo run', 'build': 'cargo build', 'test': 'cargo test'}
                            )
                        elif 'rocket' in content:
                            return Framework(
                                name='Rocket',
                                commands={'run': 'cargo run', 'build': 'cargo build', 'test': 'cargo test'}
                            )
                except:
                    pass
        
        return None
    
    def auto_fix_dependencies(self, prog: ExecutableProgram, interactive: bool = True, dry_run: bool = False, backup: bool = True) -> bool:
        """Auto-fix missing dependencies with safety features (THE KILLER FEATURE!)"""
        missing_deps = [d for d in prog.dependencies if d.required and not d.available and d.can_auto_fix]
        
        if not missing_deps:
            return True
        
        print(f"\n{Colors.WARNING}🔧 DEPENDENCY AUTO-FIX PROPOSAL{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"Program: {prog.name}")
        print(f"Location: {prog.relative_path}")
        print(f"Framework: {prog.framework.name if prog.framework else 'None'}")
        print(f"Missing Dependencies: {len(missing_deps)}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        # Show proposed command list
        print(f"{Colors.OKCYAN}📋 PROPOSED COMMANDS:{Colors.ENDC}")
        for i, dep in enumerate(missing_deps, 1):
            status = "🔧 Auto-fixable" if dep.can_auto_fix else "❌ Manual required"
            print(f"  {i}. {Colors.BOLD}{dep.name}{Colors.ENDC} - {status}")
            if dep.fix_command:
                print(f"     Command: {Colors.OKBLUE}{dep.fix_command}{Colors.ENDC}")
            if dep.message:
                print(f"     Info: {dep.message}")
            print()
        
        if dry_run:
            print(f"{Colors.OKCYAN}🔍 DRY RUN MODE - No changes will be made{Colors.ENDC}")
            return False
        
        # Auto-confirm if enabled
        if self.config.get('auto_confirm', False) or self.config.get('confirm_each_command', True) == False:
            confirm = True
        elif self.config.get('ask_each_command', False):
            # Ask for each command individually
            confirm = True
        elif not interactive:
            confirm = True
        else:
            response = input(f"\n{Colors.BOLD}Execute these {len(missing_deps)} commands? [y/N]: {Colors.ENDC}").strip().lower()
            confirm = response == 'y'
        
        if not confirm:
            print(f"{Colors.WARNING}❌ Auto-fix cancelled by user{Colors.ENDC}")
            return False
        
        # Create backup if enabled
        backup_created = False
        if backup and self.config.get('enable_backup', True):
            backup_created = self._create_backup(prog.path.parent)
            if backup_created:
                print(f"{Colors.OKGREEN}📦 Backup created{Colors.ENDC}")
        
        print(f"\n{Colors.OKCYAN}⚡ EXECUTING AUTO-FIX...{Colors.ENDC}\n")
        
        all_success = True
        executed_commands = []
        
        for i, dep in enumerate(missing_deps, 1):
            if dep.fix_command:
                print(f"{Colors.BOLD}[{i}/{len(missing_deps)}] Running: {dep.fix_command}{Colors.ENDC}")
                
                # Confirm per command if in safe mode
                if self.config.get('ask_each_command', False):
                    confirm_cmd = input(f"  Execute this command? [y/N]: ").strip().lower()
                    if confirm_cmd != 'y':
                        print(f"  {Colors.WARNING}⏭️  Skipped: {dep.name}{Colors.ENDC}")
                        continue
                
                try:
                    # Determine working directory
                    work_dir = prog.path.parent
                    
                    # Handle venv creation specially
                    if 'python -m venv' in dep.fix_command or 'python3 -m venv' in dep.fix_command:
                        result = subprocess.run(
                            dep.fix_command,
                            shell=True,
                            cwd=work_dir,
                            timeout=60,
                            capture_output=True,
                            text=True
                        )
                    else:
                        result = subprocess.run(
                            dep.fix_command,
                            shell=True,
                            cwd=work_dir,
                            timeout=300,
                            capture_output=True,
                            text=True
                        )
                    
                    executed_commands.append((dep.fix_command, result.returncode, result.stdout, result.stderr))
                    
                    if result.returncode == 0:
                        print(f"{Colors.OKGREEN}  ✅ Fixed: {dep.name}{Colors.ENDC}")
                        dep.available = True
                    else:
                        print(f"{Colors.FAIL}  ❌ Failed: {dep.name}{Colors.ENDC}")
                        if result.stderr:
                            print(f"     Error: {result.stderr.strip()}")
                        all_success = False
                
                except subprocess.TimeoutExpired:
                    print(f"{Colors.FAIL}  ⏰ Timeout: {dep.name}{Colors.ENDC}")
                    all_success = False
                except Exception as e:
                    print(f"{Colors.FAIL}  💥 Error: {dep.name} - {e}{Colors.ENDC}")
                    all_success = False
        
        # Show summary
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        if all_success:
            print(f"{Colors.OKGREEN}🎉 ALL DEPENDENCIES FIXED SUCCESSFULLY!{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠️  SOME DEPENDENCIES COULD NOT BE FIXED{Colors.ENDC}")
            print(f"     {Colors.OKCYAN}Check error messages above for details{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        # Rollback on failure if backup was created
        if not all_success and backup_created and self.config.get('auto_rollback', True):
            print(f"\n{Colors.WARNING}🔄 Rolling back changes...{Colors.ENDC}")
            self._rollback_backup(prog.path.parent)
        
        if all_success:
            print(f"\n{Colors.OKGREEN}✅ All dependencies fixed!{Colors.ENDC}\n")
        else:
            print(f"\n{Colors.WARNING}⚠️  Some dependencies could not be fixed{Colors.ENDC}\n")
        
        return all_success
    
    def _create_backup(self, work_dir: Path) -> bool:
        """Create a backup of the working directory before making changes."""
        try:
            import tempfile
            backup_dir = Path(tempfile.gettempdir()) / f"smart_launcher_backup_{int(time.time())}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a git stash if in a git repo
            if (work_dir / '.git').exists():
                try:
                    subprocess.run(['git', 'stash', 'push', '-m', 'Smart Launcher Auto-backup'], 
                                 cwd=work_dir, capture_output=True, timeout=30)
                    self._backup_info = {'type': 'git_stash', 'work_dir': work_dir}
                    return True
                except:
                    pass
            
            # Fallback: copy key files
            import shutil
            key_files = ['requirements.txt', 'package.json', 'Pipfile', 'poetry.lock', 'yarn.lock', 'pnpm-lock.yaml']
            for file in key_files:
                src = work_dir / file
                if src.exists():
                    shutil.copy2(src, backup_dir / file)
            
            self._backup_info = {'type': 'file_copy', 'backup_dir': backup_dir, 'work_dir': work_dir}
            return True
            
        except Exception as e:
            self.log(f"Failed to create backup: {e}", "WARNING")
            return False
    
    def _rollback_backup(self, work_dir: Path) -> bool:
        """Rollback changes using the backup."""
        try:
            if not hasattr(self, '_backup_info'):
                return False
                
            backup_info = self._backup_info
            
            if backup_info['type'] == 'git_stash':
                try:
                    subprocess.run(['git', 'stash', 'pop'], cwd=work_dir, capture_output=True, timeout=30)
                    return True
                except:
                    return False
            elif backup_info['type'] == 'file_copy':
                import shutil
                backup_dir = backup_info['backup_dir']
                key_files = ['requirements.txt', 'package.json', 'Pipfile', 'poetry.lock', 'yarn.lock', 'pnpm-lock.yaml']
                for file in key_files:
                    backup_file = backup_dir / file
                    target_file = work_dir / file
                    if backup_file.exists():
                        shutil.copy2(backup_file, target_file)
                
                # Clean up backup dir
                shutil.rmtree(backup_dir, ignore_errors=True)
                return True
                
        except Exception as e:
            self.log(f"Failed to rollback: {e}", "ERROR")
            return False
        
        return False
    
    def save_preferred_command(self, prog: ExecutableProgram, command: str):
        """Save the preferred command for a program."""
        key = f"{prog.type}:{prog.name}"
        self.preferred_commands[key] = command
        self.config['preferred_commands'] = self.preferred_commands
        
        # Save to user config file
        config_file = Path.home() / '.smartlauncher.yaml'
        try:
            existing_config = {}
            if config_file.exists():
                with open(config_file, 'r') as f:
                    existing_config = yaml.safe_load(f) or {}
            
            existing_config['preferred_commands'] = self.preferred_commands
            
            with open(config_file, 'w') as f:
                yaml.dump(existing_config, f, default_flow_style=False)
        except Exception as e:
            self.log(f"Failed to save preferred command: {e}", "WARNING")
    
    def run_with_watch_mode(self, prog: ExecutableProgram, args: List[str] = None) -> None:
        """Run program with file watching for auto-restart."""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            print(f"{Colors.FAIL}watchdog package required for watch mode. Install with: pip install watchdog{Colors.ENDC}")
            return
        
        class RestartHandler(FileSystemEventHandler):
            def __init__(self, launcher, prog, args):
                self.launcher = launcher
                self.prog = prog
                self.args = args
                self.process = None
                self.restart()
            
            def restart(self):
                if self.process and self.process.poll() is None:
                    self.process.terminate()
                    self.process.wait()
                
                print(f"{Colors.OKCYAN}🔄 Restarting {self.prog.name}...{Colors.ENDC}")
                result = self.launcher.execute_program_synchronously(self.prog, self.args)
                if result.status == ExecutionStatus.SUCCESS:
                    print(f"{Colors.OKGREEN}✓ Program restarted successfully{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}✗ Program failed to restart{Colors.ENDC}")
            
            def on_modified(self, event):
                if event.src_path.endswith(tuple(self.prog.type.get('extensions', []))):
                    self.restart()
        
        print(f"{Colors.OKCYAN}👀 Watch mode enabled. Monitoring for file changes...{Colors.ENDC}")
        print(f"{Colors.WARNING}Press Ctrl+C to stop{Colors.ENDC}")
        
        event_handler = RestartHandler(self, prog, args or [])
        observer = Observer()
        observer.schedule(event_handler, str(prog.path.parent), recursive=True)
        observer.start()
        
        try:
            observer.join()
        except KeyboardInterrupt:
            observer.stop()
            print(f"\n{Colors.WARNING}Watch mode stopped{Colors.ENDC}")
        observer.join()
    
    def run_with_profile_mode(self, prog: ExecutableProgram, args: List[str] = None) -> ExecutionResult:
        """Run program with profiling enabled."""
        import cProfile
        import pstats
        import io
        
        print(f"{Colors.OKCYAN}📊 Profiling enabled{Colors.ENDC}")
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = self.execute_program_synchronously(prog, args)
        finally:
            profiler.disable()
        
        # Generate profile report
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        profile_output = s.getvalue()
        
        # Save profile to file
        profile_file = f"profile_{prog.name}_{int(time.time())}.txt"
        with open(profile_file, 'w') as f:
            f.write(profile_output)
        
        print(f"{Colors.OKGREEN}📄 Profile saved to: {profile_file}{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Top 20 functions by cumulative time:{Colors.ENDC}")
        print(profile_output)
        
        return result
    
    def execute_program_synchronously(self, prog: ExecutableProgram, args: List[str] = None) -> ExecutionResult:
        """Execute program synchronously and return result."""
        start_time = datetime.now()
        
        try:
            # Build command
            if prog.type == 'Python':
                cmd = ['python3' if shutil.which('python3') else 'python', str(prog.path)]
            elif prog.type == 'JavaScript':
                cmd = ['node', str(prog.path)]
            elif prog.type == 'TypeScript':
                cmd = ['ts-node', str(prog.path)]
            elif prog.type == 'Go':
                cmd = ['go', 'run', str(prog.path)]
            elif prog.type == 'Rust':
                # For Rust, we need to build first
                build_result = subprocess.run(['cargo', 'build'], cwd=prog.path.parent, 
                                            capture_output=True, timeout=300)
                if build_result.returncode == 0:
                    cmd = ['cargo', 'run']
                else:
                    raise Exception("Cargo build failed")
            else:
                # Generic execution
                if os.access(prog.path, os.X_OK):
                    cmd = [str(prog.path)]
                else:
                    raise Exception(f"Don't know how to execute {prog.type} files")
            
            if args:
                cmd.extend(args)
            
            print(f"{Colors.BOLD}Executing: {' '.join(cmd)}{Colors.ENDC}")
            
            result = subprocess.run(
                cmd,
                cwd=prog.path.parent,
                capture_output=True,
                text=True,
                timeout=self.config.get('timeout', 300)
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            status = ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED
            
            execution_result = ExecutionResult(
                program=prog,
                status=status,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                args=args or []
            )
            
            # Print output
            if result.stdout:
                print(f"\n{Colors.BOLD}STDOUT:{Colors.ENDC}")
                print(result.stdout)
            
            if result.stderr:
                print(f"\n{Colors.WARNING}STDERR:{Colors.ENDC}")
                print(result.stderr)
            
            print(f"\n{Colors.OKGREEN if status == ExecutionStatus.SUCCESS else Colors.FAIL}Program finished with code {result.returncode} in {duration:.2f}s{Colors.ENDC}")
            
            # Save as preferred command
            command_used = f"{' '.join(cmd)} {' '.join(args) if args else ''}".strip()
            self.save_preferred_command(prog, command_used)
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            return ExecutionResult(
                program=prog,
                status=ExecutionStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                return_code=None,
                stdout="",
                stderr="Timeout expired",
                error_message="Execution timed out",
                args=args or []
            )
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            return ExecutionResult(
                program=prog,
                status=ExecutionStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                return_code=None,
                stdout="",
                stderr=str(e),
                error_message=str(e),
                args=args or []
            )
    
    def check_dependencies(self, filepath: Path, prog_type: str) -> List[DependencyCheck]:
        """Enhanced dependency checking with auto-fix support."""
        dependencies = []
        config = self.executable_patterns.get(prog_type, {})
        
        # Check interpreters
        interpreters = config.get('interpreters', [])
        for interpreter in interpreters:
            available, version = self.check_interpreter_available(interpreter)
            dependencies.append(DependencyCheck(
                name=interpreter,
                required=True,
                available=available,
                version=version,
                message=f"Interpreter {interpreter} {'found' if available else 'NOT FOUND'}",
                fix_command=self._get_interpreter_install_command(interpreter) if not available else None,
                can_auto_fix=False  # Interpreters typically need manual installation
            ))
        
        # Enhanced config file checking with auto-fix
        config_files = config.get('config_files', [])
        for config_file in config_files:
            config_path = filepath.parent / config_file
            if config_path.exists():
                dependencies.append(DependencyCheck(
                    name=config_file,
                    required=False,
                    available=True,
                    message=f"Configuration file {config_file} found"
                ))
                
                # Deep check with auto-fix support
                if config_file == 'package.json':
                    self._check_package_json_with_fix(config_path, dependencies, filepath.parent)
                elif config_file == 'requirements.txt':
                    self._check_requirements_txt_with_fix(config_path, dependencies, filepath.parent)
                elif config_file == 'Cargo.toml':
                    self._check_cargo_with_fix(config_path, dependencies, filepath.parent)
                elif config_file == 'go.mod':
                    self._check_go_mod_with_fix(config_path, dependencies, filepath.parent)
                elif config_file in ['pom.xml', 'build.gradle', 'build.gradle.kts']:
                    self._check_java_deps_with_fix(config_path, dependencies, filepath.parent)
        
        return dependencies
    
    def _check_package_json_with_fix(self, config_path: Path, dependencies: List[DependencyCheck], work_dir: Path):
        """Check Node.js dependencies with auto-fix support."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            deps = package_data.get('dependencies', {})
            dev_deps = package_data.get('devDependencies', {})
            
            if deps or dev_deps:
                node_modules = work_dir / 'node_modules'
                
                # Detect package manager
                if (work_dir / 'pnpm-lock.yaml').exists():
                    pkg_manager = 'pnpm'
                    install_cmd = 'pnpm install'
                elif (work_dir / 'yarn.lock').exists():
                    pkg_manager = 'yarn'
                    install_cmd = 'yarn install'
                else:
                    pkg_manager = 'npm'
                    install_cmd = 'npm install'
                
                if node_modules.exists():
                    dependencies.append(DependencyCheck(
                        name="node_modules",
                        required=True,
                        available=True,
                        message=f"Dependencies installed ({len(deps)} runtime, {len(dev_deps)} dev)"
                    ))
                else:
                    dependencies.append(DependencyCheck(
                        name="node_modules",
                        required=True,
                        available=False,
                        message=f"Dependencies NOT installed",
                        fix_command=f"cd {work_dir} && {install_cmd}",
                        can_auto_fix=True
                    ))
        except Exception as e:
            self.log(f"Error reading package.json: {e}", "WARNING")
    
    def _check_requirements_txt_with_fix(self, config_path: Path, dependencies: List[DependencyCheck], work_dir: Path):
        """Check Python dependencies with auto-fix and venv support."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if requirements:
                # Check for venv
                venv_exists = any((work_dir / venv_name).exists() for venv_name in ['venv', 'env', '.venv'])
                
                if not venv_exists and self.config.get('enable_venv', True):
                    # Suggest creating venv
                    python_cmd = 'python3' if shutil.which('python3') else 'python'
                    dependencies.append(DependencyCheck(
                        name="Python virtual environment",
                        required=False,
                        available=False,
                        message="Virtual environment not found (recommended)",
                        fix_command=f"cd {work_dir} && {python_cmd} -m venv venv",
                        can_auto_fix=True
                    ))
                
                # Check if packages are installed
                dependencies.append(DependencyCheck(
                    name="Python packages",
                    required=True,
                    available=True,  # Assume installed unless we can verify
                    message=f"{len(requirements)} packages required",
                    fix_command=f"cd {work_dir} && pip install -r requirements.txt",
                    can_auto_fix=True
                ))
        except Exception as e:
            self.log(f"Error reading requirements.txt: {e}", "WARNING")
    
    def _check_cargo_with_fix(self, config_path: Path, dependencies: List[DependencyCheck], work_dir: Path):
        """Check Rust/Cargo dependencies with auto-fix."""
        target_dir = work_dir / 'target'
        if not target_dir.exists():
            dependencies.append(DependencyCheck(
                name="Cargo dependencies",
                required=True,
                available=False,
                message="Project not built",
                fix_command=f"cd {work_dir} && cargo build",
                can_auto_fix=True
            ))
        else:
            dependencies.append(DependencyCheck(
                name="Cargo dependencies",
                required=True,
                available=True,
                message="Project built"
            ))
    
    def _check_go_mod_with_fix(self, config_path: Path, dependencies: List[DependencyCheck], work_dir: Path):
        """Check Go module dependencies with auto-fix."""
        dependencies.append(DependencyCheck(
            name="Go modules",
            required=True,
            available=True,
            message="Go modules defined",
            fix_command=f"cd {work_dir} && go mod tidy && go mod download",
            can_auto_fix=True
        ))
    
    def _check_java_deps_with_fix(self, config_path: Path, dependencies: List[DependencyCheck], work_dir: Path):
        """Check Java dependencies (Maven/Gradle) with auto-fix."""
        if config_path.name == 'pom.xml':
            dependencies.append(DependencyCheck(
                name="Maven dependencies",
                required=True,
                available=True,
                message="Maven project",
                fix_command=f"cd {work_dir} && mvn install",
                can_auto_fix=True
            ))
        else:
            gradle_wrapper = work_dir / 'gradlew'
            gradle_cmd = './gradlew' if gradle_wrapper.exists() else 'gradle'
            dependencies.append(DependencyCheck(
                name="Gradle dependencies",
                required=True,
                available=True,
                message="Gradle project",
                fix_command=f"cd {work_dir} && {gradle_cmd} build",
                can_auto_fix=True
            ))
    
    def _get_interpreter_install_command(self, interpreter: str) -> str:
        """Get installation command for an interpreter."""
        install_commands = {
            'python': 'Install from python.org or use your package manager',
            'python3': 'Install from python.org or use your package manager',
            'node': 'Install from nodejs.org or use nvm/package manager',
            'ruby': 'Install from ruby-lang.org or use rbenv/package manager',
            'go': 'Install from golang.org',
            'cargo': 'Install from rustup.rs',
            'java': 'Install JDK from adoptium.net or oracle.com'
        }
        return install_commands.get(interpreter, f"Install {interpreter}")
    
    def check_interpreter_available(self, interpreter: str) -> Tuple[bool, Optional[str]]:
        """Check if an interpreter/runtime is available and get its version."""
        try:
            exe_path = shutil.which(interpreter)
            if not exe_path:
                return False, None
            
            version_flags = ['--version', '-version', '-v']
            for flag in version_flags:
                try:
                    result = subprocess.run(
                        [interpreter, flag],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        version_output = result.stdout or result.stderr
                        version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', version_output)
                        if version_match:
                            return True, version_match.group(1)
                        return True, version_output.split('\n')[0][:50]
                except:
                    continue
            
            return True, "unknown"
        except Exception as e:
            return False, None
    
    def scan_for_executables(self, max_depth: int = None) -> List[ExecutableProgram]:
        """Scan for executables with enhanced detection."""
        if max_depth is None:
            max_depth = self.config.get('max_depth', 10)
        
        executables = []
        scanned_files = 0
        
        self.log(f"Starting enhanced scan of {self.base_path}", "INFO")
        
        def scan_directory(path: Path, current_depth: int = 0):
            nonlocal scanned_files
            
            if current_depth > max_depth:
                return
            
            # Detect environment at directory level
            environment = self.detect_environment(path)
            task_runners = self.detect_task_runners(path)
            
            try:
                for item in path.iterdir():
                    if item.is_file():
                        scanned_files += 1
                        
                        for prog_type, config in self.executable_patterns.items():
                            extensions = config['extensions']
                            
                            if item.suffix.lower() in extensions or (not item.suffix and prog_type == 'Executable'):
                                if prog_type == 'Executable' and item.suffix:
                                    continue
                                if prog_type == 'Executable' and not os.access(item, os.X_OK) and self.system != 'Windows':
                                    continue
                                
                                self.log(f"Analyzing {item.name}", "INFO")
                                
                                dependencies = self.check_dependencies(item, prog_type)
                                required_interpreters = [d for d in dependencies if d.required and d.name in config.get('interpreters', [])]
                                if required_interpreters and not any(d.available for d in required_interpreters):
                                    self.log(f"Skipping {item.name} - no interpreter available", "WARNING")
                                    continue
                                
                                score = self.is_likely_main_file(item)
                                config_files = self.get_config_files(item, prog_type)
                                complexity = self.estimate_complexity(item)
                                framework = self.detect_framework(item.parent, prog_type)
                                
                                executable = ExecutableProgram(
                                    path=item,
                                    name=item.name,
                                    relative_path=str(item.relative_to(self.base_path)),
                                    type=prog_type,
                                    interpreters=config.get('interpreters', []),
                                    score=score,
                                    dependencies=dependencies,
                                    has_config=len(config_files) > 0,
                                    config_files=config_files,
                                    estimated_complexity=complexity,
                                    environment=environment,
                                    framework=framework,
                                    task_runners=task_runners
                                )
                                
                                executables.append(executable)
                                break
                    
                    elif item.is_dir() and not item.name.startswith('.'):
                        if item.name not in self.config.get('exclude_dirs', []):
                            scan_directory(item, current_depth + 1)
            
            except PermissionError:
                self.log(f"Permission denied: {path}", "WARNING")
            except Exception as e:
                self.log(f"Error scanning {path}: {e}", "ERROR")
        
        scan_directory(self.base_path)
        executables.sort(key=lambda x: x.score, reverse=True)
        self.discovered_programs = executables
        
        self.log(f"Scan complete. {scanned_files} files scanned, {len(executables)} programs found", "SUCCESS")
        return executables
    
    # Utility methods from v2.0 (abbreviated for space)
    def is_likely_main_file(self, filepath: Path) -> int:
        """Score a file based on likelihood of being main entry point with framework awareness."""
        score = 0
        name_lower = filepath.stem.lower()
        filename_lower = filepath.name.lower()
        
        # Framework-specific main files get highest priority
        framework_main_files = {
            'Django': ['manage.py', 'wsgi.py', 'asgi.py'],
            'Flask': ['app.py', 'application.py', 'run.py', 'main.py'],
            'FastAPI': ['main.py', 'app.py', 'server.py'],
            'Next.js': ['pages/index.js', 'pages/_app.js', 'next.config.js'],
            'React': ['src/index.js', 'index.js', 'App.js'],
            'Vue.js': ['src/main.js', 'main.js'],
            'Angular': ['src/main.ts', 'main.ts'],
            'Gin': ['main.go'],
            'Echo': ['main.go'],
            'Actix': ['main.rs'],
            'Rocket': ['main.rs']
        }
        
        for framework, files in framework_main_files.items():
            if filename_lower in files:
                score += 50  # Framework main files get highest score
        
        for pattern in self.main_file_patterns:
            if re.match(pattern, filepath.name.lower()):
                score += 15
                break
        
        for main_name in ['main', 'app', 'index', 'start', 'run', 'manage', 'server', 'cli', 'entry']:
            if main_name in name_lower:
                score += 10
                if name_lower == main_name:
                    score += 5
        
        # Check for common executable patterns
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = [f.readline().strip() for _ in range(10)]
                
                # Shebang
                if first_lines and first_lines[0].startswith('#!'):
                    score += 8
                
                # Main function or app creation
                content = '\n'.join(first_lines)
                if 'if __name__ == "__main__":' in content:
                    score += 12
                if 'app =' in content or 'app =' in content:
                    score += 8
                if 'main(' in content or 'def main' in content:
                    score += 6
                    
        except:
            pass
        
        if self.system != 'Windows' and os.access(filepath, os.X_OK):
            score += 5
        
        # Directory depth penalty
        try:
            relative = filepath.relative_to(self.base_path)
            depth = len(relative.parts) - 1
            score += max(0, 10 - depth * 2)
        except ValueError:
            pass
        
        return score
    
    def has_shebang(self, filepath: Path) -> bool:
        """Check if file has a shebang line."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
                return first_line.startswith('#!')
        except:
            return False
    
    def get_config_files(self, filepath: Path, prog_type: str) -> List[str]:
        """Find configuration files related to the program."""
        config_files = []
        config = self.executable_patterns.get(prog_type, {})
        
        for config_file in config.get('config_files', []):
            config_path = filepath.parent / config_file
            if config_path.exists():
                config_files.append(config_file)
        
        return config_files
    
    def estimate_complexity(self, filepath: Path) -> str:
        """Estimate program complexity."""
        try:
            file_size = filepath.stat().st_size
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                
                if lines < 50:
                    return "Simple"
                elif lines < 200:
                    return "Moderate"
                elif lines < 1000:
                    return "Complex"
                else:
                    return "Very Complex"
            except:
                if file_size < 100 * 1024:
                    return "Small"
                elif file_size < 1024 * 1024:
                    return "Medium"
                else:
                    return "Large"
        except:
            return "Unknown"
    
    def display_programs_enhanced(self):
        """Display programs with enhanced information."""
        if not self.discovered_programs:
            print(f"\n{Colors.WARNING}No executable programs found.{Colors.ENDC}")
            return
        
        print(f"\n{Colors.BOLD}{'='*100}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}DISCOVERED PROGRAMS ({len(self.discovered_programs)} found){Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*100}{Colors.ENDC}\n")
        
        for idx, prog in enumerate(self.discovered_programs, 1):
            missing_deps = [d for d in prog.dependencies if d.required and not d.available]
            fixable_deps = [d for d in missing_deps if d.can_auto_fix]
            
            status_color = Colors.FAIL if missing_deps else Colors.OKGREEN
            status = "⚠ ISSUES" if missing_deps else "✓ READY"
            
            if fixable_deps:
                status += f" ({len(fixable_deps)} auto-fixable)"
            
            print(f"{Colors.BOLD}{idx}. [{prog.type}] {prog.relative_path}{Colors.ENDC}")
            print(f"   Status: {status_color}{status}{Colors.ENDC}")
            
            if prog.score >= 20:
                print(f"   {Colors.OKCYAN}★★★ High confidence main entry point (score: {prog.score}){Colors.ENDC}")
            elif prog.score >= 10:
                print(f"   {Colors.OKBLUE}★★ Likely entry point (score: {prog.score}){Colors.ENDC}")
            
            if prog.framework:
                print(f"   {Colors.OKGREEN}🎯 Framework: {prog.framework.name}{Colors.ENDC}")
            
            if prog.environment:
                print(f"   📦 Environment: {prog.environment.type}")
            
            if prog.task_runners:
                runners = ', '.join(tr.type for tr in prog.task_runners)
                print(f"   ⚙️  Task Runners: {runners}")
            
            if fixable_deps:
                print(f"   {Colors.OKCYAN}🔧 Can auto-fix dependencies{Colors.ENDC}")
            
            print()
    
    def execute_program(self, index: int, args: List[str] = None, auto_fix: bool = None, watch: bool = False, profile: bool = False) -> ExecutionResult:
        """Execute program with optional auto-fix, watch mode, and profiling."""
        if index < 0 or index >= len(self.discovered_programs):
            raise ValueError("Invalid program index")
        
        prog = self.discovered_programs[index]
        
        # Auto-fix if enabled and needed
        if auto_fix is None:
            auto_fix = self.config.get('auto_fix', False)
        
        missing_deps = [d for d in prog.dependencies if d.required and not d.available]
        if missing_deps and auto_fix:
            self.auto_fix_dependencies(prog, interactive=True)
        
        # Handle special modes
        if watch:
            self.run_with_watch_mode(prog, args)
            return ExecutionResult(
                program=prog,
                status=ExecutionStatus.SUCCESS,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration=0.0,
                return_code=0,
                stdout="Watch mode started",
                stderr="",
                args=args or []
            )
        elif profile:
            return self.run_with_profile_mode(prog, args)
        else:
            return self.execute_program_synchronously(prog, args)
    
    def generate_html_report(self, output_file: str):
        """Generate beautiful HTML report with Tailwind CSS and interactivity."""
        ready_count = sum(1 for prog in self.discovered_programs if not any(d.required and not d.available for d in prog.dependencies))
        issues_count = len(self.discovered_programs) - ready_count
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Launcher Report - {self.base_path.name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        'success': '#10b981',
                        'warning': '#f59e0b',
                        'error': '#ef4444',
                        'info': '#3b82f6'
                    }}
                }}
            }}
        }}
    </script>
    <style>
        .copy-btn {{
            transition: all 0.2s;
        }}
        .copy-btn:hover {{
            transform: scale(1.1);
        }}
        .status-badge {{
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-7xl">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900 flex items-center">
                        🚀 Smart Launcher Report
                    </h1>
                    <p class="text-gray-600 mt-2">Project: <span class="font-mono">{self.base_path}</span></p>
                    <p class="text-gray-600">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="text-right">
                    <div class="text-2xl font-bold text-gray-900">{len(self.discovered_programs)}</div>
                    <div class="text-sm text-gray-600">Programs Found</div>
                </div>
            </div>
            
            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div class="bg-success bg-opacity-10 border border-success rounded-lg p-4">
                    <div class="flex items-center">
                        <div class="text-success text-2xl">✅</div>
                        <div class="ml-3">
                            <div class="text-xl font-bold text-success">{ready_count}</div>
                            <div class="text-sm text-success">Ready to Run</div>
                        </div>
                    </div>
                </div>
                <div class="bg-error bg-opacity-10 border border-error rounded-lg p-4">
                    <div class="flex items-center">
                        <div class="text-error text-2xl">⚠️</div>
                        <div class="ml-3">
                            <div class="text-xl font-bold text-error">{issues_count}</div>
                            <div class="text-sm text-error">Need Attention</div>
                        </div>
                    </div>
                </div>
                <div class="bg-info bg-opacity-10 border border-info rounded-lg p-4">
                    <div class="flex items-center">
                        <div class="text-info text-2xl">🎯</div>
                        <div class="ml-3">
                            <div class="text-xl font-bold text-info">{sum(len(prog.task_runners) for prog in self.discovered_programs)}</div>
                            <div class="text-sm text-info">Task Runners</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Programs List -->
        <div class="space-y-6">
"""
        
        for idx, prog in enumerate(self.discovered_programs, 1):
            missing = [d for d in prog.dependencies if d.required and not d.available]
            css_class = "border-error" if missing else "border-success"
            status_icon = "❌" if missing else "✅"
            status_text = "Issues" if missing else "Ready"
            status_color = "text-error" if missing else "text-success"
            
            html += f"""
            <div class="bg-white rounded-lg shadow-md border-l-4 {css_class} overflow-hidden">
                <div class="p-6">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center">
                            <h3 class="text-xl font-bold text-gray-900">{idx}. {prog.name}</h3>
                            <span class="ml-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                                Score: {prog.score}
                            </span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <span class="status-badge inline-flex items-center px-3 py-1 rounded-full text-sm font-medium {status_color} bg-opacity-10">
                                {status_icon} {status_text}
                            </span>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <p class="text-sm text-gray-600"><strong>Path:</strong> <code class="bg-gray-100 px-2 py-1 rounded text-xs">{prog.relative_path}</code></p>
                            <p class="text-sm text-gray-600"><strong>Type:</strong> {prog.type}</p>
                            <p class="text-sm text-gray-600"><strong>Complexity:</strong> {prog.estimated_complexity}</p>
                        </div>
                        <div>
"""
            
            if prog.framework:
                html += f'                            <p class="text-sm text-gray-600"><strong>🎯 Framework:</strong> <span class="text-success font-medium">{prog.framework.name}</span></p>\n'
            
            if prog.environment:
                html += f'                            <p class="text-sm text-gray-600"><strong>📦 Environment:</strong> {prog.environment.type}</p>\n'
            
            if prog.task_runners:
                html += f'                            <p class="text-sm text-gray-600"><strong>⚙️ Task Runners:</strong> {", ".join(tr.type for tr in prog.task_runners)}</p>\n'
            
            html += f"""
                        </div>
                    </div>
                    
                    <!-- Dependencies Section -->
                    <div class="mt-4">
                        <details class="group">
                            <summary class="cursor-pointer bg-gray-50 hover:bg-gray-100 px-4 py-2 rounded-lg font-medium text-gray-900 flex items-center justify-between">
                                <span>Dependencies ({len(prog.dependencies)})</span>
                                <svg class="w-5 h-5 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                </svg>
                            </summary>
                            <div class="mt-2 space-y-2">
"""
            
            for dep in prog.dependencies:
                status_icon_dep = "✅" if dep.available else "❌"
                status_color_dep = "text-success" if dep.available else "text-error"
                bg_color = "bg-success" if dep.available else "bg-error"
                
                html += f"""
                                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div class="flex items-center">
                                        <span class="{status_color_dep} text-lg mr-3">{status_icon_dep}</span>
                                        <div>
                                            <span class="font-medium text-gray-900">{dep.name}</span>
                                            <p class="text-sm text-gray-600">{dep.message}</p>
                                        </div>
                                    </div>
"""
                
                if dep.fix_command:
                    html += f"""
                                    <button onclick="copyToClipboard('{dep.fix_command}')" class="copy-btn bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm flex items-center space-x-1">
                                        <span>📋</span>
                                        <span>Copy</span>
                                    </button>
"""
                
                html += "                                </div>"
            
            html += """
                            </div>
                        </details>
                    </div>
                    
                    <!-- Task Runners Section -->
"""
            
            if prog.task_runners:
                html += """
                    <div class="mt-4">
                        <details class="group">
                            <summary class="cursor-pointer bg-gray-50 hover:bg-gray-100 px-4 py-2 rounded-lg font-medium text-gray-900 flex items-center justify-between">
                                <span>Task Runners</span>
                                <svg class="w-5 h-5 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                </svg>
                            </summary>
                            <div class="mt-2 space-y-2">
"""
                
                for tr in prog.task_runners:
                    html += f"""
                                <div class="bg-gray-50 rounded-lg p-3">
                                    <h4 class="font-medium text-gray-900 uppercase text-sm mb-2">{tr.type}</h4>
                                    <div class="space-y-1">
"""
                    
                    for task in tr.tasks:
                        html += f"""
                                        <div class="flex items-center justify-between">
                                            <code class="bg-gray-200 px-2 py-1 rounded text-sm">{task}</code>
                                            <button onclick="copyToClipboard('{tr.type} {task}')" class="copy-btn bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded text-xs">
                                                📋
                                            </button>
                                        </div>
"""
                    
                    html += "                                    </div>\n                                </div>"
                
                html += "                            </div>\n                        </details>\n                    </div>"
            
            html += "                </div>\n            </div>"
        
        html += """
        </div>
    </div>
    
    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                // Show temporary success message
                const notification = document.createElement('div');
                notification.className = 'fixed top-4 right-4 bg-success text-white px-4 py-2 rounded-lg shadow-lg z-50';
                notification.textContent = 'Copied to clipboard!';
                document.body.appendChild(notification);
                setTimeout(() => document.body.removeChild(notification), 2000);
            });
        }
        
        // Add smooth scrolling and animations
        document.addEventListener('DOMContentLoaded', function() {
            // Animate stats cards on load
            const cards = document.querySelectorAll('[class*="bg-opacity-10"]');
            cards.forEach((card, index) => {
                card.style.animationDelay = `${index * 0.1}s`;
                card.classList.add('animate-fade-in');
            });
        });
    </script>
</body>
</html>"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"{Colors.OKGREEN}✨ Beautiful HTML report saved to: {output_file}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Tip: Open in browser and click 📋 buttons to copy commands{Colors.ENDC}")
    
    def show_environment_activation_hints(self):
        """Show environment activation commands for detected environments."""
        if not self.discovered_programs:
            return
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}ENVIRONMENT ACTIVATION HINTS{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        activation_commands = []
        
        for prog in self.discovered_programs:
            if prog.environment:
                env = prog.environment
                if env.type == 'venv':
                    venv_path = env.path or prog.path.parent / 'venv'
                    if venv_path.exists():
                        cmd = f"source {venv_path}/bin/activate  # For {prog.name}"
                        if cmd not in activation_commands:
                            activation_commands.append(cmd)
                
                elif env.type == 'conda':
                    # Try to detect conda environment name
                    conda_env_name = None
                    if env.path:
                        env_file = env.path / 'environment.yml'
                        if env_file.exists():
                            try:
                                import yaml
                                with open(env_file, 'r') as f:
                                    env_data = yaml.safe_load(f)
                                    conda_env_name = env_data.get('name')
                            except:
                                pass
                    
                    if conda_env_name:
                        cmd = f"conda activate {conda_env_name}  # For {prog.name}"
                    else:
                        cmd = f"conda activate  # For {prog.name} (environment name unknown)"
                    
                    if cmd not in activation_commands:
                        activation_commands.append(cmd)
                
                elif env.type == 'docker-compose':
                    compose_file = env.path or prog.path.parent / 'docker-compose.yml'
                    if compose_file.exists():
                        cmd = f"docker-compose up  # For {prog.name}"
                        if cmd not in activation_commands:
                            activation_commands.append(cmd)
        
        if activation_commands:
            print(f"{Colors.OKCYAN}Ready-to-paste activation commands:{Colors.ENDC}")
            for cmd in activation_commands:
                print(f"  {Colors.OKGREEN}{cmd}{Colors.ENDC}")
        else:
            print(f"{Colors.OKCYAN}No environment activation needed - all programs ready to run!{Colors.ENDC}")
    
    def generate_json_report(self, output_file):
        """Generate JSON report for tooling integration."""
        report = {
            'project': str(self.base_path),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_programs': len(self.discovered_programs),
                'by_type': {},
                'ready_count': 0,
                'issues_count': 0
            },
            'programs': []
        }
        
        for prog in self.discovered_programs:
            missing = [d for d in prog.dependencies if d.required and not d.available]
            
            if missing:
                report['summary']['issues_count'] += 1
            else:
                report['summary']['ready_count'] += 1
            
            report['summary']['by_type'][prog.type] = report['summary']['by_type'].get(prog.type, 0) + 1
            
            prog_data = {
                'name': prog.name,
                'path': prog.relative_path,
                'type': prog.type,
                'score': prog.score,
                'complexity': prog.estimated_complexity,
                'dependencies': [
                    {
                        'name': d.name,
                        'available': d.available,
                        'required': d.required,
                        'fix_command': d.fix_command,
                        'can_auto_fix': d.can_auto_fix
                    }
                    for d in prog.dependencies
                ]
            }
            
            if prog.framework:
                prog_data['framework'] = prog.framework.name
            
            if prog.task_runners:
                prog_data['task_runners'] = [tr.type for tr in prog.task_runners]
            
            report['programs'].append(prog_data)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"{Colors.OKGREEN}JSON report saved to: {output_file}{Colors.ENDC}")
    
    def list_available_commands(self):
        """List all available commands for discovered programs without executing."""
        if not self.discovered_programs:
            print(f"{Colors.WARNING}No programs found to list commands for.{Colors.ENDC}")
            return
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}AVAILABLE COMMANDS{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
        
        for idx, prog in enumerate(self.discovered_programs, 1):
            print(f"{Colors.BOLD}{idx}. {prog.name} ({prog.type}){Colors.ENDC}")
            print(f"   Path: {prog.relative_path}")
            
            if prog.framework and prog.framework.commands:
                print(f"   {Colors.OKCYAN}Framework Commands:{Colors.ENDC}")
                for cmd_name, cmd in prog.framework.commands.items():
                    print(f"     • {cmd_name}: {cmd}")
            
            if prog.task_runners:
                print(f"   {Colors.OKCYAN}Task Runners:{Colors.ENDC}")
                for tr in prog.task_runners:
                    print(f"     • {tr.type}: {len(tr.tasks)} tasks available")
                    if tr.tasks[:3]:  # Show first 3 tasks
                        for task in tr.tasks[:3]:
                            print(f"       - {task}")
                        if len(tr.tasks) > 3:
                            print(f"       ... and {len(tr.tasks) - 3} more")
            
            # Show preferred command if available
            key = f"{prog.type}:{prog.name}"
            if key in self.preferred_commands:
                print(f"   {Colors.OKGREEN}Last used: {self.preferred_commands[key]}{Colors.ENDC}")
            
            print()
    
    def run_tui_mode(self):
        """Run rich TUI interface for enhanced user experience."""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            from rich.text import Text
            from rich.prompt import Prompt, Confirm
            from rich.live import Live
            from rich.spinner import Spinner
            from rich.columns import Columns
        except ImportError:
            print(f"{Colors.FAIL}Rich library required for TUI mode. Install with: pip install rich{Colors.ENDC}")
            return
        
        console = Console()
        
        # Header
        header_text = Text("🚀 Smart Launcher v3.0", style="bold blue")
        header_panel = Panel(header_text, title="Ultimate Multi-Platform Executable Discovery System", border_style="blue")
        console.print(header_panel)
        
        # Scan with spinner
        with console.status("[bold green]Scanning directory...[/bold green]", spinner="dots"):
            self.scan_for_executables()
        
        if not self.discovered_programs:
            console.print("[red]No executable programs found.[/red]")
            return
        
        # Programs table
        table = Table(title="Discovered Programs")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Program", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Framework", style="blue")
        
        for idx, prog in enumerate(self.discovered_programs, 1):
            missing = [d for d in prog.dependencies if d.required and not d.available]
            status = "⚠️ Issues" if missing else "✅ Ready"
            framework = prog.framework.name if prog.framework else "None"
            
            table.add_row(str(idx), prog.name, prog.type, status, framework)
        
        console.print(table)
        
        # Interactive loop
        while True:
            console.print("\n[bold cyan]Commands:[/bold cyan]")
            console.print("• [green]1-{}[/green] - Execute program".format(len(self.discovered_programs)))
            console.print("• [green]d 1[/green] - Show program details")
            console.print("• [green]f 1[/green] - Auto-fix dependencies")
            console.print("• [green]html report.html[/green] - Generate HTML report")
            console.print("• [green]q[/green] - Quit")
            
            choice = Prompt.ask("\nEnter command").strip()
            
            if choice.lower() == 'q':
                break
            elif choice.startswith('d ') and len(choice.split()) == 2:
                try:
                    idx = int(choice.split()[1]) - 1
                    if 0 <= idx < len(self.discovered_programs):
                        prog = self.discovered_programs[idx]
                        self._show_program_details_tui(console, prog)
                    else:
                        console.print("[red]Invalid program number.[/red]")
                except ValueError:
                    console.print("[red]Invalid command format.[/red]")
            elif choice.startswith('f ') and len(choice.split()) == 2:
                try:
                    idx = int(choice.split()[1]) - 1
                    if 0 <= idx < len(self.discovered_programs):
                        prog = self.discovered_programs[idx]
                        self._auto_fix_tui(console, prog)
                    else:
                        console.print("[red]Invalid program number.[/red]")
                except ValueError:
                    console.print("[red]Invalid command format.[/red]")
            elif choice.startswith('html ') and len(choice.split()) == 2:
                filename = choice.split()[1]
                with console.status(f"[bold green]Generating HTML report...[/bold green]", spinner="dots"):
                    self.generate_html_report(filename)
                console.print(f"[green]HTML report saved to: {filename}[/green]")
            elif choice.isdigit():
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.discovered_programs):
                        prog = self.discovered_programs[idx]
                        self._execute_program_tui(console, prog)
                    else:
                        console.print("[red]Invalid program number.[/red]")
                except ValueError:
                    console.print("[red]Invalid program number.[/red]")
            else:
                console.print("[red]Unknown command. Type 'q' to quit.[/red]")
    
    def _show_program_details_tui(self, console, prog):
        """Show detailed program information in TUI mode."""
        details_table = Table(title=f"Details: {prog.name}")
        details_table.add_column("Property", style="cyan")
        details_table.add_column("Value", style="white")
        
        details_table.add_row("Path", str(prog.relative_path))
        details_table.add_row("Type", prog.type)
        details_table.add_row("Score", str(prog.score))
        details_table.add_row("Complexity", prog.estimated_complexity)
        
        if prog.framework:
            details_table.add_row("Framework", prog.framework.name)
        
        if prog.environment:
            details_table.add_row("Environment", prog.environment.type)
        
        console.print(details_table)
        
        # Dependencies
        if prog.dependencies:
            dep_table = Table(title="Dependencies")
            dep_table.add_column("Dependency", style="cyan")
            dep_table.add_column("Status", style="green")
            dep_table.add_column("Required", style="yellow")
            
            for dep in prog.dependencies:
                status = "✅ Available" if dep.available else "❌ Missing"
                required = "Yes" if dep.required else "No"
                dep_table.add_row(dep.name, status, required)
            
            console.print(dep_table)
    
    def _auto_fix_tui(self, console, prog):
        """Auto-fix dependencies in TUI mode."""
        missing_deps = [d for d in prog.dependencies if d.required and not d.available and d.can_auto_fix]
        
        if not missing_deps:
            console.print("[green]No auto-fixable dependencies found.[/green]")
            return
        
        # Show proposed fixes
        fix_table = Table(title="Proposed Auto-Fixes")
        fix_table.add_column("Dependency", style="cyan")
        fix_table.add_column("Command", style="white")
        
        for dep in missing_deps:
            if dep.fix_command:
                fix_table.add_row(dep.name, dep.fix_command)
        
        console.print(fix_table)
        
        if Confirm.ask("Execute these auto-fixes?"):
            with console.status("[bold green]Executing auto-fixes...[/bold green]", spinner="dots"):
                success = self.auto_fix_dependencies(prog, interactive=False)
            
            if success:
                console.print("[green]✅ All dependencies fixed successfully![/green]")
            else:
                console.print("[red]❌ Some dependencies could not be fixed.[/red]")
    
    def _execute_program_tui(self, console, prog):
        """Execute program in TUI mode."""
        args = Prompt.ask("Arguments (optional)", default="").strip()
        args_list = args.split() if args else None
        
        with console.status(f"[bold green]Executing {prog.name}...[/bold green]", spinner="dots"):
            result = self.execute_program_synchronously(prog, args_list)
        
        if result.return_code == 0:
            console.print(f"[green]✅ Program executed successfully in {result.duration:.2f}s[/green]")
        else:
            console.print(f"[red]❌ Program failed with code {result.return_code} in {result.duration:.2f}s[/red]")
        
        if result.stdout:
            console.print(Panel(result.stdout, title="Output", border_style="blue"))
        
        if result.stderr:
            console.print(Panel(result.stderr, title="Errors", border_style="red"))
    
    def show_environment_activation_hints(self):
        """Show environment activation hints for discovered programs."""
        env_hints = []
        
        for prog in self.discovered_programs:
            if prog.environment and prog.environment.activation_command:
                env_hints.append(f"• {prog.name}: {prog.environment.activation_command}")
        
        if env_hints:
            print(f"\n{Colors.HEADER}ENVIRONMENT ACTIVATION HINTS{Colors.ENDC}")
            print("=" * 50)
            for hint in env_hints:
                print(hint)
            print()
        else:
            print(f"\n{Colors.OKGREEN}No environment activation needed - all programs ready to run!{Colors.ENDC}\n")
    
    def interactive_mode(self):
        """Enhanced interactive mode with TUI support."""
        if self.config.get('tui_mode', False):
            self.run_tui_mode()
        else:
            self._terminal_interactive_mode()
    
    def _terminal_interactive_mode(self):
        """Terminal-based interactive mode (fallback)."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔═══════════════════════════════════════════════════════════════════════════════════════════════╗")
        print("║                              SMART LAUNCHER v3.0                                              ║")
        print("║                   🚀 Ultimate Multi-Platform Executable Discovery System                      ║")
        print("╚═══════════════════════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        print(f"{Colors.BOLD}Scanning Directory:{Colors.ENDC} {self.base_path}\n")
        
        self.scan_for_executables()
        self.display_programs_enhanced()
        self.show_environment_activation_hints()
        
        if not self.discovered_programs:
            print(f"{Colors.WARNING}No executable programs found.{Colors.ENDC}")
            return
        
        while True:
            try:
                print(f"\n{Colors.OKCYAN}Available Commands:{Colors.ENDC}")
                print("  [number]              - Execute program")
                print("  [number] -- arg1 arg2 - Execute with arguments")
                print("  w [num]               - Execute in watch mode")
                print("  p [num]               - Execute with profiling")
                print("  d [num]               - Show detailed info")
                print("  f [num]               - Auto-fix dependencies")
                print("  t [num]               - Show task runners")
                print("  html [file]           - Generate HTML report")
                print("  json [file]           - Generate JSON report")
                print("  r                     - Generate text report")
                print("  s                     - Rescan directory")
                print("  q                     - Quit")
                
                choice = input(f"\n{Colors.OKCYAN}Enter command: {Colors.ENDC}").strip()
                
                if not choice:
                    continue
                
                if choice.lower() == 'q':
                    print(f"\n{Colors.OKGREEN}Thank you for using Smart Launcher v3.0!{Colors.ENDC}\n")
                    break
                
                elif choice.lower() == 's':
                    print(f"\n{Colors.OKCYAN}Rescanning...{Colors.ENDC}")
                    self.scan_for_executables()
                    self.display_programs_enhanced()
                    self.show_environment_activation_hints()
                
                elif choice.lower().startswith('d '):
                    try:
                        index = int(choice.split()[1]) - 1
                        if 0 <= index < len(self.discovered_programs):
                            prog = self.discovered_programs[index]
                            self._show_program_details_terminal(prog)
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except (ValueError, IndexError):
                        print(f"{Colors.FAIL}Invalid command format. Use: d [number]{Colors.ENDC}")
                
                elif choice.lower().startswith('f '):
                    try:
                        index = int(choice.split()[1]) - 1
                        if 0 <= index < len(self.discovered_programs):
                            prog = self.discovered_programs[index]
                            self.auto_fix_dependencies(prog, interactive=True)
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except (ValueError, IndexError):
                        print(f"{Colors.FAIL}Invalid command format. Use: f [number]{Colors.ENDC}")
                
                elif choice.lower().startswith('html '):
                    filename = choice.split(maxsplit=1)[1] if len(choice.split()) > 1 else f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    self.generate_html_report(filename)
                
                elif choice.lower().startswith('json '):
                    filename = choice.split(maxsplit=1)[1] if len(choice.split()) > 1 else f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    self.generate_json_report(filename)
                
                elif choice.lower().startswith('w '):
                    try:
                        index = int(choice.split()[1]) - 1
                        if 0 <= index < len(self.discovered_programs):
                            self.execute_program(index, watch=True)
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except (ValueError, IndexError):
                        print(f"{Colors.FAIL}Invalid command format. Use: w [number]{Colors.ENDC}")
                
                elif choice.lower().startswith('p '):
                    try:
                        index = int(choice.split()[1]) - 1
                        if 0 <= index < len(self.discovered_programs):
                            self.execute_program(index, profile=True)
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except (ValueError, IndexError):
                        print(f"{Colors.FAIL}Invalid command format. Use: p [number]{Colors.ENDC}")
                
                elif choice.isdigit():
                    try:
                        index = int(choice) - 1
                        if 0 <= index < len(self.discovered_programs):
                            args_input = input("Arguments (optional): ").strip()
                            args = args_input.split() if args_input else None
                            self.execute_program(index, args=args)
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except ValueError:
                        print(f"{Colors.FAIL}Invalid number{Colors.ENDC}")
                
                else:
                    print(f"{Colors.WARNING}Unknown command. Type 'q' to quit.{Colors.ENDC}")
            
            except KeyboardInterrupt:
                print(f"\n\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
    
    def _show_program_details_terminal(self, prog):
        """Show program details in terminal mode."""
        print(f"\n{Colors.BOLD}{'='*50}{Colors.ENDC}")
        print(f"{Colors.HEADER}Details: {prog.name}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*50}{Colors.ENDC}")
        print(f"Path: {prog.relative_path}")
        print(f"Type: {prog.type}")
        print(f"Score: {prog.score}")
        print(f"Complexity: {prog.estimated_complexity}")
        
        if prog.framework:
            print(f"Framework: {prog.framework.name}")
        
        if prog.environment:
            print(f"Environment: {prog.environment.type}")
        
        if prog.dependencies:
            print(f"\n{Colors.OKCYAN}Dependencies:{Colors.ENDC}")
            for dep in prog.dependencies:
                status = "✅" if dep.available else "❌"
                required = "(required)" if dep.required else "(optional)"
                print(f"  {status} {dep.name} {required}")
                if dep.fix_command and not dep.available:
                    print(f"      Fix: {dep.fix_command}")
        
        print()
        
        while True:
            try:
                print(f"\n{Colors.OKCYAN}Available Commands:{Colors.ENDC}")
                print("  [number]              - Execute program")
                print("  [number] -- arg1 arg2 - Execute with arguments")
                print("  w [num]               - Execute in watch mode")
                print("  p [num]               - Execute with profiling")
                print("  d [num]               - Show detailed info")
                print("  f [num]               - Auto-fix dependencies")
                print("  t [num]               - Show task runners")
                print("  html [file]           - Generate HTML report")
                print("  json [file]           - Generate JSON report")
                print("  r                     - Generate text report")
                print("  s                     - Rescan directory")
                print("  q                     - Quit")
                
                choice = input(f"\n{Colors.OKCYAN}Enter command: {Colors.ENDC}").strip()
                
                if not choice:
                    continue
                
                if choice.lower() == 'q':
                    print(f"\n{Colors.OKGREEN}Thank you for using Smart Launcher v3.0!{Colors.ENDC}\n")
                    break
                
                elif choice.lower().startswith('w '):
                    try:
                        index = int(choice.split()[1]) - 1
                        if 0 <= index < len(self.discovered_programs):
                            self.execute_program(index, watch=True)
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except (ValueError, IndexError):
                        print(f"{Colors.FAIL}Invalid command format. Use: w [number]{Colors.ENDC}")
                
                elif choice.lower().startswith('p '):
                    try:
                        index = int(choice.split()[1]) - 1
                        if 0 <= index < len(self.discovered_programs):
                            self.execute_program(index, profile=True)
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except (ValueError, IndexError):
                        print(f"{Colors.FAIL}Invalid command format. Use: p [number]{Colors.ENDC}")
                
                elif choice.isdigit():
                    try:
                        index = int(choice) - 1
                        if 0 <= index < len(self.discovered_programs):
                            args_input = input("Arguments (optional): ").strip()
                            args = args_input.split() if args_input else None
                            self.execute_program(index, args=args)
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except ValueError:
                        print(f"{Colors.FAIL}Invalid number{Colors.ENDC}")
                
                elif choice.lower().startswith('f '):
                    try:
                        index = int(choice.split()[1]) - 1
                        if 0 <= index < len(self.discovered_programs):
                            prog = self.discovered_programs[index]
                            self.auto_fix_dependencies(prog, interactive=True)
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except (ValueError, IndexError):
                        print(f"{Colors.FAIL}Invalid command format. Use: f [number]{Colors.ENDC}")
                
                elif choice.lower().startswith('t '):
                    try:
                        index = int(choice.split()[1]) - 1
                        if 0 <= index < len(self.discovered_programs):
                            prog = self.discovered_programs[index]
                            if prog.task_runners:
                                print(f"\n{Colors.BOLD}Task Runners for {prog.name}:{Colors.ENDC}")
                                for tr in prog.task_runners:
                                    print(f"\n{Colors.OKCYAN}{tr.type.upper()}:{Colors.ENDC}")
                                    for task in tr.tasks:
                                        print(f"  • {task}")
                            else:
                                print(f"{Colors.WARNING}No task runners found{Colors.ENDC}")
                        else:
                            print(f"{Colors.FAIL}Invalid program number{Colors.ENDC}")
                    except (ValueError, IndexError):
                        print(f"{Colors.FAIL}Invalid command format. Use: t [number]{Colors.ENDC}")
                
                elif choice.lower().startswith('html '):
                    filename = choice.split(maxsplit=1)[1] if len(choice.split()) > 1 else f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    self.generate_html_report(filename)
                
                elif choice.lower().startswith('json '):
                    filename = choice.split(maxsplit=1)[1] if len(choice.split()) > 1 else f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    self.generate_json_report(filename)
                
                # ... (other commands from v2.0)
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")


def main():
    """Main entry point with enhanced argument parsing."""
    parser = argparse.ArgumentParser(
        description="OmniRun v3.0 - Ultimate Multi-Platform Executable Discovery System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('path', nargs='?', default='.', help='Directory to scan')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-d', '--max-depth', type=int, default=10, help='Maximum scan depth')
    parser.add_argument('-r', '--report', type=str, help='Generate text report')
    parser.add_argument('--html', type=str, help='Generate HTML report')
    parser.add_argument('--json', type=str, help='Generate JSON report')
    parser.add_argument('--auto-fix', action='store_true', help='Automatically fix dependencies')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--yes', action='store_true', help='Auto-confirm all prompts (for CI/automation)')
    parser.add_argument('--no-confirm', action='store_true', help='Skip all confirmation prompts')
    parser.add_argument('--watch', action='store_true', help='Run in watch mode')
    parser.add_argument('--profile', action='store_true', help='Run with profiling')
    parser.add_argument('--tui', action='store_true', help='Use rich TUI interface instead of terminal')
    parser.add_argument('--list-commands', action='store_true', help='List available commands without executing')
    parser.add_argument('--ask-each', action='store_true', help='Ask for confirmation before each command')
    parser.add_argument('--args', nargs='*', help='Arguments to pass to the program')
    parser.add_argument('--config', type=str, help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        launcher = OmniRun(args.path, verbose=args.verbose, config_file=args.config)
        
        if args.auto_fix:
            launcher.config['auto_fix'] = True
        
        if args.dry_run:
            launcher.config['dry_run'] = True
            
        if args.yes:
            launcher.config['auto_confirm'] = True
            launcher.config['confirm_each_command'] = False
            
        if args.tui:
            launcher.config['tui_mode'] = True
        
        if args.list_commands:
            launcher.scan_for_executables(max_depth=args.max_depth)
            launcher.list_available_commands()
            return
        
        if args.ask_each:
            launcher.config['ask_each_command'] = True
        
        if args.tui:
            launcher.run_tui_mode()
            return
        
        if args.html or args.json or args.report:
            launcher.scan_for_executables(max_depth=args.max_depth)
            if args.html:
                launcher.generate_html_report(args.html)
            if args.json:
                launcher.generate_json_report(args.json)
            if args.report:
                # Text report generation (from v2.0)
                pass
        elif args.watch or args.profile or args.args:
            # Direct execution mode
            launcher.scan_for_executables(max_depth=args.max_depth)
            if not launcher.discovered_programs:
                print(f"{Colors.FAIL}No programs found to execute{Colors.ENDC}")
                sys.exit(1)
            
            # Use first program or try to find main entry point
            prog_index = 0
            for i, prog in enumerate(launcher.discovered_programs):
                if prog.score >= 20:
                    prog_index = i
                    break
            
            launcher.execute_program(prog_index, args=args.args, watch=args.watch, profile=args.profile)
        else:
            launcher.interactive_mode()
    
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Fatal error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
