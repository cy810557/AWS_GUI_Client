class DirNode:
    def __init__(self, node):
        self.node = node
        self.children = []

    def __repr__(self):
        return '"%s"' % self.node


class DirTree(DirNode):
    def __init__(self, pathList):
        '''

        :param pathList: ['root/folder1/file1.txt',
                           'root/folder1/file2.txt',
                           'root/folder2']
        '''
        pathList = [x.split('/') for x in pathList]
        self.root = DirNode(pathList[0][0])
        # user __repr__ of parent class
        super(DirTree, self).__init__(pathList[0][0])
        self.pathList = [x[1:] for x in pathList]

    def build(self):
        for path in self.pathList:
            self.grow(self.root, path)

    def grow(self, root, path):
        for p in path:
            children_name = [x.node for x in root.children]
            if p in children_name:
                root = root.children[-1]
                continue
            root.children.append(DirNode(p))
            root = root.children[-1]


def is_s3_dir(s3node):
    return True if len(s3node.children) != 0 else False


if __name__ == "__main__":
    lst = [
        'user/root/folder1/file1.txt',
        'user/root/folder1/file2.txt',
        'user/root/folder1/file3.txt',
        'user/root/folder2/file1.png',
        'user/root/folder2/file2.png',
        'user/root/folder3/folder31/file.txt',
        'user/root/folder3/file1.json',
        'user/root/file_inroot.ipynb',
        'user/root/folder4_empty',
        'user/chiyuan/test_folder/'
    ]
    tree = DirTree(lst)
    tree.build()
    print(tree)
    print(tree.root.children)
    print(tree.root.children[0].children)

