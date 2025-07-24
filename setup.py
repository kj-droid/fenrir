from setuptools import setup, find_packages

setup(
    name="fenrir",
    version="2.0.0",
    author="Your Name",
    description="Fenrir: Multi-Module Security Scanner",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt5",
        "nmap-python",
        "requests",
        "fpdf",
        "gitpython",
        "matplotlib",
    ],
    entry_points={
        "console_scripts": [
            "fenrir=fenrir_launcher:main",
        ],
    },
)
