from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce
from typing import Optional, Iterator, TypeVar, Callable

import rx
from alleycat.reactive import ReactiveObject
from returns.maybe import Maybe, Nothing, Some
from rx import Observable
from rx import operators as ops

from alleycat.ui import Component, Container, Point, Graphics, Context, ComponentUI, Dimension


class Layout(ReactiveObject, ABC):

    def __init__(self) -> None:
        super().__init__()

    @property
    def on_constraints_change(self) -> Observable:
        return rx.empty()

    @abstractmethod
    def perform(self, component: LayoutContainer) -> None:
        pass

    @abstractmethod
    def minimum_size(self, component: LayoutContainer) -> Observable:
        pass

    @abstractmethod
    def preferred_size(self, component: LayoutContainer) -> Observable:
        pass

    @staticmethod
    def calculate_size(
            children: Observable,
            size_attribute: str,
            reducer: Callable[[Dimension, Dimension], Dimension]) -> Observable:
        if children is None:
            raise ValueError("Argument 'children' is required.")
        if size_attribute is None:
            raise ValueError("Argument 'size_attribute' is required.")
        if size_attribute is None:
            raise ValueError("Argument 'size_attribute' is required.")

        return children.pipe(
            ops.map(lambda v: map(lambda c: c.observe(size_attribute), v)),
            ops.map(lambda b: rx.combine_latest(*b, rx.of(Dimension(0, 0)))),
            ops.switch_latest(),
            ops.map(lambda b: reduce(reducer, b)))


class LayoutContainer(Component, Container[Component]):

    def __init__(self, context: Context, layout: Optional[Layout] = None, visible: bool = True):
        from .absolute import AbsoluteLayout

        self._layout = Maybe.from_value(layout).or_else_call(AbsoluteLayout)

        super().__init__(context, visible)

        self._layout_valid = True
        self._layout_in_progress = False

        on_size_change = self.observe("size")
        on_min_size_change = self.observe("effective_minimum_size")
        on_pre_size_change = self.observe("effective_preferred_size")
        on_children_change = self.observe("children")

        on_child_bounds_change = on_children_change.pipe(
            ops.map(lambda children: map(lambda c: c.observe("bounds"), children)),
            ops.map(lambda b: rx.merge(*b)),
            ops.switch_latest(),
            ops.map(lambda _: None))

        should_invalidate = rx.merge(
            on_size_change,
            on_min_size_change,
            on_pre_size_change,
            on_children_change,
            on_child_bounds_change,
            self.layout.on_constraints_change).pipe(
            ops.filter(lambda _: not self._layout_in_progress))

        self._layout_listener = should_invalidate.subscribe(
            lambda _: self.invalidate_layout(), self.context.error_handler)

    @property
    def layout(self) -> Layout:
        return self._layout

    def invalidate_layout(self) -> None:
        self._layout_valid = False

    def perform_layout(self) -> None:
        if not self._layout_valid and not self._layout_in_progress:
            self._layout_in_progress = True

            try:
                self.layout.perform(self)
            except BaseException as e:
                self.context.error_handler(e)

            self._layout_in_progress = False
            self._layout_valid = True

    def component_at(self, location: Point) -> Maybe[Component]:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        if self.bounds.contains(location):
            try:
                # noinspection PyTypeChecker
                children: Iterator[Component] = reversed(self.children)

                child = next(c for c in children if c.bounds.contains(location - self.location))

                if isinstance(child, LayoutContainer):
                    return child.component_at(location - self.location)
                else:
                    return Some(child)
            except StopIteration:
                return Some(self)

        return Nothing

    def add(self, child: Component) -> None:
        super().add(child)

        child.parent.map(lambda p: p.remove(child))
        child.parent = Some(self)

    def remove(self, child: Component) -> None:
        super().remove(child)

        child.parent = Nothing

    def draw(self, g: Graphics) -> None:
        self.perform_layout()

        super().draw(g)

    def draw_component(self, g: Graphics) -> None:
        super().draw_component(g)

        self.draw_children(g)

    def draw_children(self, g: Graphics) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            child.draw(g)

    def dispose(self) -> None:
        self.execute_safely(self._layout_listener.dispose)

        # noinspection PyTypeChecker
        for child in self.children:
            self.execute_safely(child.dispose)

        super().dispose()


T = TypeVar("T", bound=LayoutContainer, contravariant=True)


class LayoutContainerUI(ComponentUI[T], ABC):

    def __init__(self) -> None:
        super().__init__()

    def minimum_size(self, component: T) -> Observable:
        return component.layout.minimum_size(component)

    def preferred_size(self, component: T) -> Observable:
        return component.layout.preferred_size(component)


class Anchor(Enum):
    North = 0
    Northeast = 1
    East = 2
    Southeast = 3
    South = 4
    Southwest = 5
    West = 6
    Northwest = 7