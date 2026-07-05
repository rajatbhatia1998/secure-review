import os
import tempfile
import pytest
from pathlib import Path
from backend.app.utils.repo_scanner import scan_directory

def test_scan_directory_python():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy Python project structure
        py_file = Path(tmpdir) / "app.py"
        py_file.write_text("print('hello')", encoding="utf-8")
        
        req_file = Path(tmpdir) / "requirements.txt"
        req_file.write_text("fastapi\n", encoding="utf-8")
        
        res = scan_directory(tmpdir)
        
        assert "app.py" in res["files"]
        assert "requirements.txt" in res["files"]
        assert res["dominant_language"] == "Python"
        assert "pip/poetry" in res["package_managers"]

def test_scan_directory_js():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy JS React project structure
        js_file = Path(tmpdir) / "src" / "index.js"
        js_file.parent.mkdir()
        js_file.write_text("console.log('test')", encoding="utf-8")
        
        pkg_file = Path(tmpdir) / "package.json"
        pkg_file.write_text('{"name": "test"}', encoding="utf-8")
        
        res = scan_directory(tmpdir)
        
        # Check normalized separators
        assert "src/index.js" in res["files"] or "src\\index.js" in res["files"]
        assert "package.json" in res["files"]
        assert res["dominant_language"] == "JavaScript"
        assert "npm/yarn/pnpm" in res["package_managers"]
