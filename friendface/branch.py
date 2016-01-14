# -*- coding: utf-8 -*-


class Branch(set):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.replies = {}
        self.root = None
        self._name = None

    def __hash__(self):
        return hash(self.root)

    def __repr__(self):
        return '<Branch %s>' % self.name

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

    def to_flat_tree(self):
        tree = self.to_tree()
        count_leaves(tree)
        return flatten_tree(tree)

    def to_uri_list(self):
        return '\n'.join(sorted(self))


def count_leaves(root):
    total_leaves = 1  # this one
    for leaf in root['replies']:
        leaves = leaf.get('leaves') or count_leaves(leaf)
        leaf['leaves'] = leaves
        total_leaves += leaves
    return total_leaves


def flatten_tree(root, level=0):
    result = [dict(key=root['key'], level=level)]
    last = len(root.get('replies')) - 1
    for n, leaf in enumerate(sorted(
            root.get('replies'),
            key=lambda x: (x.get('leaves'), x.get('key')))):
        result.extend(flatten_tree(leaf, level+(0 if n == last else 1)))
    return result
