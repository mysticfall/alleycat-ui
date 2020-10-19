import unittest

from alleycat.reactive import functions as rv
from returns.maybe import Some, Nothing

from alleycat.ui import Bounds, Point, LayoutContainer, Component, Dimension, Panel, AbsoluteLayout, FillLayout, \
    Window, Insets
from tests.ui import UITestCase


# noinspection DuplicatedCode
class LayoutContainerTest(UITestCase):

    def test_component_at_with_hierarchy(self):
        parent = LayoutContainer(self.context)
        parent.bounds = Bounds(0, 0, 200, 200)

        child = LayoutContainer(self.context)
        child.bounds = Bounds(50, 50, 100, 100)

        grand_child = LayoutContainer(self.context)
        grand_child.bounds = Bounds(25, 25, 50, 50)

        child.add(grand_child)
        parent.add(child)

        self.assertEqual(Nothing, parent.component_at(Point(-1, 0)))
        self.assertEqual(Nothing, parent.component_at(Point(201, 0)))
        self.assertEqual(Nothing, parent.component_at(Point(200, 201)))
        self.assertEqual(Nothing, parent.component_at(Point(-1, 200)))

        self.assertEqual(Some(parent), parent.component_at(Point(50, 49)))
        self.assertEqual(Some(parent), parent.component_at(Point(151, 50)))
        self.assertEqual(Some(parent), parent.component_at(Point(150, 151)))
        self.assertEqual(Some(parent), parent.component_at(Point(49, 150)))

        self.assertEqual(Some(child), parent.component_at(Point(50, 50)))
        self.assertEqual(Some(child), parent.component_at(Point(150, 50)))
        self.assertEqual(Some(child), parent.component_at(Point(150, 150)))
        self.assertEqual(Some(child), parent.component_at(Point(50, 150)))

        self.assertEqual(Some(grand_child), parent.component_at(Point(75, 75)))
        self.assertEqual(Some(grand_child), parent.component_at(Point(125, 75)))
        self.assertEqual(Some(grand_child), parent.component_at(Point(125, 125)))
        self.assertEqual(Some(grand_child), parent.component_at(Point(75, 125)))

        self.assertEqual(Some(child), parent.component_at(Point(74, 75)))
        self.assertEqual(Some(child), parent.component_at(Point(125, 74)))
        self.assertEqual(Some(child), parent.component_at(Point(126, 125)))
        self.assertEqual(Some(child), parent.component_at(Point(75, 126)))

    def test_component_at_with_layers(self):
        parent = LayoutContainer(self.context)
        parent.bounds = Bounds(0, 0, 200, 200)

        bottom = LayoutContainer(self.context)
        bottom.bounds = Bounds(0, 0, 100, 100)

        middle = LayoutContainer(self.context)
        middle.bounds = Bounds(100, 100, 100, 100)

        top = LayoutContainer(self.context)
        top.bounds = Bounds(50, 50, 100, 100)

        parent.add(bottom)
        parent.add(middle)
        parent.add(top)

        self.assertEqual(Some(parent), parent.component_at(Point(200, 0)))
        self.assertEqual(Some(parent), parent.component_at(Point(0, 200)))

        self.assertEqual(Some(bottom), parent.component_at(Point(0, 0)))
        self.assertEqual(Some(bottom), parent.component_at(Point(100, 0)))
        self.assertEqual(Some(bottom), parent.component_at(Point(0, 100)))

        self.assertEqual(Some(middle), parent.component_at(Point(200, 100)))
        self.assertEqual(Some(middle), parent.component_at(Point(200, 200)))
        self.assertEqual(Some(middle), parent.component_at(Point(100, 200)))

        self.assertEqual(Some(top), parent.component_at(Point(100, 100)))
        self.assertEqual(Some(top), parent.component_at(Point(150, 150)))
        self.assertEqual(Some(top), parent.component_at(Point(150, 50)))
        self.assertEqual(Some(top), parent.component_at(Point(50, 150)))

    def test_component_parent(self):
        parents = []

        parent1 = LayoutContainer(self.context)
        parent2 = LayoutContainer(self.context)

        component = Component(self.context)

        rv.observe(component.parent).subscribe(parents.append)

        self.assertEqual(Nothing, component.parent)
        self.assertEqual([Nothing], parents)

        parent1.add(component)

        self.assertIn(component, parent1.children)

        self.assertEqual(Some(parent1), component.parent)
        self.assertEqual([Nothing, Some(parent1)], parents)

        parent2.add(component)

        self.assertIn(component, parent2.children)
        self.assertNotIn(component, parent1.children)

        self.assertEqual(Some(parent2), component.parent)
        self.assertEqual([Nothing, Some(parent1), Nothing, Some(parent2)], parents)

        parent2.remove(component)

        self.assertEqual(Nothing, component.parent)
        self.assertEqual([Nothing, Some(parent1), Nothing, Some(parent2), Nothing], parents)

    def test_absolute_layout(self):
        container = Window(self.context, AbsoluteLayout())
        container.bounds = Bounds(30, 30, 200, 200)

        child1 = Panel(self.context)
        child1.bounds = Bounds(10, 10, 20, 20)

        child2 = Panel(self.context)
        child2.bounds = Bounds(50, 60, 20, 20)

        container.add(child1)
        container.add(child2)

        self.context.process()

        self.assertEqual(Bounds(10, 10, 20, 20), child1.bounds)
        self.assertEqual(Bounds(50, 60, 20, 20), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

        container.bounds = Bounds(20, 20, 100, 100)
        child1.minimum_size = Some(Dimension(400, 400))
        child2.bounds = Bounds(-30, -40, 50, 50)

        self.context.process()

        self.assertEqual(Bounds(10, 10, 400, 400), child1.bounds)
        self.assertEqual(Bounds(-30, -40, 50, 50), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

    def test_fill_layout(self):
        container = Window(self.context, FillLayout())
        container.bounds = Bounds(30, 30, 200, 200)

        child1 = Panel(self.context)
        child1.bounds = Bounds(10, 10, 20, 20)

        child2 = Panel(self.context)
        child2.bounds = Bounds(50, 60, 20, 20)

        container.add(child1)
        container.add(child2)

        self.context.process()

        self.assertEqual(Bounds(0, 0, 200, 200), child1.bounds)
        self.assertEqual(Bounds(0, 0, 200, 200), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

        container.bounds = Bounds(20, 20, 100, 100)

        self.context.process()

        self.assertEqual(Bounds(0, 0, 100, 100), child1.bounds)
        self.assertEqual(Bounds(0, 0, 100, 100), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

        child1.bounds = Bounds(10, 60, 300, 300)
        child2.bounds = Bounds(-30, -40, 50, 50)

        self.context.process()

        self.assertEqual(Bounds(0, 0, 100, 100), child1.bounds)
        self.assertEqual(Bounds(0, 0, 100, 100), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

        child1.minimum_size = Some(Dimension(200, 300))
        child2.minimum_size = Some(Dimension(500, 150))

        child1.preferred_size = Some(Dimension(300, 450))
        child2.preferred_size = Some(Dimension(640, 400))

        self.context.process()

        self.assertEqual(Bounds(0, 0, 500, 300), child1.bounds)
        self.assertEqual(Bounds(0, 0, 500, 300), child2.bounds)
        self.assertEqual(Bounds(20, 20, 500, 300), container.bounds)
        self.assertEqual(Dimension(500, 300), container.effective_minimum_size)
        self.assertEqual(Dimension(640, 450), container.effective_preferred_size)

    def test_fill_layout_insets(self):
        layout = FillLayout(Insets(10, 5, 3, 6))
        container = Window(self.context, layout)
        container.bounds = Bounds(30, 30, 200, 200)

        child = Panel(self.context)

        container.add(child)

        self.context.process()

        self.assertEqual(Bounds(10, 6, 189, 187), child.bounds)
        self.assertEqual(Dimension(11, 13), container.effective_minimum_size)
        self.assertEqual(Dimension(11, 13), container.effective_preferred_size)

        child.minimum_size = Some(Dimension(10, 10))

        self.context.process()

        self.assertEqual(Bounds(10, 6, 189, 187), child.bounds)
        self.assertEqual(Dimension(21, 23), container.effective_minimum_size)
        self.assertEqual(Dimension(21, 23), container.effective_preferred_size)

        layout.padding = Insets(5, 5, 5, 5)

        self.context.process()

        self.assertEqual(Bounds(5, 5, 190, 190), child.bounds)
        self.assertEqual(Dimension(20, 20), container.effective_minimum_size)
        self.assertEqual(Dimension(20, 20), container.effective_preferred_size)


if __name__ == '__main__':
    unittest.main()
