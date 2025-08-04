from PyQt5.QtCore import QThread, pyqtSignal, QObject
import json

class WorkerSignals(QObject):
    """Defines signals available from a running worker thread."""
    progress = pyqtSignal(str)
    host_discovered = pyqtSignal(str, dict)
    finished = pyqtSignal(dict)
    network_scan_finished = pyqtSignal(list)

class DiscoveryWorker(QThread):
    """
    Worker thread specifically for running the network discovery module.
    """
    def __init__(self, selected_ranges):
        super().__init__()
        self.signals = WorkerSignals()
        self.selected_ranges = selected_ranges

    def run(self):
        from modules.network_discover import NetworkDiscover
        discover_module = NetworkDiscover()
        found_ips = discover_module.run(selected_ranges=self.selected_ranges)
        self.signals.network_scan_finished.emit(found_ips)

class ScanWorker(QThread):
    def __init__(self, targets, modules_to_run):
        super().__init__()
        self.targets = targets
        self.modules_to_run = modules_to_run
        self.signals = WorkerSignals()

    def run(self):
        from core.module_coordinator import ModuleCoordinator
        coordinator = ModuleCoordinator()
        
        all_results = {}
        for target in self.targets:
            self.signals.progress.emit(f"[*] Discovering host: {target}...")
            
            port_scanner_module = coordinator.available_modules['port_scanner']
            discovery_data = port_scanner_module.discover_host(target)
            
            self.signals.host_discovered.emit(target, discovery_data)

            if discovery_data['status'] == 'up':
                self.signals.progress.emit(f"[+] Host {target} is online. Running selected modules...")
                initial_results = {'port_scanner': {target: discovery_data}}
                
                results = coordinator.run_selected_modules(
                    modules_to_run=self.modules_to_run,
                    target=target,
                    initial_results=initial_results
                )
                all_results[target] = results
                self.signals.progress.emit(f"[+] Finished scan on target: {target}")
            else:
                self.signals.progress.emit(f"[-] Host {target} is offline. Skipping full scan.")
                all_results[target] = {'status': 'down'}

        self.signals.finished.emit(all_results)
