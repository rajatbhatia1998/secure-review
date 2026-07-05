from setuptools import setup, find_packages

setup(
    name="secure-review",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
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
