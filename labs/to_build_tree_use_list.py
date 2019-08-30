import tkinter as tk
from tkinter import ttk
import os

root = tk.Tk()
tree = ttk.Treeview(root)
ysb = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
xsb = ttk.Scrollbar(root, orient='horizontal', command=tree.xview)
tree.configure(yscroll=ysb.set, xscroll=xsb.set)
tree.heading('#0', text="testFolder", anchor='w')

tree.grid(row=1, column=1)
ysb.grid(row=1, column=2, sticky='ns')
xsb.grid(row=2, column=1, sticky='ew')
root.grid()



folder_name = "/data/ycy_workspace/C++/"
file_list = os.listdir(folder_name)
# root_node = tree.insert('', 'end', text=folder_name, open=True)
# for file in file_list:
#     tree.insert(root_node, 'end', text=file, open=True)


lst = [
    'root/folder1/file1.txt',
    'root/folder1/file2.txt',
    'root/folder1/file3.txt',
    'root/folder2/file1.png',
    'root/folder2/file2.png',
    'root/folder3/folder31/file.txt',
    'root/folder3/file1.json',
    'root/file_inroot.ipynb',
    'root/folder4_empty'
]

def path_lst_to_tree(path_list):
    list(map(build_node, path_list))

def build_node(path):
    path = path.split('/')
    parent = tree.insert('', 'end', text=path[0], open=False)
    for i, p in enumerate(path[:-1]):
        parent = tree.insert(parent, 'end', text=path[i+1], open=False)



path_lst_to_tree(lst)

tree.mainloop()
