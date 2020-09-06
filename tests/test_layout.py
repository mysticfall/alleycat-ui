import unittest

from alleycat.reactive import functions as rv
from returns.maybe import Some, Nothing

from alleycat.ui import Bounds, Point, LayoutContainer, Component
from alleycat.ui.cairo import UI


class LayoutContainerTest(unittest.TestCase):

    def test_component_at_with_hierarchy(self):
        context = UI().create_context()

        parent = LayoutContainer(context)
        parent.bounds = Bounds(0, 0, 200, 200)

        child = LayoutContainer(context)
        child.bounds = Bounds(50, 50, 100, 100)

        grand_child = LayoutContainer(context)
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
        context = UI().create_context()

        parent = LayoutContainer(context)
        parent.bounds = Bounds(0, 0, 200, 200)

        bottom = LayoutContainer(context)
        bottom.bounds = Bounds(0, 0, 100, 100)

        middle = LayoutContainer(context)
        middle.bounds = Bounds(100, 100, 100, 100)

        top = LayoutContainer(context)
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
        context = UI().create_context()

        parents = []

        parent1 = LayoutContainer(context)
        parent2 = LayoutContainer(context)

        component = Component(context)

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


if __name__ == '__main__':
    unittest.main()
