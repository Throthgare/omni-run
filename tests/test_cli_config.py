"""Tests for CLI and configuration in OmniRun."""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from conftest import *


class TestArgumentParsing:
    def test_default_path_argument(self, omni_runner):
        omni_runner.scan_for_executables()
        assert omni_runner.base_path is not None
    
    def test_verbose_flag(self, temp_dir):
        from omni_run import OmniRun
        runner = OmniRun(str(temp_dir), verbose=True)
        assert runner.verbose is True


class TestConfigurationFile:
    def test_yaml_config_loading(self, custom_config_file, temp_dir):
        from omni_run import OmniRun
        runner = OmniRun(str(temp_dir), config_file=str(custom_config_file))
        assert runner.config.get('auto_fix') is True
    
    def test_exclude_dirs_config(self, omni_runner):
        exclude_dirs = omni_runner.config.get('exclude_dirs', [])
        assert 'node_modules' in exclude_dirs


class TestConfigurationOptions:
    def test_auto_fix_default(self, omni_runner):
        assert omni_runner.config.get('auto_fix', False) is False
    
    def test_enable_backup_default(self, omni_runner):
        assert omni_runner.config.get('enable_backup', True) is True
    
    def test_auto_rollback_default(self, omni_runner):
        assert omni_runner.config.get('auto_rollback', True) is True
    
    def test_enable_docker_default(self, omni_runner):
        assert omni_runner.config.get('enable_docker', True) is True
    
    def test_enable_venv_default(self, omni_runner):
        assert omni_runner.config.get('enable_venv', True) is True


class TestColorOutput:
    def test_colors_class_exists(self):
        from omni_run import Colors
        assert hasattr(Colors, 'HEADER')
        assert hasattr(Colors, 'OKBLUE')
        assert hasattr(Colors, 'OKGREEN')
    
    def test_colors_can_be_disabled(self):
        from omni_run import Colors
        original = getattr(Colors, 'HEADER', '')
        Colors.disable()
        assert Colors.HEADER == ''
        if original:
            Colors.HEADER = original


class TestLogging:
    def test_log_method_exists(self, omni_runner):
        assert hasattr(omni_runner, 'log')
        assert callable(omni_runner.log)
    
    def test_log_with_level(self, omni_runner, capsys):
        omni_runner.log('Test message', 'INFO')
        captured = capsys.readouterr()
        assert 'Test message' in captured.out
    
    def test_verbose_only_log(self, omni_runner, capsys):
        omni_runner.verbose = False
        omni_runner.log('Verbose-only message', 'INFO')
        captured = capsys.readouterr()
        assert 'Verbose-only message' not in captured.out
    
    def test_verbose_log_shows(self, omni_runner, capsys):
        omni_runner.verbose = True
        omni_runner.log('Verbose message', 'INFO')
        captured = capsys.readouterr()
        assert 'Verbose message' in captured.out


class TestConfigModification:
    def test_modify_config(self, omni_runner):
        original = omni_runner.config.get('auto_fix')
        omni_runner.config['auto_fix'] = not original
        assert omni_runner.config.get('auto_fix') is not original
    
    def test_add_custom_config(self, omni_runner):
        omni_runner.config['custom_option'] = 'custom_value'
        assert omni_runner.config.get('custom_option') == 'custom_value'


class TestExecutablePatterns:
    def test_executable_patterns_exist(self, omni_runner):
        assert hasattr(omni_runner, 'executable_patterns')
        assert isinstance(omni_runner.executable_patterns, dict)
    
    def test_python_pattern_exists(self, omni_runner):
        assert 'Python' in omni_runner.executable_patterns
    
    def test_javascript_pattern_exists(self, omni_runner):
        assert 'JavaScript' in omni_runner.executable_patterns
    
    def test_go_pattern_exists(self, omni_runner):
        assert 'Go' in omni_runner.executable_patterns


class TestMainFilePatterns:
    def test_main_file_patterns_exist(self, omni_runner):
        assert hasattr(omni_runner, 'main_file_patterns')
        assert isinstance(omni_runner.main_file_patterns, list)
        assert len(omni_runner.main_file_patterns) > 0
