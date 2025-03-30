from abc import ABC

from app.priontech_logging import load_logger


class BaseInvoiceHandler(ABC):
    """Handles the Lingua invoice process."""

    def __init__(self):
        self.logger = load_logger()
