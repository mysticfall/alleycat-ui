from typing import TypeVar, Final, Generic

from returns.maybe import Maybe, Nothing

from alleycat.ui import Component, ComponentUI, Graphics, LookAndFeel, Panel, RGBA, Window, Label, Point, Toolkit, \
    TextAlign, Font, Button, LabelButton, WindowUI

T = TypeVar("T", bound=Component, contravariant=True)


class GlassLookAndFeel(LookAndFeel):
    BorderThickness: Final = 2

    def __init__(self, toolkit: Toolkit) -> None:
        super().__init__(toolkit)

        def with_prefix(key: str, prefix: str) -> str:
            return str.join(".", [prefix, key])

        active_color = RGBA(0.3, 0.7, 0.3, 1)
        highlight_color = RGBA(0.9, 0.8, 0.5, 1)

        self.set_font("text", toolkit.font_registry.fallback_font)

        self.set_color(with_prefix(ColorKeys.Background, "Window"), RGBA(0, 0, 0, 0.8))
        self.set_color(with_prefix(ColorKeys.Border, "Window"), active_color)
        self.set_color(with_prefix(ColorKeys.Border, "Button"), active_color)
        self.set_color(with_prefix(ColorKeys.BorderHover, "Button"), highlight_color)
        self.set_color(with_prefix(ColorKeys.BackgroundActive, "Button"), active_color)
        self.set_color(with_prefix(ColorKeys.BorderActive, "Button"), active_color)

        self.set_color(ColorKeys.Text, RGBA(0.8, 0.8, 0.8, 1))
        self.set_color(with_prefix(ColorKeys.TextHover, "Button"), highlight_color)
        self.set_color(with_prefix(ColorKeys.TextActive, "Button"), RGBA(0, 0, 0, 1))

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def create_ui(self, component: T) -> ComponentUI[T]:
        assert component is not None

        if isinstance(component, Panel):
            return GlassPanelUI()
        elif isinstance(component, Window):
            return GlassWindowUI()
        elif isinstance(component, LabelButton):
            return GlassLabelButtonUI()
        elif isinstance(component, Button):
            return GlassButtonUI()
        elif isinstance(component, Label):
            return GlassLabelUI()

        return GlassComponentUI()


# noinspection PyMethodMayBeStatic
class GlassComponentUI(ComponentUI[T], Generic[T]):

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: T) -> None:
        assert g is not None
        assert component is not None

        self.background_color(component).map(lambda c: self.draw_background(g, component, c))
        self.border_color(component).map(lambda c: self.draw_border(g, component, c))

    def background_color(self, component: T) -> Maybe[RGBA]:
        return component.resolve_color(ColorKeys.Background)

    def border_color(self, component: T) -> Maybe[RGBA]:
        return component.resolve_color(ColorKeys.Border)

    def draw_background(self, g: Graphics, component: T, color: RGBA) -> None:
        g.color = color
        g.fill_rect(component.bounds)

    def draw_border(
            self,
            g: Graphics,
            component: T,
            color: RGBA,
            thickness: float = GlassLookAndFeel.BorderThickness) -> None:
        g.color = color
        g.stroke = thickness
        g.draw_rect(component.bounds)


class GlassPanelUI(GlassComponentUI[Panel]):

    def __init__(self) -> None:
        super().__init__()


class GlassWindowUI(GlassComponentUI[Window], WindowUI[Window]):

    def __init__(self) -> None:
        super().__init__()


# noinspection PyMethodMayBeStatic
class GlassLabelUI(GlassComponentUI[Label]):
    _ratio_for_align = {TextAlign.Begin: 0., TextAlign.Center: 0.5, TextAlign.End: 1.}

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: Label) -> None:
        super().draw(g, component)

        font = self.text_font(component)
        color = self.text_color(component)

        color.map(lambda c: self.draw_text(g, component, font, c))

    def draw_text(self, g: Graphics, component: Label, font: Font, color: RGBA) -> None:
        g.font = font
        g.color = color

        text = component.text
        size = component.text_size

        extents = component.context.toolkit.font_registry.text_extent(text, font, size)

        (x, y, w, h) = component.bounds.tuple

        rh = self._ratio_for_align[component.text_align]
        rv = self._ratio_for_align[component.text_vertical_align]

        tx = (w - extents.width) * rh + x
        ty = (h - extents.height) * rv + extents.height + y

        g.draw_text(text, size, Point(tx, ty))

    def text_color(self, component: Label) -> Maybe[RGBA]:
        return component.resolve_color(ColorKeys.Text)

    def text_font(self, component: Label) -> Font:
        font_registry = component.context.toolkit.font_registry

        return component.resolve_font("text").value_or(font_registry.fallback_font)


# noinspection PyMethodMayBeStatic
class GlassButtonUI(GlassComponentUI[Button]):

    def __init__(self) -> None:
        super().__init__()

    def background_color(self, component: T) -> Maybe[RGBA]:
        return self.resolve_color(component, ColorKeys.Background)

    def border_color(self, component: T) -> Maybe[RGBA]:
        return self.resolve_color(component, ColorKeys.Border)

    def resolve_color(self, component: LabelButton, key: str) -> Maybe[RGBA]:
        color: Maybe[RGBA] = Nothing

        if component.active:
            color = component.resolve_color(key + ":active")
        elif component.hover:
            color = component.resolve_color(key + ":hover")

        return component.resolve_color(key) if color == Nothing else color


class GlassLabelButtonUI(GlassButtonUI, GlassLabelUI):

    def __init__(self) -> None:
        super().__init__()

    def text_color(self, component: T) -> Maybe[RGBA]:
        return self.resolve_color(component, ColorKeys.Text)


class ColorKeys:
    Background: Final = "background"
    BackgroundHover: Final = "background:hover"
    BackgroundActive: Final = "background:active"

    Border: Final = "border"
    BorderHover: Final = "border:hover"
    BorderActive: Final = "border:active"

    Text: Final = "text"
    TextHover: Final = "text:hover"
    TextActive: Final = "text:active"
