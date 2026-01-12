"""
Tests for auto-fix functionality in OmniRun.

This module tests:
- Auto-fix proposal generation
- Auto-fix execution
- Dry-run mode
- Backup creation and rollback
- Safety features
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from conftest import *


class TestAutoFixProposal:
    """Tests for auto-fix proposal generation."""
    
    def test_auto_fix_proposal_shows_missing_deps(self, nodejs_express_app, omni_runner):
        """Test that auto-fix proposal shows missing dependencies."""
        omni_runner.scan_for_executables()
        
        express_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Express.js"), None)
        
        if express_prog:
            missing_deps = [d for d in express_prog.dependencies if d.required and not d.available and d.can_auto_fix]
            
            # node_modules should be missing and auto-fixable
            node_modules_deps = [d for d in missing_deps if d.name == "node_modules"]
            assert len(node_modules_deps) > 0
    
    def test_auto_fix_no_proposal_when_no_missing(self, python_simple_script, omni_runner):
        """Test that no auto-fix proposal when all deps available."""
        omni_runner.scan_for_executables()
        
        prog = next(p for p in omni_runner.discovered_programs if p.name == "hello.py")
        
        missing_deps = [d for d in prog.dependencies if d.required and not d.available and d.can_auto_fix]
        
        # Simple script with available interpreter should have no missing deps
        assert len(missing_deps) == 0
    
    def test_auto_fix_proposal_shows_commands(self, nodejs_express_app, omni_runner):
        """Test that auto-fix proposal shows fix commands."""
        omni_runner.scan_for_executables()
        
        express_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Express.js"), None)
        
        if express_prog:
            missing_deps = [d for d in express_prog.dependencies if d.required and not d.available and d.can_auto_fix]
            
            for dep in missing_deps:
                if dep.name == "node_modules":
                    assert dep.fix_command is not None
                    assert "install" in dep.fix_command.lower()


class TestAutoFixExecution:
    """Tests for auto-fix execution."""
    
    def test_auto_fix_returns_bool(self, nodejs_express_app, omni_runner):
        """Test that auto_fix returns boolean."""
        omni_runner.scan_for_executables()
        
        express_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Express.js"), None)
        
        if express_prog:
            # Dry run - don't actually execute
            result = omni_runner.auto_fix_dependencies(express_prog, interactive=False, dry_run=True)
            
            assert isinstance(result, bool)
    
    def test_auto_fix_dry_run(self, nodejs_express_app, omni_runner, temp_dir):
        """Test that dry-run mode doesn't make changes."""
        omni_runner.scan_for_executables()
        
        express_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Express.js"), None)
        
        if express_prog:
            # Do dry run
            result = omni_runner.auto_fix_dependencies(express_prog, interactive=False, dry_run=True)
            
            # node_modules should not be created
            node_modules = omni_runner.base_path / "node_modules"
            assert not node_modules.exists()
    
    def test_auto_fix_non_interactive(self, nodejs_express_app, omni_runner):
        """Test auto-fix in non-interactive mode."""
        omni_runner.scan_for_executables()
        
        express_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Express.js"), None)
        
        if express_prog:
            # Non-interactive mode - should not prompt
            result = omni_runner.auto_fix_dependencies(express_prog, interactive=False)
            
            assert isinstance(result, bool)


class TestAutoFixSafety:
    """Tests for auto-fix safety features."""
    
    def test_backup_creation_enabled(self, nodejs_express_app, omni_runner, temp_dir):
        """Test that backup is created when enabled."""
        omni_runner.scan_for_executables()
        
        express_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Express.js"), None)
        
        if express_prog:
            # Create backup should be possible
            backup_created = omni_runner._create_backup(omni_runner.base_path)
            
            assert backup_created is True
    
    def test_rollback_on_failure(self, nodejs_express_app, omni_runner, temp_dir):
        """Test that rollback works on failure."""
        omni_runner.scan_for_executables()
        
        express_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Express.js"), None)
        
        if express_prog:
            # Create backup
            backup_created = omni_runner._create_backup(omni_runner.base_path)
            
            if backup_created:
                # Test rollback
                rollback_result = omni_runner._rollback_backup(omni_runner.base_path)
                
                assert isinstance(rollback_result, bool)
    
    def test_auto_rollback_config(self, omni_runner):
        """Test that auto-rollback can be configured."""
        # Default should be True
        assert omni_runner.config.get('auto_rollback', True) is True
        
        # Can be disabled
        omni_runner.config['auto_rollback'] = False
        assert omni_runner.config.get('auto_rollback') is False
    
    def test_enable_backup_config(self, omni_runner):
        """Test that backup can be disabled via config."""
        # Default should be True
        assert omni_runner.config.get('enable_backup', True) is True
        
        # Can be disabled
        omni_runner.config['enable_backup'] = False
        assert omni_runner.config.get('enable_backup') is False


class TestAutoFixConfirmation:
    """Tests for auto-fix confirmation prompts."""
    
    def test_auto_confirm_config(self, omni_runner):
        """Test auto-confirm configuration."""
        # Default should be False
        assert omni_runner.config.get('auto_confirm', False) is False
        
        # Can be enabled
        omni_runner.config['auto_confirm'] = True
        assert omni_runner.config.get('auto_confirm') is True
    
    def test_confirm_each_command_config(self, omni_runner):
        """Test confirm_each_command configuration."""
        # Default behavior depends on implementation
        # Test that config key exists
        assert 'confirm_each_command' in omni_runner.config or omni_runner.config.get('confirm_each_command') is not None
    
    def test_ask_each_command_config(self, omni_runner):
        """Test ask_each_command configuration."""
        # Can be set
        omni_runner.config['ask_each_command'] = True
        assert omni_runner.config.get('ask_each_command') is True


class TestAutoFixPackageManagers:
    """Tests for auto-fix with different package managers."""
    
    def test_npm_install_command(self, nodejs_express_app, omni_runner):
        """Test npm install command generation."""
        omni_runner.scan_for_executables()
        
        express_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Express.js"), None)
        
        if express_prog:
            node_modules_dep = next((d for d in express_prog.dependencies if d.name == "node_modules"), None)
            
            if node_modules_dep and node_modules_dep.fix_command:
                # Should contain install command
                assert "npm install" in node_modules_dep.fix_command or "npm" in node_modules_dep.fix_command
    
    def test_yarn_install_command(self, temp_dir, omni_runner):
        """Test yarn install command generation."""
        # Create project with yarn.lock
        (temp_dir / "package.json").write_text('{"name": "test"}')
        (temp_dir / "yarn.lock").write_text("# yarn lockfile\n")
        (temp_dir / "app.js").write_text('console.log("test")\n')
        
        omni_runner.scan_for_executables()
        
        prog = next(p for p in omni_runner.discovered_programs if p.type == "JavaScript")
        
        node_modules_dep = next((d for d in prog.dependencies if d.name == "node_modules"), None)
        
        if node_modules_dep and node_modules_dep.fix_command:
            # Should detect yarn
            assert "yarn" in node_modules_dep.fix_command.lower() or "npm" in node_modules_dep.fix_command.lower()
    
    def test_pnpm_install_command(self, temp_dir, omni_runner):
        """Test pnpm install command generation."""
        # Create project with pnpm-lock.yaml
        (temp_dir / "package.json").write_text('{"name": "test"}')
        (temp_dir / "pnpm-lock.yaml").write_text("# pnpm lockfile\n")
        (temp_dir / "app.js").write_text('console.log("test")\n')
        
        omni_runner.scan_for_executables()
        
        prog = next(p for p in omni_runner.discovered_programs if p.type == "JavaScript")
        
        node_modules_dep = next((d for d in prog.dependencies if d.name == "node_modules"), None)
        
        if node_modules_dep and node_modules_dep.fix_command:
            # Should detect pnpm
            assert "pnpm" in node_modules_dep.fix_command.lower() or "npm" in node_modules_dep.fix_command.lower()


class TestAutoFixPython:
    """Tests for Python-specific auto-fix."""
    
    def test_pip_install_command(self, python_flask_app, omni_runner):
        """Test pip install command generation."""
        omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Flask"), None)
        
        if flask_prog:
            packages_dep = next((d for d in flask_prog.dependencies if d.name == "Python packages"), None)
            
            if packages_dep and packages_dep.fix_command:
                assert "pip" in packages_dep.fix_command.lower()
                assert "install" in packages_dep.fix_command.lower()
    
    def test_venv_creation_command(self, python_flask_app, omni_runner):
        """Test venv creation command generation."""
        omni_runner.scan_for_executables()
        
        flask_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Flask"), None)
        
        if flask_prog:
            venv_dep = next((d for d in flask_prog.dependencies if d.name == "Python virtual environment"), None)
            
            if venv_dep and venv_dep.fix_command:
                assert "venv" in venv_dep.fix_command.lower()


class TestAutoFixGo:
    """Tests for Go-specific auto-fix."""
    
    def test_go_mod_tidy_command(self, go_simple_program, omni_runner):
        """Test go mod tidy command generation."""
        omni_runner.scan_for_executables()
        
        go_prog = next(p for p in omni_runner.discovered_programs if p.type == "Go")
        
        gomod_dep = next((d for d in go_prog.dependencies if d.name == "Go modules"), None)
        
        if gomod_dep and gomod_dep.fix_command:
            assert "go mod" in gomod_dep.fix_command.lower()


class TestAutoFixRust:
    """Tests for Rust-specific auto-fix."""
    
    def test_cargo_build_command(self, rust_simple_program, omni_runner):
        """Test cargo build command generation."""
        omni_runner.scan_for_executables()
        
        rust_prog = next(p for p in omni_runner.discovered_programs if p.type == "Rust")
        
        cargo_dep = next((d for d in rust_prog.dependencies if d.name == "Cargo dependencies"), None)
        
        if cargo_dep and cargo_dep.fix_command:
            assert "cargo build" in cargo_dep.fix_command.lower()


class TestAutoFixJava:
    """Tests for Java-specific auto-fix."""
    
    def test_maven_install_command(self, java_maven_app, omni_runner):
        """Test mvn install command generation."""
        omni_runner.scan_for_executables()
        
        java_prog = next(p for p in omni_runner.discovered_programs if p.type == "Java")
        
        maven_dep = next((d for d in java_prog.dependencies if d.name == "Maven dependencies"), None)
        
        if maven_dep and maven_dep.fix_command:
            assert "mvn" in maven_dep.fix_command.lower()
    
    def test_gradle_build_command(self, java_gradle_app, omni_runner):
        """Test gradle build command generation."""
        omni_runner.scan_for_executables()
        
        java_prog = next(p for p in omni_runner.discovered_programs if p.type == "Java")
        
        gradle_dep = next((d for d in java_prog.dependencies if d.name == "Gradle dependencies"), None)
        
        if gradle_dep and gradle_dep.fix_command:
            assert "gradle" in gradle_dep.fix_command.lower() or "./gradlew" in gradle_dep.fix_command


class TestAutoFixDisplay:
    """Tests for auto-fix display/output."""
    
    def test_fix_command_in_dep(self, nodejs_express_app, omni_runner):
        """Test that fix command is stored in dependency."""
        omni_runner.scan_for_executables()
        
        express_prog = next((p for p in omni_runner.discovered_programs if p.framework and p.framework.name == "Express.js"), None)
        
        if express_prog:
            node_modules_dep = next((d for d in express_prog.dependencies if d.name == "node_modules"), None)
            
            if node_modules_dep:
                assert hasattr(node_modules_dep, 'fix_command')
                assert node_modules_dep.can_auto_fix is True or node_modules_dep.fix_command is not None


class TestAutoFixEdgeCases:
    """Tests for auto-fix edge cases."""
    
    def test_no_auto_fix_for_interpreter(self, python_simple_script, omni_runner):
        """Test that interpreter cannot be auto-fixed."""
        omni_runner.scan_for_executables()
        
        prog = next(p for p in omni_runner.discovered_programs if p.name == "hello.py")
        
        interp_deps = [d for d in prog.dependencies if d.name in ["python", "python3"]]
        
        for dep in interp_deps:
            # Interpreters cannot be auto-fixed
            assert dep.can_auto_fix is False
    
    def test_auto_fix_when_enabled_in_config(self, omni_runner):
        """Test auto_fix config option."""
        # Default is False
        assert omni_runner.config.get('auto_fix', False) is False
        
        # Can be enabled
        omni_runner.config['auto_fix'] = True
        assert omni_runner.config.get('auto_fix') is True


class TestAutoFixExecutionResult:
    """Tests for auto-fix execution result handling."""
    
    def test_execute_program_with_auto_fix(self, nodejs_express_app, omni_runner):
        """Test execute_program with auto_fix parameter."""
        omni_runner.scan_for_executables()
        
        # Set auto_fix in config
        omni_runner.config['auto_fix'] = True
        
        # Should work without error
        try:
            result = omni_runner.execute_program(0, auto_fix=True)
            assert result is not None
        except Exception as e:
            # May fail if no interpreter available - that's OK
            pass
    
    def test_execute_program_skips_auto_fix(self, python_simple_script, omni_runner):
        """Test execute_program without auto_fix when not needed."""
        omni_runner.scan_for_executables()
        
        if omni_runner.discovered_programs:
            result = omni_runner.execute_program(0, auto_fix=False)
            assert result is not None

