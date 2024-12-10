from setuptools import setup, find_packages

setup(
    name="fenrir",
    version="1.0.0",
    author="Your Name",
    author_email="your_email@example.com",
    description="Fenrir: Multi-Module Security Scanner",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.0.5",
        "apscheduler==3.10.1",
        "scapy==2.5.0",
        "requests==2.31.0",
        "dnspython==2.3.1",
        "scikit-learn==1.3.1",
        "pandas==2.1.1",
        "numpy==1.25.2",
        "joblib==1.3.2",
        "beautifulsoup4==4.13.0",
        "PyQt5==5.15.9",
        "matplotlib==3.8.1",
        "python-dotenv==1.0.0",
        "nmap==0.0.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "fenrir=main:main",
        ],
    },
)
