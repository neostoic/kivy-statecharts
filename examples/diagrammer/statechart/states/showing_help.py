from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

from kivy_statecharts.system.state import State


class ShowingHelpScreen(State):

    def __init__(self, **kwargs):
        super(ShowingHelpScreen, self).__init__(**kwargs)

    def enter_state(self, context=None):

        if not 'Help' in self.statechart.app.screen_manager.screen_names:

            self.app = self.statechart.app

            view = BoxLayout(orientation='vertical', spacing=10)

            toolbar = BoxLayout(size_hint=(1.0, None), height=30)

            button = ToggleButton(text='Help',
                                  color=[1.0, 1.0, 1.0, .9],
                                  bold=True,
                                  group='screen manager buttons')
            button.state = 'down'
            toolbar.add_widget(button)

            button = ToggleButton(
                    text='DrawingArea', group='screen manager buttons')
            button.bind(on_press=self.go_to_drawing_area)

            toolbar.add_widget(button)

            view.add_widget(toolbar)

            state_diagram_description = """
After app loads, you see a blank rectangle display on the right for the drawing
area, but the full area of the window is actually now the drawing area. You can
do this:

0) If you want, try out the menu to select the State menu, and the Triangle
choice in the submenu, but presently the Triangle is hard-coded.

1) Touch (or click) once in the drawing area to draw a triangle shape.

2) Touch again in another area to draw a second shape.

3) Touch the perimeter of a triangle and drag to move it.

4) Touch and drag in the center of one rectangle to the center of another.

4a) On touch up, bubbles will appear on either end of the connection.

4b) In a given bubble, touch and drag within the Drag button to move the
    connection point for the end (dragging out of the drag button will
    terminate the move, presently -- needs event handling in state for
    drawing_area).

4c) Repeat drag ops on the Drag button, for now to drag the given connection
    point further, clockwise (too jerky and skips for now).

4d) Once the connection point is ok, touch Accept.

5) You can add more triangles and connections.

6) You can move triangles with connections, and the connections will adjust."""

            scrollview = ScrollView()
            scrollview.add_widget(
                    Label(text=state_diagram_description, markup=True))

            view.add_widget(scrollview)

            screen = Screen(name='Help')
            screen.add_widget(view)

            self.app.screen_manager.add_widget(screen)

        if self.app.screen_manager.current != 'Help':
            self.app.screen_manager.current = 'Help'

    def exit_state(self, context=None):
        pass

    def go_to_drawing_area(self, *args):
        self.go_to_state('ShowingDrawingArea')