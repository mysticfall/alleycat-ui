from __future__ import annotations

import functools
from abc import ABC
from collections import Mapping
from typing import Optional, Callable, Any, Dict, TYPE_CHECKING

from rx.disposable import Disposable

from alleycat.ui import EventDispatcher, EventLoopAware, Event, InputLookup, Input

if TYPE_CHECKING:
    from alleycat.ui import Toolkit, WindowManager

ErrorHandler = Callable[[Exception], None]


def catch_error(func: Callable[..., None]) -> Callable[..., None]:
    @functools.wraps(func)
    def safe_func(*args, **kwargs) -> None:
        try:
            func(*args, **kwargs)
        except Exception as e:
            args[0].error_handler(e)

    return safe_func


def default_error_handler(e: Exception) -> None:
    print(e)


class Context(EventLoopAware, EventDispatcher, InputLookup, Disposable):

    def __init__(self,
                 toolkit: Toolkit,
                 window_manager: Optional[WindowManager] = None,
                 error_handler: Optional[ErrorHandler] = None) -> None:
        if toolkit is None:
            raise ValueError("Argument 'toolkit' is required.")

        super().__init__()

        from alleycat.ui import WindowManager

        self._toolkit = toolkit

        self._window_manager = window_manager if window_manager is not None else WindowManager()
        self._error_handler = error_handler if error_handler is not None else default_error_handler

        self._graphics = toolkit.create_graphics(self)

        assert self._graphics is not None

        inputs = toolkit.create_inputs(self)

        assert inputs is not None

        self._inputs = {i.id: i for i in inputs}
        self._pollers = [i for i in inputs if isinstance(i, EventLoopAware)]

    @property
    def inputs(self) -> Mapping[str, Input]:
        return self._inputs

    @property
    def window_manager(self) -> WindowManager:
        return self._window_manager

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    @catch_error
    def process(self) -> None:
        self.process_inputs()
        self.process_draw()

    @catch_error
    def process_inputs(self) -> None:
        for poller in self._pollers:
            poller.process()

    @catch_error
    def process_draw(self) -> None:
        self._window_manager.draw(self._graphics)

    @catch_error
    def dispatch_event(self, event: Event) -> None:
        pass

    def dispose(self) -> None:
        super().dispose()

        catch_error(self._graphics.dispose)()
        catch_error(self._window_manager.dispose)()

        for i in self.inputs.values():
            catch_error(i.dispose)()


class ContextBuilder(ABC):

    def __init__(self, toolkit: Toolkit) -> None:
        if toolkit is None:
            raise ValueError("Argument 'toolkit' is required.")

        self.toolkit = toolkit
        self._args: Dict[str, Any] = dict()

    def with_window_manager(self, manager: WindowManager) -> ContextBuilder:
        if manager is None:
            raise ValueError("Argument 'manager' is required.")

        self._args["window_manager"] = manager

        return self

    def with_error_handler(self, handler: ErrorHandler) -> ContextBuilder:
        if handler is None:
            raise ValueError("Argument 'handler' is required.")

        self._args["error_handler"] = handler

        return self

    def create_context(self) -> Context:
        return Context(self.toolkit, **self._args)
