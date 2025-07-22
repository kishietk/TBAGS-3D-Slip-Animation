### cores/entities/roof_core.py
from .panel_core import Panel

class Roof(Panel):
    """
    屋根パネル。
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.is_roof: bool = True
