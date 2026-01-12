"""
Tests for framework detection in OmniRun.

This module tests:
- Django detection
- Flask detection
- FastAPI detection
- React detection
- Next.js detection
- Express detection
- Gin/Echo detection
- Actix/Rocket detection
- Spring Boot detection
- Rails detection
- Laravel detection
"""

import os
import pytest
from pathlib import Path

from conftest import *


class TestPythonFrameworkDetection:
    """Tests for Python framework detection."""
    
    def test_detect_flask(self, python_flask_app, omni_runner):
        """Test Flask framework detection."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        assert flask_prog is not None
        assert flask_prog.framework.name == "Flask"
    
    def test_flask_commands(self, python_flask_app, omni_runner):
        """Test that Flask framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        assert flask_prog is not None
        
        commands = flask_prog.framework.commands
        assert "run" in commands
        assert "test" in commands
    
    def test_detect_django(self, python_django_app, omni_runner):
        """Test Django framework detection."""
        programs = omni_runner.scan_for_executables()
        
        django_prog = next((p for p in programs if p.framework and p.framework.name == "Django"), None)
        assert django_prog is not None
        assert django_prog.framework.name == "Django"
    
    def test_django_commands(self, python_django_app, omni_runner):
        """Test that Django framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        django_prog = next((p for p in programs if p.framework and p.framework.name == "Django"), None)
        assert django_prog is not None
        
        commands = django_prog.framework.commands
        assert "runserver" in commands
        assert "migrate" in commands
        assert "shell" in commands
        assert "test" in commands
    
    def test_detect_fastapi(self, python_fastapi_app, omni_runner):
        """Test FastAPI framework detection."""
        programs = omni_runner.scan_for_executables()
        
        fastapi_prog = next((p for p in programs if p.framework and p.framework.name == "FastAPI"), None)
        assert fastapi_prog is not None
        assert fastapi_prog.framework.name == "FastAPI"
    
    def test_fastapi_commands(self, python_fastapi_app, omni_runner):
        """Test that FastAPI framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        fastapi_prog = next((p for p in programs if p.framework and p.framework.name == "FastAPI"), None)
        assert fastapi_prog is not None
        
        commands = fastapi_prog.framework.commands
        assert "run" in commands
        assert "test" in commands


class TestJavaScriptFrameworkDetection:
    """Tests for JavaScript/TypeScript framework detection."""
    
    def test_detect_express(self, nodejs_express_app, omni_runner):
        """Test Express.js framework detection."""
        programs = omni_runner.scan_for_executables()
        
        express_prog = next((p for p in programs if p.framework and p.framework.name == "Express.js"), None)
        assert express_prog is not None
        assert express_prog.framework.name == "Express.js"
    
    def test_express_commands(self, nodejs_express_app, omni_runner):
        """Test that Express.js framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        express_prog = next((p for p in programs if p.framework and p.framework.name == "Express.js"), None)
        assert express_prog is not None
        
        commands = express_prog.framework.commands
        assert "start" in commands
        assert "dev" in commands
    
    def test_detect_react(self, nodejs_react_app, omni_runner):
        """Test React framework detection."""
        programs = omni_runner.scan_for_executables()
        
        react_prog = next((p for p in programs if p.framework and p.framework.name == "React"), None)
        assert react_prog is not None
        assert react_prog.framework.name == "React"
    
    def test_react_commands(self, nodejs_react_app, omni_runner):
        """Test that React framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        react_prog = next((p for p in programs if p.framework and p.framework.name == "React"), None)
        assert react_prog is not None
        
        commands = react_prog.framework.commands
        assert "start" in commands
        assert "build" in commands
        assert "test" in commands
    
    def test_detect_nextjs(self, nodejs_nextjs_app, omni_runner):
        """Test Next.js framework detection."""
        programs = omni_runner.scan_for_executables()
        
        nextjs_prog = next((p for p in programs if p.framework and p.framework.name == "Next.js"), None)
        assert nextjs_prog is not None
        assert nextjs_prog.framework.name == "Next.js"
    
    def test_nextjs_commands(self, nodejs_nextjs_app, omni_runner):
        """Test that Next.js framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        nextjs_prog = next((p for p in programs if p.framework and p.framework.name == "Next.js"), None)
        assert nextjs_prog is not None
        
        commands = nextjs_prog.framework.commands
        assert "dev" in commands
        assert "build" in commands
        assert "start" in commands


class TestGoFrameworkDetection:
    """Tests for Go framework detection."""
    
    def test_detect_gin(self, go_gin_app, omni_runner):
        """Test Gin framework detection."""
        programs = omni_runner.scan_for_executables()
        
        gin_prog = next((p for p in programs if p.framework and p.framework.name == "Gin"), None)
        assert gin_prog is not None
        assert gin_prog.framework.name == "Gin"
    
    def test_gin_commands(self, go_gin_app, omni_runner):
        """Test that Gin framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        gin_prog = next((p for p in programs if p.framework and p.framework.name == "Gin"), None)
        assert gin_prog is not None
        
        commands = gin_prog.framework.commands
        assert "run" in commands
        assert "build" in commands
        assert "test" in commands
    
    def test_detect_echo(self, go_echo_app, omni_runner):
        """Test Echo framework detection."""
        programs = omni_runner.scan_for_executables()
        
        echo_prog = next((p for p in programs if p.framework and p.framework.name == "Echo"), None)
        assert echo_prog is not None
        assert echo_prog.framework.name == "Echo"
    
    def test_echo_commands(self, go_echo_app, omni_runner):
        """Test that Echo framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        echo_prog = next((p for p in programs if p.framework and p.framework.name == "Echo"), None)
        assert echo_prog is not None
        
        commands = echo_prog.framework.commands
        assert "run" in commands
        assert "build" in commands
        assert "test" in commands


class TestRustFrameworkDetection:
    """Tests for Rust framework detection."""
    
    def test_detect_actix(self, rust_actix_app, omni_runner):
        """Test Actix framework detection."""
        programs = omni_runner.scan_for_executables()
        
        actix_prog = next((p for p in programs if p.framework and p.framework.name == "Actix"), None)
        assert actix_prog is not None
        assert actix_prog.framework.name == "Actix"
    
    def test_actix_commands(self, rust_actix_app, omni_runner):
        """Test that Actix framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        actix_prog = next((p for p in programs if p.framework and p.framework.name == "Actix"), None)
        assert actix_prog is not None
        
        commands = actix_prog.framework.commands
        assert "run" in commands
        assert "build" in commands
        assert "test" in commands
    
    def test_detect_rocket(self, rust_rocket_app, omni_runner):
        """Test Rocket framework detection."""
        programs = omni_runner.scan_for_executables()
        
        rocket_prog = next((p for p in programs if p.framework and p.framework.name == "Rocket"), None)
        assert rocket_prog is not None
        assert rocket_prog.framework.name == "Rocket"
    
    def test_rocket_commands(self, rust_rocket_app, omni_runner):
        """Test that Rocket framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        rocket_prog = next((p for p in programs if p.framework and p.framework.name == "Rocket"), None)
        assert rocket_prog is not None
        
        commands = rocket_prog.framework.commands
        assert "run" in commands
        assert "build" in commands
        assert "test" in commands


class TestJavaFrameworkDetection:
    """Tests for Java framework detection."""
    
    def test_detect_spring_boot(self, java_spring_boot_app, omni_runner):
        """Test Spring Boot framework detection."""
        programs = omni_runner.scan_for_executables()
        
        spring_prog = next((p for p in programs if p.framework and p.framework.name == "Spring Boot"), None)
        assert spring_prog is not None
        assert spring_prog.framework.name == "Spring Boot"
    
    def test_spring_boot_commands(self, java_spring_boot_app, omni_runner):
        """Test that Spring Boot framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        spring_prog = next((p for p in programs if p.framework and p.framework.name == "Spring Boot"), None)
        assert spring_prog is not None
        
        commands = spring_prog.framework.commands
        assert "run" in commands
        assert "test" in commands


class TestRubyFrameworkDetection:
    """Tests for Ruby framework detection."""
    
    def test_detect_rails(self, ruby_rails_app, omni_runner):
        """Test Ruby on Rails framework detection."""
        programs = omni_runner.scan_for_executables()
        
        rails_prog = next((p for p in programs if p.framework and p.framework.name == "Ruby on Rails"), None)
        assert rails_prog is not None
        assert rails_prog.framework.name == "Ruby on Rails"
    
    def test_rails_commands(self, ruby_rails_app, omni_runner):
        """Test that Rails framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        rails_prog = next((p for p in programs if p.framework and p.framework.name == "Ruby on Rails"), None)
        assert rails_prog is not None
        
        commands = rails_prog.framework.commands
        assert "server" in commands
        assert "console" in commands
        assert "test" in commands


class TestPHPFrameworkDetection:
    """Tests for PHP framework detection."""
    
    def test_detect_laravel(self, php_laravel_app, omni_runner):
        """Test Laravel framework detection."""
        programs = omni_runner.scan_for_executables()
        
        laravel_prog = next((p for p in programs if p.framework and p.framework.name == "Laravel"), None)
        assert laravel_prog is not None
        assert laravel_prog.framework.name == "Laravel"
    
    def test_laravel_commands(self, php_laravel_app, omni_runner):
        """Test that Laravel framework has correct commands."""
        programs = omni_runner.scan_for_executables()
        
        laravel_prog = next((p for p in programs if p.framework and p.framework.name == "Laravel"), None)
        assert laravel_prog is not None
        
        commands = laravel_prog.framework.commands
        assert "serve" in commands
        assert "test" in commands


class TestNoFramework:
    """Tests for projects without frameworks."""
    
    def test_simple_python_no_framework(self, python_simple_script, omni_runner):
        """Test that simple Python script has no framework."""
        programs = omni_runner.scan_for_executables()
        
        simple_prog = next(p for p in programs if p.name == "hello.py")
        assert simple_prog.framework is None
    
    def test_simple_node_no_framework(self, nodejs_simple_script, omni_runner):
        """Test that simple Node.js script has no framework."""
        programs = omni_runner.scan_for_executables()
        
        simple_prog = next(p for p in programs if p.name == "server.js")
        assert simple_prog.framework is None
    
    def test_simple_go_no_framework(self, go_simple_program, omni_runner):
        """Test that simple Go program has no framework."""
        programs = omni_runner.scan_for_executables()
        
        simple_prog = next(p for p in programs if p.name == "main.go")
        assert simple_prog.framework is None


class TestFrameworkEntryPoint:
    """Tests for framework entry point detection."""
    
    def test_flask_entry_point(self, python_flask_app, omni_runner):
        """Test that Flask entry point is set correctly."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        assert flask_prog is not None
        assert flask_prog.framework.entry_point is not None
        assert flask_prog.framework.entry_point.name == "app.py"
    
    def test_django_entry_point(self, python_django_app, omni_runner):
        """Test that Django entry point is set correctly."""
        programs = omni_runner.scan_for_executables()
        
        django_prog = next((p for p in programs if p.framework and p.framework.name == "Django"), None)
        assert django_prog is not None
        assert django_prog.framework.entry_point is not None
        assert django_prog.framework.entry_point.name == "manage.py"


class TestFrameworkVersion:
    """Tests for framework version detection."""
    
    def test_nextjs_version(self, nodejs_nextjs_app, omni_runner):
        """Test that Next.js version is detected from package.json."""
        programs = omni_runner.scan_for_executables()
        
        nextjs_prog = next((p for p in programs if p.framework and p.framework.name == "Next.js"), None)
        assert nextjs_prog is not None
        assert nextjs_prog.framework.version is not None
        # Version should be something like ^13.0.0
        assert nextjs_prog.framework.version.startswith("^13")


class TestMultipleFrameworks:
    """Tests for projects with multiple potential frameworks."""
    
    def test_flask_over_generic_python(self, python_flask_app, omni_runner):
        """Test that Flask is detected instead of generic Python."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        assert flask_prog is not None
        # Should have Flask-specific commands
        assert "run" in flask_prog.framework.commands


class TestFrameworkInNestedDirectory:
    """Tests for framework detection in nested directories."""
    
    def test_nested_flask_app(self, temp_dir, omni_runner):
        """Test Flask detection in nested directory."""
        # Create Flask app in subdirectory
        app_dir = temp_dir / "backend"
        app_dir.mkdir()
        
        (app_dir / "app.py").write_text('''
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "API"
''')
        
        (app_dir / "requirements.txt").write_text("flask>=2.0.0\n")
        
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        assert flask_prog is not None
        assert "backend" in flask_prog.relative_path

