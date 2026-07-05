from setuptools import setup, find_packages

setup(
    name="secure-review",
    version="1.2.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-core>=0.1.0",
        "langchain-openai>=0.0.5",
        "langchain-anthropic>=0.1.0",
        "langgraph>=0.0.10",
        "GitPython>=3.1.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "requests>=2.30.0",
        "bandit>=1.7.5",
    ],
    entry_points={
        "console_scripts": [
            "secure-review=backend.app.cli:app",
        ],
    },
    package_data={
        "backend.app": [
            "dist/*",
            "dist/assets/*",
        ],
    },
    include_package_data=True,
)
