# -*- coding: utf-8 -*-


class Branch(set):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.replies = {}
        self.root = None
        self._name = None

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self):
        return self._name or self.root

    @name.setter
    def name(self, name):
        self._name = name

    def insert(self, message):
        self.add(message.key)
        message.branch = self

        if message.in_reply_to is not None:
            if message.in_reply_to in self.replies.keys():
                self.replies[message.in_reply_to].append(message.key)
            else:
                self.replies[message.in_reply_to] = [message.key]

        elif self.root is not None:
            raise ValueError("Branch cannot have more than one root.")

        else:
            self.root = message.key

    def to_tree(self, root=None):
        root = root or self.root
        return {
            'key': root,
            'replies': [
                self.to_tree(reply) for reply in self.replies.get(root, [])
            ]
        }
