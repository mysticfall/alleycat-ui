from abc import ABC, abstractmethod
from typing import Callable

ErrorHandler = Callable[[BaseException], None]


class ErrorHandlerSupport(ABC):

    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def error_handler(self) -> ErrorHandler:
        pass

    def execute_safely(self, process: Callable[[], None]):
        if process is None:
            raise ValueError("Argument 'process' is required.")

        try:
            process()
        except Exception as e:
            self.error_handler(e)
