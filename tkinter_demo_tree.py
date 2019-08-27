## ref: https://stackoverflow.com/questions/16746387/tkinter-treeview-widget
import os
import tkinter as tk
import tkinter.ttk as ttk

class App(tk.Frame):
    def __init__(self, master, path):
        tk.Frame.__init__(self, master)
        self.tree = ttk.Treeview(self)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.bind("<ButtonRelease-1>", self.treeviewClick)
        folder_name = os.path.basename(path)
        self.tree.heading('#0', text=os.path.basename(folder_name), anchor='w')

        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=folder_name, open=True)
        self.process_directory(root_node, abspath)

        self.tree.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')
        self.grid()

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            oid = self.tree.insert(parent, 'end', text=p, open=False)
            if isdir:
                self.process_directory(oid, abspath)

    def parent_path(self, item, path=''):
        parent_iid = self.tree.parent(item)
        if parent_iid == '':
            return path
        else:
            parent_folder = self.tree.item(parent_iid)['text']
            path = parent_folder + '/' + path
            return self.parent_path(parent_iid, path)

    def treeviewClick(self, event):#单击
        for item in self.tree.selection():
            #item_text = self.tree.item(item, 'text')
            item_path = self.tree.item(item)['text']
            parent_path = self.parent_path(item)  # 输出所选行的第一列的值
            print(os.path.join(parent_path, item_path))


if __name__ == "__main__":
    root = tk.Tk()
    path_to_my_project = "/data/ycy_workspace/GitHub/SenseAD_FT"
    app = App(root, path=path_to_my_project)
    app.mainloop()