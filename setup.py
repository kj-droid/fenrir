import os
import sys
import subprocess
import shutil
from setuptools import setup, find_packages
from setuptools.command.install import install

# --- Project Metadata ---
NAME = "fenrir"
VERSION = "2.4.1" # Version bump for permission fixes
DESCRIPTION = "Fenrir: An advanced, multi-module security scanner"
AUTHOR = "Fenrir Development Team"
EMAIL = "contact@example.com"
URL = "https://github.com/kj-droid/fenrir" 

# --- Python Package Dependencies ---
REQUIRED = [
    'PyQt5',
    'python-nmap',
    'GitPython',
    'requests',
    'fpdf',
    'netifaces',
]

# --- Configuration for Privileged Executables ---
PRIVILEGED_COMMANDS = {
    'nmap': {
        'method': 'setcap',
        'capabilities': 'cap_net_raw,cap_net_admin+eip',
        'package': 'nmap'
    },
    'netdiscover': {
        'method': 'sudoers',
        'package': 'netdiscover'
    }
}

# --- System-Level Dependencies (for Debian/Kali) ---
SYSTEM_DEPS = ['git', 'exploitdb', 'libcap2-bin'] + list(set([conf['package'] for conf in PRIVILEGED_COMMANDS.values()]))


class CustomInstallCommand(install):
    """
    Customized setuptools install command to handle system dependencies and permissions.
    """
    def run(self):
        self.install_system_dependencies()
        self.configure_executable_permissions()
        install.run(self)

    def install_system_dependencies(self):
        if sys.platform == 'linux' and os.geteuid() == 0:
            try:
                print("--- Running apt-get update ---")
                subprocess.check_call(['apt-get', 'update', '-y'])
                print(f"--- Installing System Dependencies: {', '.join(SYSTEM_DEPS)} ---")
                subprocess.check_call(['apt-get', 'install', '-y'] + SYSTEM_DEPS)
                print("--- System dependencies installed successfully. ---")
            except Exception as e:
                print(f"Warning: Failed to install system dependencies: {e}", file=sys.stderr)
        elif sys.platform == 'linux':
            print("Warning: Not running as root. Skipping system dependency installation.", file=sys.stderr)

    def configure_executable_permissions(self):
        """
        Sets permissions for all executables defined in PRIVILEGED_COMMANDS.
        """
        if sys.platform == 'linux' and os.geteuid() == 0:
            username = os.getenv('SUDO_USER')
            if not username:
                print("Warning: Could not determine the original user who ran sudo. Sudoers rules may need to be added manually.", file=sys.stderr)

            for exe, config in PRIVILEGED_COMMANDS.items():
                exe_path = shutil.which(exe)
                if not exe_path:
                    print(f"Warning: '{exe}' not found. Skipping permission setup. Please ensure '{config['package']}' is installed.", file=sys.stderr)
                    continue

                print(f"--- Configuring permissions for {exe.capitalize()} ---")

                if config['method'] == 'setcap':
                    setcap_path = shutil.which('setcap')
                    if setcap_path:
                        try:
                            command = [setcap_path, config['capabilities'], exe_path]
                            subprocess.check_call(command)
                            print(f"--- {exe.capitalize()} permissions configured successfully via setcap. ---")
                        except Exception as e:
                            print(f"Warning: Failed to set capabilities for {exe}: {e}", file=sys.stderr)
                    else:
                        print(f"Warning: 'setcap' not found. Cannot configure {exe}.", file=sys.stderr)

                elif config['method'] == 'sudoers':
                    if username:
                        sudoers_file = f"/etc/sudoers.d/fenrir-{exe}"
                        sudoers_rule = f"{username} ALL=(ALL) NOPASSWD: {exe_path}"
                        print(f"Creating sudoers rule: '{sudoers_rule}' in '{sudoers_file}'")
                        try:
                            with open(sudoers_file, 'w') as f:
                                f.write(sudoers_rule + '\n')
                            os.chmod(sudoers_file, 0o440) # Set correct permissions
                            print(f"--- {exe.capitalize()} permissions configured successfully via sudoers file. ---")
                        except Exception as e:
                            print(f"ERROR: Failed to write sudoers file for {exe}: {e}", file=sys.stderr)
                    else:
                        print(f"Warning: Cannot automatically configure sudoers for {exe.capitalize()}. Please add the following rule manually using 'sudo visudo':")
                        print(f"<your_username> ALL=(ALL) NOPASSWD: {exe_path}")

# --- Setup Configuration ---
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(),
    py_modules=['fenrir_launcher', 'fenrir_cli', 'update_db', 'verify_db'],
    include_package_data=True,
    license="MIT",
    install_requires=REQUIRED,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
    ],
    entry_points={
        "console_scripts": [
            "fenrir=fenrir_launcher:main",
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,
    },
)
