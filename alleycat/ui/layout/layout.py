from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import chain
from typing import Sequence, Tuple, Any, Mapping

import rx
from alleycat.reactive import ReactiveObject, RV, RP
from alleycat.reactive import functions as rv
from rx import Observable

from alleycat.ui import Component, Dimension, Bounds


class Layout(ReactiveObject, ABC):
    _children: RP[Sequence[LayoutItem]] = rv.from_value(())

    children: RV[Sequence[LayoutItem]] = _children.as_view()

    minimum_size: RV[Dimension]

    preferred_size: RV[Dimension]

    def __init__(self) -> None:
        super().__init__()

    def add(self, child: Component, *args, **kwargs) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        existing = filter(lambda c: c.component != child, self._children)
        item = LayoutItem(child, args, kwargs)

        # noinspection PyTypeChecker
        self._children = tuple(chain(existing, (item,)))

    def remove(self, child: Component) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        # noinspection PyTypeChecker
        self._children = tuple(filter(lambda c: c.component != child, self._children))

    @property
    def on_constraints_change(self) -> Observable:
        return rx.empty()

    @abstractmethod
    def perform(self, bounds: Bounds) -> None:
        pass


@dataclass(frozen=True)
class LayoutItem:
    component: Component

    args: Tuple[Any, ...]

    kwargs: Mapping[str, Any]
