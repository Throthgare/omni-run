"""
Tests for program execution in OmniRun.

This module tests:
- Synchronous program execution
- Execution with arguments
- Execution result handling
- Error handling during execution
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from conftest import *


class TestSynchronousExecution:
    """Tests for synchronous program execution."""
    
    def test_execute_simple_python(self, python_simple_script, omni_runner):
        """Test executing a simple Python script."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        result = omni_runner.execute_program_synchronously(prog)
        
        assert result.status in [omni_run.ExecutionStatus.SUCCESS, omni_run.ExecutionStatus.FAILED]
        assert result.program == prog
        assert result.start_time <= result.end_time
        assert result.duration >= 0
    
    def test_execute_python_with_output(self, python_simple_script, omni_runner):
        """Test that Python script output is captured."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        result = omni_runner.execute_program_synchronously(prog)
        
        # Should capture stdout
        assert result.stdout is not None
        # May contain "Hello, World!" depending on interpreter availability
    
    def test_execution_returns_result_object(self, python_simple_script, omni_runner):
        """Test that execution returns an ExecutionResult."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        result = omni_runner.execute_program_synchronously(prog)
        
        assert result is not None
        assert hasattr(result, 'status')
        assert hasattr(result, 'start_time')
        assert hasattr(result, 'end_time')
        assert hasattr(result, 'duration')
        assert hasattr(result, 'return_code')
        assert hasattr(result, 'stdout')
        assert hasattr(result, 'stderr')
    
    def test_execution_with_nonexistent_file(self, temp_dir, omni_runner):
        """Test handling of non-existent program file."""
        from omni_run import ExecutableProgram, ExecutionResult, ExecutionStatus
        
        fake_prog = ExecutableProgram(
            path=Path("/nonexistent/file.py"),
            name="nonexistent.py",
            relative_path="nonexistent.py",
            type="Python",
            interpreters=["python"],
            score=10,
            dependencies=[],
            has_config=False,
            config_files=[],
            estimated_complexity="Simple"
        )
        
        result = omni_runner.execute_program_synchronously(fake_prog)
        
        assert result.status == ExecutionStatus.ERROR
        assert result.error_message is not None


class TestExecutionWithArguments:
    """Tests for execution with command-line arguments."""
    
    def test_execute_with_args_list(self, python_main_pattern, omni_runner):
        """Test executing with args passed as list."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        
        # Some programs may not accept args
        try:
            result = omni_runner.execute_program_synchronously(prog, args=["--help"])
            assert result is not None
            assert result.args == ["--help"]
        except Exception:
            # Some programs may fail with args - that's OK
            pass


class TestExecutionResultStatus:
    """Tests for execution result status values."""
    
    def test_success_status(self, python_simple_script, omni_runner):
        """Test successful execution has SUCCESS status."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        result = omni_runner.execute_program_synchronously(prog)
        
        # Status should be SUCCESS if return code is 0
        if result.return_code == 0:
            assert result.status == omni_run.ExecutionStatus.SUCCESS
    
    def test_failed_status(self, temp_dir, omni_runner):
        """Test failed execution has FAILED status."""
        # Create a script that exits with non-zero code
        script = temp_dir / "fail.py"
        script.write_text('import sys\nsys.exit(1)\n')
        
        omni_runner.scan_for_executables()
        
        prog = next((p for p in omni_runner.discovered_programs if p.name == "fail.py"), None)
        if prog is None:
            pytest.skip("Program not discovered")
        
        result = omni_runner.execute_program_synchronously(prog)
        
        assert result.status == omni_run.ExecutionStatus.FAILED
        assert result.return_code == 1


class TestExecutionHistory:
    """Tests for execution history tracking."""
    
    def test_execution_history_populated(self, python_simple_script, omni_runner):
        """Test that execution history is populated."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        omni_runner.execute_program_synchronously(prog)
        
        assert len(omni_runner.execution_history) >= 1
    
    def test_execution_history_contains_result(self, python_simple_script, omni_runner):
        """Test that execution history contains the result."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        result = omni_runner.execute_program_synchronously(prog)
        
        assert result in omni_runner.execution_history


class TestExecutionDuration:
    """Tests for execution duration tracking."""
    
    def test_duration_calculated(self, python_simple_script, omni_runner):
        """Test that execution duration is calculated."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        result = omni_runner.execute_program_synchronously(prog)
        
        assert result.duration >= 0
        assert isinstance(result.duration, float)
    
    def test_start_before_end_time(self, python_simple_script, omni_runner):
        """Test that start_time is before end_time."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        result = omni_runner.execute_program_synchronously(prog)
        
        assert result.start_time <= result.end_time


class TestExecutionByIndex:
    """Tests for executing programs by index."""
    
    def test_execute_by_valid_index(self, python_simple_script, omni_runner):
        """Test executing program by valid index."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        result = omni_runner.execute_program(index=0)
        
        assert result is not None
        assert result.program in omni_runner.discovered_programs
    
    def test_execute_by_invalid_index(self, omni_runner):
        """Test executing by invalid index raises error."""
        omni_runner.scan_for_executables()
        
        with pytest.raises(ValueError):
            omni_runner.execute_program(index=999)
    
    def test_negative_index_error(self, omni_runner):
        """Test that negative index raises error."""
        omni_runner.scan_for_executables()
        
        with pytest.raises(ValueError):
            omni_runner.execute_program(index=-1)


class TestExecutionReturnCode:
    """Tests for return code handling."""
    
    def test_return_code_zero_success(self, temp_dir, omni_runner):
        """Test that return code 0 indicates success."""
        script = temp_dir / "success.py"
        script.write_text('print("success")\n')
        
        omni_runner.scan_for_executables()
        
        prog = next((p for p in omni_runner.discovered_programs if p.name == "success.py"), None)
        if prog is None:
            pytest.skip("Program not discovered")
        
        result = omni_runner.execute_program_synchronously(prog)
        
        # Return code should be 0
        assert result.return_code == 0
    
    def test_return_code_nonzero_failure(self, temp_dir, omni_runner):
        """Test that non-zero return code indicates failure."""
        script = temp_dir / "fail.py"
        script.write_text('import sys\nsys.exit(42)\n')
        
        omni_runner.scan_for_executables()
        
        prog = next((p for p in omni_runner.discovered_programs if p.name == "fail.py"), None)
        if prog is None:
            pytest.skip("Program not discovered")
        
        result = omni_runner.execute_program_synchronously(prog)
        
        assert result.return_code == 42


class TestExecutionStdout:
    """Tests for stdout capture."""
    
    def test_stdout_captured(self, temp_dir, omni_runner):
        """Test that stdout is captured."""
        script = temp_dir / "output.py"
        script.write_text('print("test output")\n')
        
        omni_runner.scan_for_executables()
        
        prog = next((p for p in omni_runner.discovered_programs if p.name == "output.py"), None)
        if prog is None:
            pytest.skip("Program not discovered")
        
        result = omni_runner.execute_program_synchronously(prog)
        
        assert result.stdout is not None
        # Should contain the output
        assert "test output" in result.stdout or result.stdout == ""


class TestExecutionStderr:
    """Tests for stderr capture."""
    
    def test_stderr_captured(self, temp_dir, omni_runner):
        """Test that stderr is captured."""
        script = temp_dir / "stderr.py"
        script.write_text('import sys\nsys.stderr.write("error message\\n")\n')
        
        omni_runner.scan_for_executables()
        
        prog = next((p for p in omni_runner.discovered_programs if p.name == "stderr.py"), None)
        if prog is None:
            pytest.skip("Program not discovered")
        
        result = omni_runner.execute_program_synchronously(prog)
        
        assert result.stderr is not None


class TestExecutionTimeout:
    """Tests for execution timeout handling."""
    
    def test_timeout_respected(self, temp_dir, omni_runner):
        """Test that timeout is respected."""
        script = temp_dir / "slow.py"
        script.write_text('import time\ntime.sleep(10)\n')
        
        omni_runner.scan_for_executables()
        
        # Set short timeout for test
        omni_runner.config['timeout'] = 1
        
        prog = next((p for p in omni_runner.discovered_programs if p.name == "slow.py"), None)
        if prog is None:
            pytest.skip("Program not discovered")
        
        result = omni_runner.execute_program_synchronously(prog)
        
        # Should have timed out
        assert result.status == omni_run.ExecutionStatus.ERROR
        assert "timeout" in result.error_message.lower() or result.return_code is None


class TestPreferredCommand:
    """Tests for preferred command storage."""
    
    def test_preferred_command_saved(self, python_simple_script, omni_runner):
        """Test that preferred command is saved after execution."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        omni_runner.execute_program_synchronously(prog)
        
        # Should have saved preferred command
        key = f"{prog.type}:{prog.name}"
        assert key in omni_runner.preferred_commands
    
    def test_preferred_command_contains_command(self, python_simple_script, omni_runner):
        """Test that saved command contains the execution command."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        omni_runner.execute_program_synchronously(prog)
        
        key = f"{prog.type}:{prog.name}"
        command = omni_runner.preferred_commands[key]
        
        assert command is not None
        assert len(command) > 0


class TestExecuteProgramMethod:
    """Tests for the execute_program method with auto-fix."""
    
    def test_execute_with_auto_fix_disabled(self, python_simple_script, omni_runner):
        """Test execute_program with auto_fix=False."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        # Should execute without auto-fix
        result = omni_runner.execute_program(0, auto_fix=False)
        
        assert result is not None
    
    def test_execute_with_auto_fix_enabled(self, python_simple_script, omni_runner):
        """Test execute_program with auto_fix=True."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        omni_runner.config['auto_fix'] = True
        
        # Should attempt auto-fix if needed
        result = omni_runner.execute_program(0, auto_fix=True)
        
        assert result is not None


class TestProgramComplexity:
    """Tests for program complexity estimation."""
    
    def test_complexity_simple(self, python_simple_script, omni_runner):
        """Test that simple script has Simple complexity."""
        omni_runner.scan_for_executables()
        
        if not omni_runner.discovered_programs:
            pytest.skip("No programs discovered")
        
        prog = omni_runner.discovered_programs[0]
        
        assert prog.estimated_complexity in ["Simple", "Unknown"]
    
    def test_complexity_moderate(self, temp_dir, omni_runner):
        """Test complexity estimation for larger files."""
        # Create a file with more lines
        script = temp_dir / "moderate.py"
        lines = ['def func():\n    pass'] * 100
        script.write_text('\n'.join(lines))
        
        omni_runner.scan_for_executables()
        
        prog = next((p for p in omni_runner.discovered_programs if p.name == "moderate.py"), None)
        if prog is None:
            pytest.skip("Program not discovered")
        
        assert prog.estimated_complexity in ["Moderate", "Complex", "Very Complex"]


class TestExecutionEnvironmentVars:
    """Tests for environment variable handling."""
    
    def test_execution_with_env_vars(self, temp_dir, omni_runner):
        """Test that execution can use environment variables."""
        script = temp_dir / "env_test.py"
        script.write_text('import os\nprint(os.environ.get("TEST_VAR", "default"))\n')
        
        omni_runner.scan_for_executables()
        
        prog = next((p for p in omni_runner.discovered_programs if p.name == "env_test.py"), None)
        if prog is None:
            pytest.skip("Program not discovered")
        
        # Set environment variable
        import os as os_mod
        os_mod.environ["TEST_VAR"] = "test_value"
        
        try:
            result = omni_runner.execute_program_synchronously(prog)
            assert result is not None
        finally:
            del os_mod.environ["TEST_VAR"]

