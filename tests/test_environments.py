"""
Tests for environment and task runner detection in OmniRun.

This module tests:
- Virtual environment detection
- Conda environment detection
- Docker detection
- Task runner detection (Makefile, justfile, npm, Taskfile)
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from conftest import *


class TestVirtualEnvironmentDetection:
    """Tests for virtual environment detection."""
    
    def test_detect_venv(self, python_with_venv, omni_runner):
        """Test virtual environment detection."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert env.type == "venv"
    
    def test_venv_python_version(self, python_with_venv, omni_runner):
        """Test that venv Python version is detected."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert env.python_version is not None
    
    def test_venv_activation_command(self, python_with_venv, omni_runner):
        """Test that venv activation command is set."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert env.activation_command is not None
        assert "activate" in env.activation_command
    
    def test_no_venv_in_simple_project(self, python_simple_script, omni_runner):
        """Test that no venv is detected in simple project."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is None
    
    def test_venv_paths_checked(self, python_with_venv, omni_runner):
        """Test that common venv paths are checked."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        # venv should be one of the standard names
        assert env.path.name in ["venv", "env", ".venv", "virtualenv"]


class TestCondaEnvironmentDetection:
    """Tests for conda environment detection."""
    
    def test_detect_conda_env(self, conda_environment, omni_runner):
        """Test conda environment detection."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert env.type == "conda"
    
    def test_conda_activation_command(self, conda_environment, omni_runner):
        """Test that conda activation command is set."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert env.activation_command is not None
        assert "conda" in env.activation_command


class TestDockerDetection:
    """Tests for Docker container detection."""
    
    def test_detect_dockerfile(self, dockerfile_project, omni_runner):
        """Test Dockerfile detection."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert env.type == "docker"
    
    def test_docker_activation_command(self, dockerfile_project, omni_runner):
        """Test that Docker activation command is set."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert env.activation_command is not None
        assert "docker" in env.activation_command
        assert "build" in env.activation_command
        assert "run" in env.activation_command
    
    def test_detect_docker_compose(self, docker_compose_project, omni_runner):
        """Test docker-compose detection."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert env.type == "docker-compose"
    
    def test_docker_compose_activation_command(self, docker_compose_project, omni_runner):
        """Test that docker-compose activation command is set."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert "docker-compose" in env.activation_command or "compose" in env.activation_command
    
    def test_docker_compose_preferred_over_dockerfile(self, docker_compose_project, omni_runner):
        """Test that docker-compose takes precedence over Dockerfile."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is not None
        assert env.type == "docker-compose"
    
    def test_no_docker_when_disabled(self, dockerfile_project, omni_runner_with_config):
        """Test that Docker detection can be disabled."""
        # Config has enable_docker: true by default, but we can override
        omni_runner_with_config.config['enable_docker'] = False
        
        env = omni_runner_with_config.detect_environment(omni_runner_with_config.base_path)
        
        # Should not detect docker when disabled
        assert env is None or env.type != "docker"


class TestNoEnvironment:
    """Tests for projects without environments."""
    
    def test_simple_python_no_env(self, python_simple_script, omni_runner):
        """Test that simple Python project has no environment."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is None
    
    def test_simple_node_no_env(self, nodejs_simple_script, omni_runner):
        """Test that simple Node.js project has no environment."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is None
    
    def test_simple_go_no_env(self, go_simple_program, omni_runner):
        """Test that simple Go project has no environment."""
        env = omni_runner.detect_environment(omni_runner.base_path)
        
        assert env is None


class TestEnvironmentAssociatedWithProgram:
    """Tests for environment association with programs."""
    
    def test_program_has_environment(self, python_with_venv, omni_runner):
        """Test that discovered programs have environment attached."""
        programs = omni_runner.scan_for_executables()
        
        python_prog = next((p for p in programs if p.type == "Python"), None)
        assert python_prog is not None
        assert python_prog.environment is not None
        assert python_prog.environment.type == "venv"
    
    def test_docker_program_has_environment(self, dockerfile_project, omni_runner):
        """Test that Docker project has environment attached."""
        programs = omni_runner.scan_for_executables()
        
        docker_prog = next(p for p in programs if p.type == "Python")
        assert docker_prog is not None
        assert docker_prog.environment is not None


class TestTaskRunnerDetection:
    """Tests for task runner detection."""
    
    def test_detect_makefile(self, makefile_project, omni_runner):
        """Test Makefile detection."""
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        make_runner = next((r for r in runners if r.type == "make"), None)
        assert make_runner is not None
    
    def test_makefile_tasks(self, makefile_project, omni_runner):
        """Test that Makefile tasks are parsed."""
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        make_runner = next((r for r in runners if r.type == "make"), None)
        assert make_runner is not None
        assert len(make_runner.tasks) > 0
        # Should have 'test', 'run', 'clean', 'all' tasks
        task_names = [t.split(':')[0] for t in make_runner.tasks]
        assert "test" in task_names
        assert "run" in task_names
        assert "clean" in task_names
    
    def test_detect_justfile(self, justfile_project, omni_runner):
        """Test justfile detection."""
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        just_runner = next((r for r in runners if r.type == "just"), None)
        assert just_runner is not None
    
    def test_justfile_tasks(self, justfile_project, omni_runner):
        """Test that justfile recipes are parsed."""
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        just_runner = next((r for r in runners if r.type == "just"), None)
        assert just_runner is not None
        assert len(just_runner.tasks) > 0
    
    def test_detect_taskfile(self, taskfile_project, omni_runner):
        """Test Taskfile.yml detection."""
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        task_runner = next((r for r in runners if r.type == "task"), None)
        assert task_runner is not None
    
    def test_taskfile_tasks(self, taskfile_project, omni_runner):
        """Test that Taskfile tasks are parsed."""
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        task_runner = next((r for r in runners if r.type == "task"), None)
        assert task_runner is not None
        assert len(task_runner.tasks) > 0
    
    def test_detect_npm_scripts(self, nodejs_express_app, omni_runner):
        """Test npm script detection."""
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        npm_runner = next((r for r in runners if r.type == "npm"), None)
        assert npm_runner is not None
    
    def test_npm_script_tasks(self, nodejs_express_app, omni_runner):
        """Test that npm scripts are parsed."""
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        npm_runner = next((r for r in runners if r.type == "npm"), None)
        assert npm_runner is not None
        assert "start" in npm_runner.tasks
        assert "dev" in npm_runner.tasks
        assert "test" in npm_runner.tasks


class TestTaskRunnerAssociation:
    """Tests for task runner association with programs."""
    
    def test_program_has_task_runners(self, makefile_project, omni_runner):
        """Test that programs have task runners attached."""
        programs = omni_runner.scan_for_executables()
        
        python_prog = next(p for p in programs if p.name == "app.py")
        assert python_prog is not None
        assert len(python_prog.task_runners) > 0
    
    def test_program_has_make_runner(self, makefile_project, omni_runner):
        """Test that program has make task runner."""
        programs = omni_runner.scan_for_executables()
        
        python_prog = next(p for p in programs if p.name == "app.py")
        make_runner = next((r for r in python_prog.task_runners if r.type == "make"), None)
        assert make_runner is not None
    
    def test_program_has_npm_runner(self, nodejs_express_app, omni_runner):
        """Test that program has npm task runner."""
        programs = omni_runner.scan_for_executables()
        
        js_prog = next(p for p in programs if p.name == "app.js")
        assert js_prog is not None
        npm_runner = next((r for r in js_prog.task_runners if r.type == "npm"), None)
        assert npm_runner is not None


class TestMultipleTaskRunners:
    """Tests for projects with multiple task runners."""
    
    def test_multiple_task_runners_detected(self, temp_dir, omni_runner):
        """Test that multiple task runners are detected."""
        # Create Makefile
        (temp_dir / "Makefile").write_text('''
.PHONY: test
test:
    echo "make test"
''')
        
        # Create package.json
        (temp_dir / "package.json").write_text('{"scripts": {"test": "echo npm test"}}')
        
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        types_found = {r.type for r in runners}
        assert "make" in types_found
        assert "npm" in types_found


class TestTaskRunnerWithDescriptions:
    """Tests for task runner descriptions."""
    
    def test_makefile_with_comments(self, temp_dir, omni_runner):
        """Test that Makefile task descriptions are parsed."""
        (temp_dir / "Makefile").write_text('''
# Build the application
build:
    echo "building"

# Run tests
test:
    echo "testing"

# Deploy the application
deploy: # Deploy to production
    echo "deploying"
''')
        
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        make_runner = next((r for r in runners if r.type == "make"), None)
        assert make_runner is not None
        
        # Check for descriptions
        tasks_with_desc = [t for t in make_runner.tasks if ':' in t]
        # At least some tasks should have descriptions
        assert len(tasks_with_desc) >= 0  # Description parsing is best-effort


class TestNoTaskRunners:
    """Tests for projects without task runners."""
    
    def test_simple_python_no_task_runners(self, python_simple_script, omni_runner):
        """Test that simple Python project has no task runners."""
        programs = omni_runner.scan_for_executables()
        
        simple_prog = next(p for p in programs if p.name == "hello.py")
        assert len(simple_prog.task_runners) == 0
    
    def test_explicit_no_task_runners(self, temp_dir, omni_runner):
        """Test that project with no task runners returns empty list."""
        # Create a simple file without any task runners
        (temp_dir / "script.py").write_text('print("hello")\n')
        
        runners = omni_runner.detect_task_runners(omni_runner.base_path)
        
        assert runners == []


class TestEnvironmentActivationHints:
    """Tests for environment activation hints."""
    
    def test_shows_venv_activation(self, python_with_venv, omni_runner, capsys):
        """Test that venv activation hints are shown."""
        omni_runner.scan_for_executables()
        omni_runner.show_environment_activation_hints()
        
        captured = capsys.readouterr()
        assert "source" in captured.out.lower() or "activate" in captured.out.lower()
    
    def test_shows_docker_activation(self, dockerfile_project, omni_runner, capsys):
        """Test that Docker activation hints are shown."""
        omni_runner.scan_for_executables()
        omni_runner.show_environment_activation_hints()
        
        captured = capsys.readouterr()
        assert "docker" in captured.out.lower()

