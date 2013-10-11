from kivy.controllers.listcontroller import ListController
from kivy.models import SelectableStringItem
from kivy.properties import ObjectProperty
from kivy.properties import OptionProperty
from kivy.selection import SelectionTool

from views.buttons.shape_bubble_button import ShapeBubbleButton

from views.graphics.shapes import PolygonVectorShape
from models.shape_tool import ShapeTool


class StateShapeToolsController(ListController):

    def __init__(self, **kwargs):

        kwargs['selection_mode'] = 'single'
        kwargs['allow_empty_selection'] = False

        super(StateShapeToolsController, self).__init__(**kwargs)

