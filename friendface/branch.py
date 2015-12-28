# -*- coding: utf-8 -*-


class Branch(set):
    def __init__(self, key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key
    
    def __hash__(self):
        return hash(self.key)

    def __in__(self, value):
        return value in [key for key in self]

    def insert(self, key, parent):
        if parent == self.key:
            self.add(Branch(key))
        else:
            for child in self:
                child.insert(key, parent)
