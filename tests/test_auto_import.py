import os
import sys
import tempfile
import pytest
from unittest import mock


class TestAutoImportModules:
    """Tests for the auto_import_modules function."""

    def test_auto_import_skips_nonexistent_modules(self, tmp_path):
        """Test that auto_import_modules skips modules that don't exist."""
        # Create a minimal package structure
        pkg_dir = tmp_path / "test_pkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        sub_dir = pkg_dir / "submodule"
        sub_dir.mkdir()
        (sub_dir / "__init__.py").write_text("")
        # Note: No tools.py file

        # Add tmp_path to sys.path so we can import the test package
        sys.path.insert(0, str(tmp_path))

        try:
            from mcp_foundry.mcp_server import auto_import_modules

            # Should not raise any exceptions
            auto_import_modules("test_pkg", targets=["tools", "resources"])
        finally:
            sys.path.remove(str(tmp_path))
            # Clean up imported modules
            for key in list(sys.modules.keys()):
                if key.startswith("test_pkg"):
                    del sys.modules[key]

    def test_auto_import_imports_existing_modules(self, tmp_path):
        """Test that auto_import_modules successfully imports existing modules."""
        # Create a minimal package structure with a tools.py file
        pkg_dir = tmp_path / "test_pkg2"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        sub_dir = pkg_dir / "submodule"
        sub_dir.mkdir()
        (sub_dir / "__init__.py").write_text("")
        (sub_dir / "tools.py").write_text("IMPORTED = True")

        # Add tmp_path to sys.path so we can import the test package
        sys.path.insert(0, str(tmp_path))

        try:
            from mcp_foundry.mcp_server import auto_import_modules

            # Import should succeed
            auto_import_modules("test_pkg2", targets=["tools"])

            # Verify the module was imported
            import test_pkg2.submodule.tools
            assert test_pkg2.submodule.tools.IMPORTED is True
        finally:
            sys.path.remove(str(tmp_path))
            # Clean up imported modules
            for key in list(sys.modules.keys()):
                if key.startswith("test_pkg2"):
                    del sys.modules[key]

    def test_auto_import_reports_missing_dependencies(self, tmp_path, caplog):
        """Test that auto_import_modules logs errors for missing dependencies."""
        import logging

        # Create a package with a module that has a missing import
        pkg_dir = tmp_path / "test_pkg3"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        sub_dir = pkg_dir / "submodule"
        sub_dir.mkdir()
        (sub_dir / "__init__.py").write_text("")
        # This module tries to import a non-existent module
        (sub_dir / "tools.py").write_text("import nonexistent_module_xyz123")

        sys.path.insert(0, str(tmp_path))

        try:
            from mcp_foundry.mcp_server import auto_import_modules

            with caplog.at_level(logging.ERROR):
                auto_import_modules("test_pkg3", targets=["tools"])

            # Should have logged an error about missing dependency
            assert any("missing dependency" in record.message for record in caplog.records)
        finally:
            sys.path.remove(str(tmp_path))
            # Clean up imported modules
            for key in list(sys.modules.keys()):
                if key.startswith("test_pkg3"):
                    del sys.modules[key]

    def test_auto_import_skips_special_directories(self, tmp_path):
        """Test that auto_import_modules skips __pycache__ and other special directories."""
        # Create a package with __pycache__ directory
        pkg_dir = tmp_path / "test_pkg4"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        pycache_dir = pkg_dir / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "tools.py").write_text("SHOULD_NOT_IMPORT = True")

        sys.path.insert(0, str(tmp_path))

        try:
            from mcp_foundry.mcp_server import auto_import_modules

            # Should not raise any exceptions and should not import __pycache__
            auto_import_modules("test_pkg4", targets=["tools"])

            # Verify __pycache__.tools was not imported
            assert "test_pkg4.__pycache__.tools" not in sys.modules
        finally:
            sys.path.remove(str(tmp_path))
            # Clean up imported modules
            for key in list(sys.modules.keys()):
                if key.startswith("test_pkg4"):
                    del sys.modules[key]
