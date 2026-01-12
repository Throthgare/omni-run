"""
Tests for core discovery functionality in OmniRun.

This module tests:
- File scanning and detection
- Language identification
- Framework detection
- Environment detection
- Task runner detection
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import fixtures
from conftest import *


class TestFileScanning:
    """Tests for file scanning functionality."""
    
    def test_scan_empty_directory(self, empty_directory, omni_runner):
        """Test scanning an empty directory."""
        programs = omni_runner.scan_for_executables()
        assert programs == []
    
    def test_scan_single_python_file(self, python_simple_script, omni_runner):
        """Test scanning a single Python file."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "Python"
        assert programs[0].name == "hello.py"
    
    def test_scan_python_main_file(self, python_main_pattern, omni_runner):
        """Test scanning a Python file with main pattern."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "Python"
        # Main pattern files should have higher score
        assert programs[0].score > 0
    
    def test_scan_multiple_files(self, mixed_extensions, omni_runner):
        """Test scanning multiple files with different extensions."""
        programs = omni_runner.scan_for_executables()
        
        # Should find .py, .js, .ts, .go, .rs files
        types_found = {prog.type for prog in programs}
        
        assert "Python" in types_found
        assert "JavaScript" in types_found
        assert "TypeScript" in types_found
        assert "Go" in types_found
        assert "Rust" in types_found
    
    def test_scan_nested_directories(self, deep_directory_structure, omni_runner):
        """Test scanning nested directory structure."""
        programs = omni_runner.scan_for_executables()
        
        # Should find files at all levels
        assert len(programs) > 0
        # All should be Python files
        for prog in programs:
            assert prog.type == "Python"
    
    def test_max_depth_limit(self, deep_directory_structure, omni_runner):
        """Test that max_depth limits scanning."""
        programs = omni_runner.scan_for_executables(max_depth=3)
        
        # Should only find files up to depth 3
        for prog in programs:
            depth = len(prog.path.relative_to(omni_runner.base_path).parts) - 1
            assert depth <= 3
    
    def test_exclude_directories(self, temp_dir, omni_runner):
        """Test that excluded directories are not scanned."""
        # Create files in regular and excluded directories
        (temp_dir / "main.py").write_text("print('main')")
        
        excluded = temp_dir / "node_modules"
        excluded.mkdir()
        (excluded / "dep.js").write_text("console.log('dep')")
        
        programs = omni_runner.scan_for_executables()
        
        # Should find main.py but not dep.js
        assert any(p.name == "main.py" for p in programs)
        assert not any("node_modules" in str(p.path) for p in programs)
    
    def test_hidden_directories_skipped(self, hidden_directory, omni_runner):
        """Test that hidden directories are skipped by default."""
        programs = omni_runner.scan_for_executables()
        
        # Hidden files should not be found
        assert not any("secret.py" in str(p.path) for p in programs)


class TestLanguageIdentification:
    """Tests for programming language identification."""
    
    def test_identify_python(self, python_simple_script, omni_runner):
        """Test Python file identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "Python"
    
    def test_identify_javascript(self, nodejs_simple_script, omni_runner):
        """Test JavaScript file identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "JavaScript"
    
    def test_identify_typescript(self, temp_dir, omni_runner):
        """Test TypeScript file identification."""
        script = temp_dir / "app.ts"
        script.write_text('const x: string = "hello";\nconsole.log(x);\n')
        
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "TypeScript"
    
    def test_identify_go(self, go_simple_program, omni_runner):
        """Test Go file identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "Go"
    
    def test_identify_rust(self, rust_simple_program, omni_runner):
        """Test Rust file identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "Rust"
    
    def test_identify_java(self, java_maven_app, omni_runner):
        """Test Java file identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "Java"
    
    def test_identify_ruby(self, ruby_simple_script, omni_runner):
        """Test Ruby file identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "Ruby"
    
    def test_identify_php(self, php_simple_script, omni_runner):
        """Test PHP file identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "PHP"
    
    def test_identify_cpp(self, cpp_simple_program, omni_runner):
        """Test C++ file identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "C++"
    
    def test_identify_c(self, c_simple_program, omni_runner):
        """Test C file identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "C"
    
    def test_identify_binary(self, binary_file, omni_runner):
        """Test binary executable identification."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].type == "Executable"


class TestMainFileScoring:
    """Tests for main entry point scoring."""
    
    def test_main_py_high_score(self, python_main_pattern, omni_runner):
        """Test that main.py gets high score."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].score >= 15  # Should match main pattern
    
    def test_app_py_high_score(self, temp_dir, omni_runner):
        """Test that app.py gets high score."""
        script = temp_dir / "app.py"
        script.write_text('print("app")\n')
        
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].score >= 10  # Should match app pattern
    
    def test_manage_py_high_score(self, python_django_app, omni_runner):
        """Test that manage.py gets high score for Django."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        # manage.py is a Django-specific main file
        assert programs[0].score >= 20
    
    def test_server_js_high_score(self, nodejs_simple_script, omni_runner):
        """Test that server.js gets higher score."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        assert programs[0].score >= 10  # Matches server pattern
    
    def test_shebang_increases_score(self, file_with_shebang, omni_runner):
        """Test that files with shebang get higher score."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        # Shebang adds to score
        assert programs[0].score >= 5
    
    def test_if_main_pattern(self, python_main_pattern, omni_runner):
        """Test that if __name__ == '__main__' increases score."""
        programs = omni_runner.scan_for_executables()
        assert len(programs) == 1
        # Main pattern should give additional points
        assert programs[0].score >= 12
    
    def test_depth_affects_score(self, deep_directory_structure, omni_runner):
        """Test that file depth affects score."""
        programs = omni_runner.scan_for_executables()
        
        # Files closer to root should have higher scores
        if len(programs) > 1:
            sorted_by_score = sorted(programs, key=lambda p: p.score, reverse=True)
            # First file should be at shallower depth
            first_depth = len(programs[0].path.relative_to(omni_runner.base_path).parts) - 1
            second_depth = len(sorted_by_score[1].path.relative_to(omni_runner.base_path).parts) - 1
            assert first_depth <= second_depth


class TestDirectoryDepth:
    """Tests for directory depth handling."""
    
    def test_shallow_files_preferred(self, temp_dir, omni_runner):
        """Test that files at shallower depths are preferred."""
        # Create file at root
        (temp_dir / "main.py").write_text('print("root")\n')
        
        # Create file in subdirectory
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "main.py").write_text('print("subdir")\n')
        
        programs = omni_runner.scan_for_executables()
        
        # Should find both files
        assert len(programs) == 2
        
        # Root file should have higher score
        root_prog = next(p for p in programs if p.path.parent == temp_dir)
        subdir_prog = next(p for p in programs if p.path.parent != temp_dir)
        
        assert root_prog.score >= subdir_prog.score


class TestMultiLanguageProject:
    """Tests for multi-language project handling."""
    
    def test_detect_all_languages(self, multi_language_project, omni_runner):
        """Test that all languages in a project are detected."""
        programs = omni_runner.scan_for_executables()
        
        types_found = {prog.type for prog in programs}
        
        assert "Python" in types_found
        assert "JavaScript" in types_found
        assert "Go" in types_found
    
    def test_sort_by_score(self, multi_language_project, omni_runner):
        """Test that programs are sorted by score."""
        programs = omni_runner.scan_for_executables()
        
        # Verify sorted by score descending
        for i in range(len(programs) - 1):
            assert programs[i].score >= programs[i + 1].score


class TestDiscoveredProgramsStorage:
    """Tests for discovered programs storage."""
    
    def test_programs_stored_in_instance(self, python_simple_script, omni_runner):
        """Test that discovered programs are stored in the instance."""
        omni_runner.scan_for_executables()
        
        assert len(omni_runner.discovered_programs) == 1
        assert omni_runner.discovered_programs[0].name == "hello.py"
    
    def test_programs_cleared_on_rescan(self, python_simple_script, omni_runner):
        """Test that programs are cleared when rescanning."""
        omni_runner.scan_for_executables()
        assert len(omni_runner.discovered_programs) == 1
        
        # Add another file
        (omni_runner.base_path / "another.py").write_text('print("another")\n')
        
        # Rescan
        omni_runner.scan_for_executables()
        
        # Should now have 2 programs
        assert len(omni_runner.discovered_programs) == 2


class TestScannedFilesCounter:
    """Tests for scanned files tracking."""
    
    def test_scan_counts_files(self, temp_dir, omni_runner):
        """Test that scanning counts files correctly."""
        # Create multiple files
        for i in range(5):
            (temp_dir / f"file_{i}.py").write_text(f'print({i})\n')
        
        programs = omni_runner.scan_for_executables()
        
        assert len(programs) == 5


class TestPermissionHandling:
    """Tests for permission-related edge cases."""
    
    def test_unreadable_file_skipped(self, temp_dir, omni_runner):
        """Test that unreadable files are handled gracefully."""
        script = temp_dir / "secret.py"
        script.write_text('print("secret")\n')
        
        # Make file unreadable
        os.chmod(script, 0o000)
        
        try:
            # Should not raise exception
            programs = omni_runner.scan_for_executables()
            # File might be skipped due to permission error
        finally:
            # Restore permissions for cleanup
            os.chmod(script, 0o644)


class TestInvalidFiles:
    """Tests for handling invalid files."""
    
    def test_syntax_error_python_file(self, invalid_python_file, omni_runner):
        """Test that syntax errors in Python files don't prevent detection."""
        programs = omni_runner.scan_for_executables()
        
        # File should still be detected
        assert len(programs) == 1
        assert programs[0].name == "broken.py"
    
    def test_empty_file(self, temp_dir, omni_runner):
        """Test that empty files are handled."""
        script = temp_dir / "empty.py"
        script.write_text("")
        
        programs = omni_runner.scan_for_executables()
        
        # Empty file should still be detected
        assert len(programs) == 1
        assert programs[0].name == "empty.py"
    
    def test_binary_content_file(self, temp_dir, omni_runner):
        """Test that files with binary content are handled."""
        script = temp_dir / "data"
        script.write_bytes(b'\x00\x01\x02\x03\x04\x05')
        os.chmod(script, 0o755)  # Make it executable
        
        programs = omni_runner.scan_for_executables()
        
        # Should be detected as executable (no extension, but executable)
        assert len(programs) == 1
        assert programs[0].type == "Executable"


class TestConfigAffectsScanning:
    """Tests for configuration affecting scanning behavior."""
    
    def test_custom_max_depth(self, deep_directory_structure, omni_runner_with_config):
        """Test that custom max_depth affects scanning."""
        programs = omni_runner_with_config.scan_for_executables()
        
        # Default max_depth is 10, but custom config says 5
        # So files deeper than 5 should not be found
        for prog in programs:
            depth = len(prog.path.relative_to(omni_runner_with_config.base_path).parts) - 1
            assert depth <= 5
    
    def test_custom_exclude_dirs(self, temp_dir, omni_runner):
        """Test that custom exclude directories are respected."""
        # Create config file to exclude custom_exclude directory
        config_file = temp_dir / ".omnirun.yaml"
        config_file.write_text("""
exclude_dirs:
  - custom_exclude
""")
        
        # Create OmniRun with config
        from omni_run import OmniRun
        runner = OmniRun(str(temp_dir), config_file=str(config_file))
        
        # Create files in root and excluded dirs
        (temp_dir / "main.py").write_text('print("main")\n')
        
        custom_dir = temp_dir / "custom_exclude"
        custom_dir.mkdir()
        (custom_dir / "excluded.py").write_text('print("excluded")\n')
        
        programs = runner.scan_for_executables()
        
        # main.py should be found
        assert any(p.name == "main.py" for p in programs)
        # excluded.py should not be found
        assert not any("custom_exclude" in str(p.path) for p in programs)


class TestRelativePathCalculation:
    """Tests for relative path calculation."""
    
    def test_relative_path_correct(self, python_simple_script, omni_runner):
        """Test that relative paths are calculated correctly."""
        programs = omni_runner.scan_for_executables()
        
        assert len(programs) == 1
        assert programs[0].relative_path == "hello.py"
    
    def test_relative_path_nested(self, temp_dir, omni_runner):
        """Test relative paths for nested files."""
        subdir = temp_dir / "src"
        subdir.mkdir()
        (subdir / "app.py").write_text('print("app")\n')
        
        programs = omni_runner.scan_for_executables()
        
        app_prog = next(p for p in programs if p.name == "app.py")
        assert app_prog.relative_path == "src/app.py"

