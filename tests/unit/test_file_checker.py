"""Unit tests for the FileChecker class."""
import argparse
from unittest import mock

import pytest

import flake8
from flake8 import checker
from flake8._compat import importlib_metadata
from flake8.plugins import finder


@mock.patch("flake8.checker.FileChecker._make_processor", return_value=None)
def test_repr(*args):
    """Verify we generate a correct repr."""
    file_checker = checker.FileChecker(
        filename="example.py",
        plugins=finder.Checkers([], [], []),
        options=argparse.Namespace(),
    )
    assert repr(file_checker) == "FileChecker for example.py"


def test_nonexistent_file():
    """Verify that checking non-existent file results in an error."""
    c = checker.FileChecker(
        filename="example.py",
        plugins=finder.Checkers([], [], []),
        options=argparse.Namespace(),
    )

    assert c.processor is None
    assert not c.should_process
    assert len(c.results) == 1
    error = c.results[0]
    assert error[0] == "E902"


def test_raises_exception_on_failed_plugin(tmp_path, default_options):
    """Checks that a failing plugin results in PluginExecutionFailed."""
    fname = tmp_path.joinpath("t.py")
    fname.touch()
    plugin = finder.LoadedPlugin(
        finder.Plugin(
            "plugin-name",
            "1.2.3",
            importlib_metadata.EntryPoint("X", "dne:dne", "flake8.extension"),
        ),
        mock.Mock(side_effect=ValueError),
        {},
    )
    fchecker = checker.FileChecker(
        filename=str(fname),
        plugins=finder.Checkers([], [], []),
        options=default_options,
    )
    with pytest.raises(flake8.exceptions.PluginExecutionFailed):
        fchecker.run_check(plugin)
