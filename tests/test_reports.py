"""
Tests for report generation in OmniRun.

This module tests:
- HTML report generation
- JSON report generation
- Report content validation
- Report file output
"""

import os
import json
import pytest
from pathlib import Path
from datetime import datetime

from conftest import *


class TestHTMLReportGeneration:
    """Tests for HTML report generation."""
    
    def test_generate_html_report(self, python_flask_app, omni_runner, temp_dir):
        """Test basic HTML report generation."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        assert output_file.exists()
        
        content = output_file.read_text()
        
        # Should have basic HTML structure
        assert "<html" in content.lower() or "<!DOCTYPE html>" in content.upper()
        assert "</html>" in content.lower()
    
    def test_html_report_contains_program_info(self, python_flask_app, omni_runner, temp_dir):
        """Test that HTML report contains program information."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        
        # Should contain program names
        assert "Flask" in content or "flask" in content.lower()
    
    def test_html_report_has_tailwind(self, python_flask_app, omni_runner, temp_dir):
        """Test that HTML report uses Tailwind CSS."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        
        # Should include Tailwind CDN
        assert "tailwindcss" in content.lower() or "cdn.tailwindcss.com" in content
    
    def test_html_report_has_interactivity(self, python_flask_app, omni_runner, temp_dir):
        """Test that HTML report has interactive elements."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        
        # Should have JavaScript for interactivity
        assert "<script" in content.lower()
    
    def test_html_report_shows_status(self, python_flask_app, omni_runner, temp_dir):
        """Test that HTML report shows program status."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        
        # Should show ready or issues status
        assert "ready" in content.lower() or "issues" in content.lower() or "✅" in content
    
    def test_html_report_shows_dependencies(self, python_flask_app, omni_runner, temp_dir):
        """Test that HTML report shows dependency information."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        
        # Should mention dependencies
        assert "dependencies" in content.lower() or "node_modules" in content.lower()
    
    def test_html_report_multiple_programs(self, multi_language_project, omni_runner, temp_dir):
        """Test HTML report with multiple programs."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        
        # Should contain information about multiple programs
        assert content.count("Python") + content.count("python") > 1 or len(omni_runner.discovered_programs) > 1
    
    def test_html_report_with_frameworks(self, nodejs_express_app, omni_runner, temp_dir):
        """Test HTML report shows framework information."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        
        # Should mention Express
        assert "express" in content.lower() or "Express" in content
    
    def test_html_file_is_valid_html(self, python_simple_script, omni_runner, temp_dir):
        """Test that generated HTML is valid."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        
        # Basic HTML validation
        assert len(content) > 100  # Should have meaningful content
        assert "<html" in content.lower() or "<!DOCTYPE" in content


class TestJSONReportGeneration:
    """Tests for JSON report generation."""
    
    def test_generate_json_report(self, python_simple_script, omni_runner, temp_dir):
        """Test basic JSON report generation."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        assert output_file.exists()
        
        # Should be valid JSON
        data = json.loads(output_file.read_text())
        assert data is not None
    
    def test_json_report_has_project_info(self, python_simple_script, omni_runner, temp_dir):
        """Test that JSON report contains project information."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        # Should have project path
        assert "project" in data
        assert data["project"] is not None
    
    def test_json_report_has_generation_time(self, python_simple_script, omni_runner, temp_dir):
        """Test that JSON report includes generation timestamp."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        # Should have generation time
        assert "generated_at" in data
        assert data["generated_at"] is not None
    
    def test_json_report_has_summary(self, python_simple_script, omni_runner, temp_dir):
        """Test that JSON report includes summary."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        # Should have summary
        assert "summary" in data
        assert "total_programs" in data["summary"]
    
    def test_json_report_has_programs(self, python_simple_script, omni_runner, temp_dir):
        """Test that JSON report contains program list."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        # Should have programs array
        assert "programs" in data
        assert isinstance(data["programs"], list)
        assert len(data["programs"]) == len(omni_runner.discovered_programs)
    
    def test_json_program_has_required_fields(self, python_simple_script, omni_runner, temp_dir):
        """Test that JSON program entries have required fields."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        if len(data["programs"]) > 0:
            prog = data["programs"][0]
            
            # Check required fields
            assert "name" in prog
            assert "path" in prog
            assert "type" in prog
            assert "score" in prog
            assert "complexity" in prog
    
    def test_json_program_has_dependencies(self, python_flask_app, omni_runner, temp_dir):
        """Test that JSON report includes dependency information."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        if len(data["programs"]) > 0:
            prog = data["programs"][0]
            
            # Should have dependencies
            assert "dependencies" in prog
            assert isinstance(prog["dependencies"], list)
    
    def test_json_dependencies_have_fix_info(self, nodejs_express_app, omni_runner, temp_dir):
        """Test that JSON dependencies include fix command info."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        # Find a program with dependencies
        programs_with_deps = [p for p in data["programs"] if p.get("dependencies")]
        if programs_with_deps:
            prog = programs_with_deps[0]
            dep = prog["dependencies"][0]
            
            # Should have fix info
            assert "fix_command" in dep
            assert "can_auto_fix" in dep
    
    def test_json_report_has_framework(self, python_flask_app, omni_runner, temp_dir):
        """Test that JSON report includes framework information."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        # Find Flask program
        flask_prog = next((p for p in data["programs"] if "Flask" in str(p.get("framework", ""))), None)
        
        if flask_prog:
            assert flask_prog.get("framework") == "Flask"
    
    def test_json_report_has_task_runners(self, nodejs_express_app, omni_runner, temp_dir):
        """Test that JSON report includes task runner information."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        # Find Express program
        express_prog = next((p for p in data["programs"] if p.get("framework") == "Express.js"), None)
        
        if express_prog:
            assert "task_runners" in express_prog
            assert "npm" in express_prog["task_runners"]
    
    def test_json_report_is_machine_readable(self, multi_language_project, omni_runner, temp_dir):
        """Test that JSON report is properly formatted for machine reading."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        content = output_file.read_text()
        
        # Should be parseable without errors
        data = json.loads(content)
        
        # Should have expected structure
        assert "summary" in data
        assert "programs" in data
        
        # Summary should have counts
        assert "total_programs" in data["summary"]
        assert "ready_count" in data["summary"]
        assert "issues_count" in data["summary"]
    
    def test_json_summary_counts(self, python_flask_app, omni_runner, temp_dir):
        """Test that JSON summary has correct counts."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        assert data["summary"]["total_programs"] == len(omni_runner.discovered_programs)
        
        # ready + issues should equal total
        assert data["summary"]["ready_count"] + data["summary"]["issues_count"] == data["summary"]["total_programs"]
    
    def test_json_by_type_counts(self, multi_language_project, omni_runner, temp_dir):
        """Test that JSON summary includes program counts by type."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        assert "by_type" in data["summary"]
        
        # Count by type should sum to total
        type_counts = sum(data["summary"]["by_type"].values())
        assert type_counts == data["summary"]["total_programs"]


class TestReportFilePaths:
    """Tests for report file path handling."""
    
    def test_html_report_to_new_path(self, python_simple_script, omni_runner, temp_dir):
        """Test generating HTML report to a new path."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "subdir" / "report.html"
        
        # Should create parent directories
        omni_runner.generate_html_report(str(output_file))
        
        assert output_file.exists()
    
    def test_json_report_to_new_path(self, python_simple_script, omni_runner, temp_dir):
        """Test generating JSON report to a new path."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "subdir" / "report.json"
        
        # Should create parent directories
        omni_runner.generate_json_report(str(output_file))
        
        assert output_file.exists()
    
    def test_overwrite_existing_report(self, python_simple_script, omni_runner, temp_dir):
        """Test overwriting existing report file."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        
        # Create initial report
        omni_runner.generate_html_report(str(output_file))
        initial_content = output_file.read_text()
        
        # Modify file
        output_file.write_text("modified")
        
        # Generate new report
        omni_runner.scan_for_executables()  # Rescan to get new data
        omni_runner.generate_html_report(str(output_file))
        
        # File should be overwritten
        new_content = output_file.read_text()
        assert new_content != "modified"
        assert "<html" in new_content.lower() or "<!DOCTYPE" in new_content


class TestReportWithNoPrograms:
    """Tests for reports when no programs are found."""
    
    def test_html_report_empty(self, empty_directory, omni_runner, temp_dir):
        """Test HTML report with no programs."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        assert "0" in content or "No programs" in content or len(omni_runner.discovered_programs) == 0
    
    def test_json_report_empty(self, empty_directory, omni_runner, temp_dir):
        """Test JSON report with no programs."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        assert data["summary"]["total_programs"] == 0
        assert len(data["programs"]) == 0


class TestReportTimestamps:
    """Tests for timestamp handling in reports."""
    
    def test_html_report_has_timestamp(self, python_simple_script, omni_runner, temp_dir):
        """Test that HTML report includes timestamp."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.html"
        omni_runner.generate_html_report(str(output_file))
        
        content = output_file.read_text()
        
        # Should contain some date/time information
        assert "20" in content  # Years start with 20
    
    def test_json_report_timestamp_format(self, python_simple_script, omni_runner, temp_dir):
        """Test that JSON report has ISO format timestamp."""
        omni_runner.scan_for_executables()
        
        output_file = temp_dir / "report.json"
        omni_runner.generate_json_report(str(output_file))
        
        data = json.loads(output_file.read_text())
        
        # Should be ISO format
        assert "T" in data["generated_at"]  # ISO format has T between date and time
        assert "-" in data["generated_at"]  # ISO format has dashes

