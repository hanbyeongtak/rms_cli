import logging

class EJDebugFilter(logging.Filter):
    def filter(self, record):
        # Always show ERROR level logs
        if record.levelno >= logging.ERROR:
            return True
        # Only show INFO/DEBUG level logs if they start with "[>>> EJ_DEBUG]"
        if record.levelno >= logging.INFO:
            if hasattr(record, 'message') and record.message.startswith("[>>> EJ_DEBUG]"):
                return True
        return False
