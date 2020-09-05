from typing import Tuple, Sequence

import rx
from alleycat.reactive import functions as rv, RV
from rx import operators as ops
from rx.disposable import Disposable
from rx.subject import Subject

from alleycat.ui import Context, Container, Graphics


class Window(Container):

    def __init__(self, context: Context) -> None:
        super().__init__(context)

        context.window_manager.add(self)


class WindowManager(Disposable):
    windows: RV[Sequence[Window]] = rv.new_view()

    def __init__(self) -> None:
        super().__init__()

        self._added_child = Subject()
        self._removed_child = Subject()

        changed_child = rx.merge(
            self._added_child.pipe(ops.map(lambda v: (v, True))),
            self._removed_child.pipe(ops.map(lambda v: (v, False))))

        def on_child_change(children: Tuple[Window, ...], event: Tuple[Window, bool]):
            (child, added) = event

            if added and child not in children:
                return children + (child,)
            elif not added and child in children:
                return tuple(c for c in children if c is not child)

        # noinspection PyTypeChecker
        self.windows = changed_child.pipe(
            ops.scan(on_child_change, ()), ops.start_with(()), ops.distinct_until_changed())

    def add(self, child: Window) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._added_child.on_next(child)

    def remove(self, child: Window) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._removed_child.on_next(child)

    def draw(self, g: Graphics) -> None:
        # noinspection PyTypeChecker
        for window in self.windows:
            window.draw(g)
