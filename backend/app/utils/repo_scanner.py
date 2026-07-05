import os
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple

IGNORE_DIRS: Set[str] = {
    '.git', 'node_modules', 'venv', '.venv', 'dist', 'build', '__pycache__',
    'env', '.env', '.idea', '.vscode', 'artifacts', 'target', '.gemini'
}

IGNORE_EXTENSIONS: Set[str] = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz',
    '.mp4', '.mp3', '.db', '.sqlite', '.exe', '.dll', '.so', '.dylib', '.woff',
    '.woff2', '.ttf', '.eot', '.svg', '.bin', '.pyc', '.map'
}

LANGUAGE_MAP: Dict[str, str] = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript React',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript React',
    '.go': 'Go',
    '.rs': 'Rust',
    '.java': 'Java',
    '.cpp': 'C++',
    '.c': 'C',
    '.h': 'C/C++ Header',
    '.cs': 'C#',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.sh': 'Shell Script',
    '.ps1': 'PowerShell',
    '.html': 'HTML',
    '.css': 'CSS',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.json': 'JSON',
    '.md': 'Markdown',
    '.dockerfile': 'Dockerfile',
}

def is_binary(file_path: Path) -> bool:
    if file_path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return True
    except Exception:
        return True
    return False

def scan_directory(root_path: str) -> Dict[str, Any]:
    root = Path(root_path).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Path '{root_path}' does not exist or is not a directory.")

    file_list: List[str] = []
    languages: Dict[str, int] = {}
    package_managers: List[str] = []
    frameworks: List[str] = []

    # Traverse directory tree
    for dirpath, dirnames, filenames in os.walk(root):
        # In-place modify dirnames to skip ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            full_path = Path(dirpath) / filename
            if is_binary(full_path):
                continue
            
            relative_path = str(full_path.relative_to(root)).replace('\\', '/')
            file_list.append(relative_path)

            # Detect language
            ext = full_path.suffix.lower()
            if filename.lower() == 'dockerfile' or filename.lower().endswith('.dockerfile'):
                lang = 'Dockerfile'
            else:
                lang = LANGUAGE_MAP.get(ext, 'Other')
            
            if lang != 'Other':
                languages[lang] = languages.get(lang, 0) + 1

            # Detect package managers / frameworks
            lower_name = filename.lower()
            if lower_name == 'package.json':
                package_managers.append('npm/yarn/pnpm')
            elif lower_name in ('requirements.txt', 'pyproject.toml', 'pipfile'):
                package_managers.append('pip/poetry')
            elif lower_name == 'go.mod':
                package_managers.append('go modules')
            elif lower_name == 'cargo.toml':
                package_managers.append('cargo')

            # Simple framework cues
            if filename.startswith('next.config'):
                frameworks.append('Next.js')
            elif filename.startswith('vite.config'):
                frameworks.append('Vite')
            elif 'django' in lower_name or (ext == '.py' and 'wsgi.py' in lower_name):
                frameworks.append('Django')
            elif 'flask' in lower_name:
                frameworks.append('Flask')

    # Ensure unique lists
    package_managers = list(set(package_managers))
    frameworks = list(set(frameworks))

    # Calculate overall dominant language
    dominant_lang = "Unknown"
    programming_langs = {k: v for k, v in languages.items() if k not in ("JSON", "YAML", "Markdown")}
    if programming_langs:
        dominant_lang = max(programming_langs, key=programming_langs.get)
    elif languages:
        dominant_lang = max(languages, key=languages.get)

    return {
        "root": str(root).replace('\\', '/'),
        "files": file_list,
        "languages": languages,
        "dominant_language": dominant_lang,
        "package_managers": package_managers,
        "frameworks": frameworks,
    }

def get_file_content(root_path: str, relative_path: str, max_lines: int = 1000) -> str:
    path = Path(root_path) / relative_path
    if not path.exists():
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [f.readline() for _ in range(max_lines)]
            return "".join(lines)
    except Exception:
        return ""
