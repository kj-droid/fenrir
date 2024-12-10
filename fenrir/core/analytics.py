
class Analytics:
    @staticmethod
    def generate_summary(results):
        return {module: len(data) for module, data in results.items()}
