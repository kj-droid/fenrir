from PyQt5.QtCore import QThread, pyqtSignal, QObject
import json

class WorkerSignals(QObject):
    """Defines signals available from a running worker thread."""
    progress = pyqtSignal(str)
    open_ports_found = pyqtSignal(dict)
    vulnerabilities_found = pyqtSignal(dict)
    finished = pyqtSignal(str)

class ScanWorker(QThread):
    """Worker thread for running scans in the background."""
    def __init__(self, targets, modules_to_run):
        super().__init__()
        self.targets = targets
        self.modules_to_run = modules_to_run
        self.signals = WorkerSignals()

    def run(self):
        from core.module_coordinator import ModuleCoordinator
        coordinator = ModuleCoordinator()
        
        for target in self.targets:
            self.signals.progress.emit(f"[*] Starting scan on target: {target}...")
            
            results = coordinator.run_selected_modules(
                modules_to_run=self.modules_to_run,
                target=target
            )

            # --- FIX: Emit the port scanner result directly ---
            # The result already contains the target as a key.
            if 'port_scanner' in results and isinstance(results['port_scanner'], dict):
                self.signals.open_ports_found.emit(results['port_scanner'])

            # Vulnerability data needs to be associated with the target, so this wrapping is correct.
            if 'vulnerability_identifier' in results and isinstance(results['vulnerability_identifier'], dict):
                vulns_data = {target: results['vulnerability_identifier']}
                self.signals.vulnerabilities_found.emit(vulns_data)

            self.signals.progress.emit(f"[+] Finished scan on target: {target}")

        self.signals.finished.emit("All scans complete.")
