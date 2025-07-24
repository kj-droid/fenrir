class BaseModule:
    def __init__(self):
        self.name = self.__class__.__name__

    def run(self, target, ports, previous_results=None):
        """
        The main method for a module.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Each module must implement the 'run' method.")
