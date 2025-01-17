from setuptools import setup, find_packages

setup(
    name="openadapt-descriptions",
    version="0.1.0",
    description="Generate natural language descriptions for OpenAdapt recordings",
    author="OpenAdapt Contributors",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openadapt",
        "click",
        "pyyaml",
        "tenacity",
        "python-dotenv",
        "anthropic",
    ],
    entry_points={
        "console_scripts": [
            "openadapt-descriptions=openadapt_descriptions.cli:main",
        ],
    },
) 