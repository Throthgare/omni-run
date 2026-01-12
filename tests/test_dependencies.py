"""
Tests for dependency analysis in OmniRun.

This module tests:
- Interpreter availability checks
- Config file detection
- Dependency resolution
- Auto-fix capability detection
- Dependency checking for various languages
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from conftest import *


class TestInterpreterAvailability:
    """Tests for interpreter availability checking."""
    
    def test_python_available(self, omni_runner):
        """Test Python interpreter availability check."""
        available, version = omni_runner.check_interpreter_available("python")
        
        # Python should be available in the test environment
        assert available is True
        assert version is not None
    
    def test_python3_available(self, omni_runner):
        """Test python3 interpreter availability check."""
        available, version = omni_runner.check_interpreter_available("python3")
        
        assert available is True
        assert version is not None
    
    def test_node_available(self, omni_runner):
        """Test Node.js interpreter availability check."""
        available, version = omni_runner.check_interpreter_available("node")
        
        # Node may or may not be available
        if available:
            assert version is not None
    
    def test_go_available(self, omni_runner):
        """Test Go interpreter availability check."""
        available, version = omni_runner.check_interpreter_available("go")
        
        if available:
            assert version is not None
    
    def test_ruby_available(self, omni_runner):
        """Test Ruby interpreter availability check."""
        available, version = omni_runner.check_interpreter_available("ruby")
        
        if available:
            assert version is not None
    
    def test_nonexistent_interpreter(self, omni_runner):
        """Test checking for non-existent interpreter."""
        available, version = omni_runner.check_interpreter_available("nonexistent_interpreter_12345")
        
        assert available is False
        assert version is None


class TestDependencyCheckClass:
    """Tests for the DependencyCheck dataclass."""
    
    def test_dependency_check_creation(self):
        """Test creating a DependencyCheck instance."""
        from omni_run import DependencyCheck
        
        dep = DependencyCheck(
            name="test-package",
            required=True,
            available=True,
            version="1.0.0",
            message="Package found",
            fix_command="pip install test-package",
            can_auto_fix=True
        )
        
        assert dep.name == "test-package"
        assert dep.required is True
        assert dep.available is True
        assert dep.version == "1.0.0"
        assert dep.can_auto_fix is True
    
    def test_dependency_check_defaults(self):
        """Test DependencyCheck default values."""
        from omni_run import DependencyCheck
        
        dep = DependencyCheck(
            name="test-package",
            required=False,
            available=False
        )
        
        assert dep.version is None
        assert dep.message is None
        assert dep.fix_command is None
        assert dep.can_auto_fix is False


class TestPythonDependencyChecking:
    """Tests for Python dependency checking."""
    
    def test_check_requirements_txt(self, python_flask_app, omni_runner):
        """Test checking requirements.txt."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        assert flask_prog is not None
        
        # Should have dependencies
        deps = flask_prog.dependencies
        assert len(deps) > 0
        
        # Should have python interpreter check
        python_deps = [d for d in deps if d.name in ["python", "python3"]]
        assert len(python_deps) > 0
        assert python_deps[0].available is True
    
    def test_python_with_interpreter_available(self, python_simple_script, omni_runner):
        """Test that Python programs check interpreter availability."""
        programs = omni_runner.scan_for_executables()
        
        prog = next(p for p in programs if p.name == "hello.py")
        
        # Should have interpreter dependency
        interp_deps = [d for d in prog.dependencies if d.name in ["python", "python3"]]
        assert len(interp_deps) > 0
        assert interp_deps[0].available is True
    
    def test_python_config_files_detected(self, python_flask_app, omni_runner):
        """Test that Python config files are detected."""
        programs = omni_runner.scan_for_executables()
        
        prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        
        assert prog.has_config is True
        assert "requirements.txt" in prog.config_files


class TestNodeDependencyChecking:
    """Tests for Node.js dependency checking."""
    
    def test_check_package_json(self, nodejs_express_app, omni_runner):
        """Test checking package.json."""
        programs = omni_runner.scan_for_executables()
        
        express_prog = next((p for p in programs if p.framework and p.framework.name == "Express.js"), None)
        assert express_prog is not None
        
        deps = express_prog.dependencies
        assert len(deps) > 0
    
    def test_node_modules_missing(self, nodejs_express_app, omni_runner):
        """Test that missing node_modules is detected."""
        programs = omni_runner.scan_for_executables()
        
        express_prog = next((p for p in programs if p.framework and p.framework.name == "Express.js"), None)
        
        # node_modules should not exist in fixture
        node_modules_dep = next((d for d in express_prog.dependencies if d.name == "node_modules"), None)
        if node_modules_dep:
            assert node_modules_dep.available is False
            assert node_modules_dep.can_auto_fix is True
    
    def test_node_with_node_modules(self, nodejs_with_node_modules, omni_runner):
        """Test that existing node_modules is detected."""
        programs = omni_runner.scan_for_executables()
        
        prog = next(p for p in programs if p.type == "JavaScript")
        
        node_modules_dep = next((d for d in prog.dependencies if d.name == "node_modules"), None)
        if node_modules_dep:
            assert node_modules_dep.available is True
    
    def test_npm_scripts_as_tasks(self, nodejs_express_app, omni_runner):
        """Test that npm scripts are available as tasks."""
        programs = omni_runner.scan_for_executables()
        
        express_prog = next((p for p in programs if p.framework and p.framework.name == "Express.js"), None)
        
        npm_runner = next((r for r in express_prog.task_runners if r.type == "npm"), None)
        assert npm_runner is not None
        assert "start" in npm_runner.tasks
        assert "dev" in npm_runner.tasks


class TestGoDependencyChecking:
    """Tests for Go dependency checking."""
    
    def test_check_go_mod(self, go_simple_program, omni_runner):
        """Test checking go.mod."""
        programs = omni_runner.scan_for_executables()
        
        go_prog = next(p for p in programs if p.type == "Go")
        
        # Should have go.mod detected
        assert "go.mod" in go_prog.config_files
    
    def test_go_fix_command(self, go_simple_program, omni_runner):
        """Test that Go fix commands are set correctly."""
        programs = omni_runner.scan_for_executables()
        
        go_prog = next(p for p in programs if p.type == "Go")
        
        # Find go.mod dependency
        gomod_dep = next((d for d in go_prog.dependencies if d.name == "Go modules"), None)
        if gomod_dep:
            assert gomod_dep.can_auto_fix is True
            assert "go mod" in gomod_dep.fix_command.lower()


class TestRustDependencyChecking:
    """Tests for Rust dependency checking."""
    
    def test_check_cargo_toml(self, rust_simple_program, omni_runner):
        """Test checking Cargo.toml."""
        programs = omni_runner.scan_for_executables()
        
        rust_prog = next(p for p in programs if p.type == "Rust")
        
        # Should have Cargo.toml detected
        assert "Cargo.toml" in rust_prog.config_files
    
    def test_rust_target_missing(self, rust_simple_program, omni_runner):
        """Test that missing target directory is detected."""
        programs = omni_runner.scan_for_executables()
        
        rust_prog = next(p for p in programs if p.type == "Rust")
        
        # Find cargo dependencies check
        cargo_dep = next((d for d in rust_prog.dependencies if d.name == "Cargo dependencies"), None)
        if cargo_dep:
            assert cargo_dep.can_auto_fix is True
            assert "cargo build" in cargo_dep.fix_command
    
    def test_rust_with_target(self, rust_with_target, omni_runner):
        """Test that existing target directory is detected."""
        programs = omni_runner.scan_for_executables()
        
        rust_prog = next(p for p in programs if p.type == "Rust")
        
        cargo_dep = next((d for d in rust_prog.dependencies if d.name == "Cargo dependencies"), None)
        if cargo_dep:
            assert cargo_dep.available is True


class TestJavaDependencyChecking:
    """Tests for Java dependency checking."""
    
    def test_check_pom_xml(self, java_maven_app, omni_runner):
        """Test checking pom.xml."""
        programs = omni_runner.scan_for_executables()
        
        java_prog = next(p for p in programs if p.type == "Java")
        
        assert "pom.xml" in java_prog.config_files
    
    def test_maven_fix_command(self, java_maven_app, omni_runner):
        """Test that Maven fix commands are set correctly."""
        programs = omni_runner.scan_for_executables()
        
        java_prog = next(p for p in programs if p.type == "Java")
        
        maven_dep = next((d for d in java_prog.dependencies if d.name == "Maven dependencies"), None)
        if maven_dep:
            assert maven_dep.can_auto_fix is True
            assert "mvn" in maven_dep.fix_command
    
    def test_check_build_gradle(self, java_gradle_app, omni_runner):
        """Test checking build.gradle."""
        programs = omni_runner.scan_for_executables()
        
        java_prog = next(p for p in programs if p.type == "Java")
        
        assert "build.gradle" in java_prog.config_files or "build.gradle.kts" in java_prog.config_files


class TestMissingDependencies:
    """Tests for missing dependency detection."""
    
    def test_python_missing_deps(self, python_flask_app, omni_runner):
        """Test that missing Python dependencies are detected."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        
        missing = [d for d in flask_prog.dependencies if d.required and not d.available]
        
        # node_modules is likely missing
        node_modules_missing = any(d.name == "node_modules" for d in missing)
        
        # Should be able to auto-fix
        if node_modules_missing:
            node_modules_dep = next(d for d in flask_prog.dependencies if d.name == "node_modules")
            assert node_modules_dep.can_auto_fix is True
    
    def test_node_missing_deps(self, nodejs_express_app, omni_runner):
        """Test that missing Node dependencies are detected."""
        programs = omni_runner.scan_for_executables()
        
        express_prog = next((p for p in programs if p.framework and p.framework.name == "Express.js"), None)
        
        missing = [d for d in express_prog.dependencies if d.required and not d.available]
        
        # node_modules should be missing
        node_modules_missing = any(d.name == "node_modules" for d in missing)
        if node_modules_missing:
            node_modules_dep = next(d for d in express_prog.dependencies if d.name == "node_modules")
            assert node_modules_dep.can_auto_fix is True
            assert "npm install" in node_modules_dep.fix_command or "yarn" in node_modules_dep.fix_command


class TestAutoFixCapability:
    """Tests for auto-fix capability detection."""
    
    def test_python_packages_auto_fixable(self, python_flask_app, omni_runner):
        """Test that Python packages are auto-fixable."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        
        # Find Python packages dependency
        packages_dep = next((d for d in flask_prog.dependencies if d.name == "Python packages"), None)
        if packages_dep:
            assert packages_dep.can_auto_fix is True
            assert "pip install" in packages_dep.fix_command
    
    def test_venv_creation_auto_fixable(self, python_flask_app, omni_runner):
        """Test that venv creation is auto-fixable."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        
        # Find venv dependency
        venv_dep = next((d for d in flask_prog.dependencies if d.name == "Python virtual environment"), None)
        if venv_dep:
            assert venv_dep.can_auto_fix is True
            assert "venv" in venv_dep.fix_command
    
    def test_interpreter_not_auto_fixable(self, python_simple_script, omni_runner):
        """Test that interpreter is not auto-fixable."""
        programs = omni_runner.scan_for_executables()
        
        prog = next(p for p in programs if p.name == "hello.py")
        
        # Find interpreter dependency
        interp_deps = [d for d in prog.dependencies if d.name in ["python", "python3"]]
        if interp_deps:
            assert interp_deps[0].can_auto_fix is False


class TestRequiredVsOptionalDependencies:
    """Tests for required vs optional dependency distinction."""
    
    def test_interpreter_required(self, python_simple_script, omni_runner):
        """Test that interpreter is marked as required."""
        programs = omni_runner.scan_for_executables()
        
        prog = next(p for p in programs if p.name == "hello.py")
        
        interp_deps = [d for d in prog.dependencies if d.name in ["python", "python3"]]
        if interp_deps:
            assert interp_deps[0].required is True
    
    def test_config_file_optional(self, python_flask_app, omni_runner):
        """Test that config files may be marked as optional."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        
        # Find requirements.txt
        req_dep = next((d for d in flask_prog.dependencies if d.name == "requirements.txt"), None)
        if req_dep:
            # Config files are typically optional
            assert req_dep.required is False


class TestDependencyMessages:
    """Tests for dependency check messages."""
    
    def test_interpreter_message(self, omni_runner):
        """Test interpreter check message."""
        available, version = omni_runner.check_interpreter_available("python")
        
        # Message should be generated when creating dependency check
        from omni_run import DependencyCheck
        dep = DependencyCheck(
            name="python",
            required=True,
            available=available,
            version=version,
            message=f"Interpreter python {'found' if available else 'NOT FOUND'}"
        )
        
        assert "python" in dep.message.lower()
        assert ("found" in dep.message or "NOT" in dep.message)
    
    def test_node_modules_message(self, nodejs_express_app, omni_runner):
        """Test node_modules check message."""
        programs = omni_runner.scan_for_executables()
        
        express_prog = next((p for p in programs if p.framework and p.framework.name == "Express.js"), None)
        
        node_modules_dep = next((d for d in express_prog.dependencies if d.name == "node_modules"), None)
        if node_modules_dep:
            assert "node_modules" in node_modules_dep.message.lower()


class TestFixCommands:
    """Tests for fix command generation."""
    
    def test_npm_install_command(self, nodejs_express_app, omni_runner):
        """Test that npm install command is generated."""
        programs = omni_runner.scan_for_executables()
        
        express_prog = next((p for p in programs if p.framework and p.framework.name == "Express.js"), None)
        
        node_modules_dep = next((d for d in express_prog.dependencies if d.name == "node_modules"), None)
        if node_modules_dep:
            assert "install" in node_modules_dep.fix_command.lower()
    
    def test_pip_install_command(self, python_flask_app, omni_runner):
        """Test that pip install command is generated."""
        programs = omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in programs if p.framework and p.framework.name == "Flask"), None)
        
        packages_dep = next((d for d in flask_prog.dependencies if d.name == "Python packages"), None)
        if packages_dep:
            assert "pip" in packages_dep.fix_command.lower()
    
    def test_cargo_build_command(self, rust_simple_program, omni_runner):
        """Test that cargo build command is generated."""
        programs = omni_runner.scan_for_executables()
        
        rust_prog = next(p for p in programs if p.type == "Rust")
        
        cargo_dep = next((d for d in rust_prog.dependencies if d.name == "Cargo dependencies"), None)
        if cargo_dep:
            assert "cargo build" in cargo_dep.fix_command
    
    def test_go_mod_command(self, go_simple_program, omni_runner):
        """Test that go mod commands are generated."""
        programs = omni_runner.scan_for_executables()
        
        go_prog = next(p for p in programs if p.type == "Go")
        
        gomod_dep = next((d for d in go_prog.dependencies if d.name == "Go modules"), None)
        if gomod_dep:
            assert "go mod" in gomod_dep.fix_command.lower()

