from math import ceil
from enum import Enum
from abc import ABC, abstractclassmethod


class BPlusTree:

    def __init__(self, degree):
        self.degree = degree  # max amount of chilren
        self.UPPER_BOUND = degree - 1  # max amount of key
        self.LOWER_BOUND = ceil(degree / 2) - 1  # min amount of key
        self.root = None  # root of tree
        self.head = None  # head of linked list
        self.tail = None  # tail of linked list
        self.size = 0  # amount of data
        self.height = 0  # height of tree

    def insert(self, key, val):
        # empty case: 0 -> 1
        if self.size == 0:
            # for tree
            self.root = self.BPlusTreeDataNode([key], [val], self)
            self.size = 1
            self.height = 1
            # for linkedlist
            self.head = self.root  # maintain the head of linkedlist
            self.tail = self.root  # ...tail
            return
        # non-empty case: x -> x + 1
        try:
            # throw dulplication error (for unique index)
            splitted_key, newnode = self.root.set(key, val)
        except Exception as ex:
            print(ex)
            return
        # child does no split
        if newnode is None:
            return

        self.root = self.BPlusTreeIndexNode(
            [splitted_key], [self.root, newnode], self)
        self.height += 1

    def find(self, key):
        if self.root is None:
            raise Exception(f"key {key} not found\n")

        return self.root.get(key)

    def range_query(self, start, end):
        if self.root is None:
            return {}

        return self.root.range_query(start, end)

    def delete(self, key):
        # empty case
        if self.size == 0:
            return
        # non-empty case
        delete_info = self.root.remove(key)
        if not delete_info.is_delete:
            return
        if len(self.root.keys) == 0:
            self.root = None if len(self.root.vals) == 0 else self.root.vals[0]
            self.height -= 1

    def print_tree(self, node, last=True, header=''):
        if not(isinstance(node, self.BPlusTreeIndexNode) or isinstance(node, self.BPlusTreeDataNode)):
            return

        elbow = "└──"
        pipe = "│  "
        tee = "├──"
        blank = "   "

        if (isinstance(node, self.BPlusTreeDataNode)):
            print(header + (elbow if last else tee), 'id:',
                  id(node), ' keys:', node.keys, end='')
            print(' vals: [', ', '.join(
                list(map(lambda val: val, node.vals))), ']', end='')
            print(' prev:', id(node.prev) if node.prev is not None else 'None',
                  ' next:', id(node.next) if node.next is not None else 'None')
        else:
            print(header + (elbow if last else tee),
                  'keys:', node.keys, 'vals:', end='')
            print('[', ', '.join(list(map(lambda val: str(id(val)), node.vals))), ']')

        children = node.vals
        for i, c in enumerate(children):
            self.print_tree(
                c, header=header + (blank if last else pipe), last=i == len(children) - 1)

    # ---------- Tree Nodes ----------

    class BPlusTreeAbstractNode(ABC):

        def __init__(self, keys, vals, tree):
            self.keys = keys
            self.vals = vals
            self.tree = tree # for maintain size, get upper_bound/lower_bound

        @abstractclassmethod
        def get(self, key):
            pass

        @abstractclassmethod
        def set(self, key, val):
            pass

        @abstractclassmethod
        def remove(self, key):
            pass

        @abstractclassmethod
        def range_query(self, start, end):
            pass

        @abstractclassmethod
        def split(self):
            pass

        @abstractclassmethod
        def borrow(self, borrowed_node, direction, parrent_key):
            pass

        @abstractclassmethod
        def merge(self, merged_node, parrent_key):
            pass

        def find_upper_index(self, key):
            l = 0
            r = len(self.keys)
            while (l < r):
                mid = l + (r - l) // 2
                if (self.keys[mid] > key):
                    r = mid
                elif (self.keys[mid] < key):
                    l = mid + 1
                else:
                    l = mid + 1

            return l

        class Direction(Enum):
            LEFT = 0
            RIGHT = 1

        class DeleteInfo:

            def __init__(self, is_delete, is_under):
                self.is_delete = is_delete
                self.is_under = is_under

    # index node
    # non-leaf node

    class BPlusTreeIndexNode(BPlusTreeAbstractNode):

        def __init__(self, keys, vals, tree):
            super().__init__(keys, vals, tree)

        def get(self, key):
            idx = self.find_upper_index(key)
            return self.vals[idx].get(key)

        def set(self, key, val):
            idx = self.find_upper_index(key)
            splitted_key, newnode = self.vals[idx].set(key, val)
            # child does not split
            if newnode is None:
                return None, None

            idx = self.find_upper_index(newnode.keys[0])
            self.keys[idx:idx] = [splitted_key]
            self.vals[idx + 1:idx + 1] = [newnode]
            if len(self.keys) > self.tree.UPPER_BOUND:
                newnode = self.split()
                splitted_key = newnode.keys[0]
                newnode.keys = newnode.keys[1:]
                return splitted_key, newnode

            return None, None

        def remove(self, key):
            idx = self.find_upper_index(key)
            delete_info = self.vals[idx].remove(key)
            # no deletion happen
            if not delete_info.is_delete:
                return delete_info
            # child node become invalid
            if delete_info.is_under:
                self.reorgnize(idx, self.vals[idx]) # child_idx, child_node

            return self.DeleteInfo(True, len(self.keys) < self.tree.LOWER_BOUND)

        def range_query(self, start, end):
            idx = self.find_upper_index(start)
            return self.vals[idx].range_query(start, end)

        def split(self):
            mid = ceil(self.tree.UPPER_BOUND / 2)
            right_node = self.tree.BPlusTreeIndexNode(
                self.keys[mid:], self.vals[mid + 1:], self.tree)
            self.keys = self.keys[:mid]
            self.vals = self.vals[:mid + 1]
            return right_node

        def reorgnize(self, child_idx, child_node):
            # borrow from left brother
            if child_idx > 0 and len(self.vals[child_idx - 1].keys) > self.tree.LOWER_BOUND:
                parrent_key_idx = child_idx - 1
                parrent_key = self.keys[parrent_key_idx]
                new_parent_key = child_node.borrow(
                    self.vals[child_idx - 1], self.Direction.LEFT, parrent_key)
                self.keys[parrent_key_idx] = new_parent_key
            # borrow from right brother
            elif child_idx < len(self.vals) - 1 and len(self.vals[child_idx + 1].keys) > self.tree.LOWER_BOUND:
                parrent_key_idx = child_idx
                parrent_key = self.keys[parrent_key_idx]
                new_parent_key = child_node.borrow(
                    self.vals[child_idx + 1], self.Direction.RIGHT, parrent_key)
                self.keys[parrent_key_idx] = new_parent_key
            # merge
            else:
                if child_idx > 0:
                    parrent_key_idx = child_idx - 1
                    parrent_key = self.keys[parrent_key_idx]
                    self.vals[child_idx - 1].merge(child_node, parrent_key)
                    self.keys.pop(parrent_key_idx)
                    self.vals.pop(child_idx)
                else:
                    # child_idx = 0
                    parrent_key_idx = child_idx
                    parrent_key = self.keys[parrent_key_idx]
                    child_node.merge(self.vals[child_idx + 1], parrent_key)
                    self.keys.pop(parrent_key_idx)
                    self.vals.pop(child_idx + 1)

        def borrow(self, borrowed_node, direction, parrent_key):
            if direction == self.Direction.LEFT:
                self.keys[0:0] = [parrent_key]
                self.vals[0:0] = [borrowed_node.vals.pop(-1)]
                return borrowed_node.keys.pop(-1)
            else:
                self.keys.append(parrent_key)
                self.vals.append(borrowed_node.vals.pop(0))
                return borrowed_node.keys.pop(0)

        def merge(self, merged_node, parrent_key):
            self.keys += [parrent_key] + merged_node.keys
            self.vals += merged_node.vals

    # data node
    # leaf node
    class BPlusTreeDataNode(BPlusTreeAbstractNode):

        def __init__(self, keys, vals, tree):
            super().__init__(keys, vals, tree)
            self.prev = None
            self.next = None

        def get(self, key):
            idx = self.find_equal_index(key)
            if idx == -1:
                raise Exception(f"key {key} not found\n")
            return self.vals[idx]

        def set(self, key, val):
            idx = self.find_equal_index(key)
            # for unique index
            if idx != -1:
                raise Exception(f"key {key} is already exist\n")
            idx = self.find_upper_index(key)
            self.keys[idx:idx] = [key]
            self.vals[idx:idx] = [val]
            self.tree.size += 1
            # split self
            if len(self.keys) > self.tree.UPPER_BOUND:
                newnode = self.split()
                splitted_key = newnode.keys[0]
                return splitted_key, newnode

            return None, None

        def remove(self, key):
            idx = self.find_equal_index(key)
            if idx == -1:
                return self.DeleteInfo(False, False)
            self.keys.pop(idx)
            self.vals.pop(idx)
            self.tree.size -= 1
            return self.DeleteInfo(True, len(self.keys) < self.tree.LOWER_BOUND)

        def range_query(self, start, end):
            ret = {}

            start_idx = self.find_ceiling_index(start)
            end_idx = self.find_ceiling_index(end)
            for i in range(start_idx, end_idx):
                ret[self.keys[i]] = self.vals[i]

            next = self.next
            while next is not None:
                for i in range(0, len(next.keys)):
                    if next.keys[i] < end:
                        ret[next.keys[i]] = next.vals[i]
                    else:
                        return ret
                next = next.next

            return ret

        # produce the right node (self as the left node) ex. "->[1,2,3,4]->" => "->[1,2]->[3,4]->"
        def split(self):
            mid = ceil(self.tree.UPPER_BOUND / 2)
            # for tree
            right_node = self.tree.BPlusTreeDataNode(
                self.keys[mid:], self.vals[mid:], self.tree)
            self.keys = self.keys[:mid]
            self.vals = self.vals[:mid]
            # for linkedlist
            right_node.next = self.next
            if self.next is not None:
                self.next.prev = right_node
            else:
                self.tree.tail = right_node
            self.next = right_node
            right_node.prev = self

            return right_node

        def borrow(self, borrowed_node, direction, parrent_key):
            if direction == self.Direction.LEFT:
                self.keys[0:0] = [borrowed_node.keys.pop(-1)]
                self.vals[0:0] = [borrowed_node.vals.pop(-1)]
                return self.keys[0]
            else:
                self.keys.append(borrowed_node.keys.pop(0))
                self.vals.append(borrowed_node.vals.pop(0))
                return borrowed_node.keys[0]

        def merge(self, merged_node, parrent_key):
            # for tree
            self.keys += merged_node.keys
            self.vals += merged_node.vals
            # for linkedlist
            if merged_node.next is None:
                self.tree.tail = self
            else:
                merged_node.next.prev = self
            self.next = merged_node.next

        def find_equal_index(self, key):
            l = 0
            r = len(self.keys)
            while l < r:
                mid = l + (r - l) // 2
                if (self.keys[mid] == key):
                    return mid
                elif (self.keys[mid] < key):
                    l = mid + 1
                else:
                    r = mid

            return -1

        def find_ceiling_index(self, key):
            l = 0
            r = len(self.keys) - 1
            while (l <= r):
                mid = l + (r - l) // 2
                if key <= mid:
                    r = mid - 1
                else:
                    l = mid + 1
            return l
