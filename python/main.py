from b_plus_tree import BPlusTree


class UnitTest:
    def __init__(self, degree):
        self.degree = degree

    def insert_test(self,
                    insert_list=[
                        [1, 'a'],
                        [2, 'b'],
                        [3, 'c'],
                        [4, 'd'],
                        [5, 'e'],
                        [6, 'f'],
                        [7, 'g'],
                        [8, 'h'],
                        [9, 'i'],
                        [10, 'j'],
                        [11, '1a'],
                        [12, '1b'],
                        [13, '1c'],
                        [14, '1d'],
                        [15, '1e'],
                        [16, '1f'],
                    ]):
        print('Insert Test: ')
        tree = BPlusTree(self.degree)
        for key, val in insert_list:
            print(f'Insert: Key [{key}] Value [{val}]')
            tree.insert(key, val)
        tree.print_tree(tree.root, "\n")
        return tree

    def find_test(self,
                  insert_list=[[1, 'hello'], [5, 'leetcode'],
                               [7, 'lab'], [8, 'world']],
                  find_list=[7, 3]):
        print('Find Test: ')
        tree = self.insert_test(insert_list)
        for key in find_list:
            try:
                print(f'Find key {key}: ', tree.find(key))
            except:
                print(f"key {key} not found")

    def delete_test(self,
                    insert_list=[
                        [1, 'a'],
                        [2, 'b'],
                        [3, 'c'],
                        [4, 'd'],
                        [5, 'e'],
                        [6, 'f'],
                        [7, 'g'],
                        [8, 'h'],
                        [9, 'i'],
                        [10, 'j'],
                        [11, '1a'],
                        [12, '1b'],
                        [13, '1c'],
                        [14, '1d'],
                        [15, '1e'],
                        [16, '1f'],
                    ],
                    delete_list=[1, 2, 3, 16, 9, 5]
                    ):
        tree = self.insert_test(insert_list)
        print('-' * 40)
        print('Delete Test: ')
        print('-' * 40)
        for key in delete_list:
            tree.delete(key)
            tree.print_tree(tree.root, "\n")
            print('-' * 40)

if __name__ == "__main__":
    Test = UnitTest(5)
    Test.insert_test()
    print("*" * 40)
    Test.delete_test()
    print("*" * 40)
    Test.find_test()
