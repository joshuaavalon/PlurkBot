from typing import List

__all__ = ["NewPlurkEvent"]


class NewPlurkEvent:
    def __init__(self, plurks: List[dict]):
        self.plurks = plurks  # type:List[dict]
