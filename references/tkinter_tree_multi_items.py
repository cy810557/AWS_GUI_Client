import tkinter as tk
import tkinter.ttk

def select():
    curItems = tree.selection()
    tk.Label(root, text="\n".join([str(tree.item(i)['values']) for i in curItems])).pack()

root = tk.Tk()
tree = tkinter.ttk.Treeview(root, height=4)

tree['show'] = 'headings'
tree['columns'] = ('Badge Name', 'Requirement', 'Cost', 'Difficulty')
tree.heading("#1", text='Badge Name', anchor='w')
tree.column("#1", stretch="no")
tree.heading("#2", text='Requirement', anchor='w')
tree.column("#2", stretch="no")
tree.heading("#3", text='Cost', anchor='w')
tree.column("#3", stretch="no")
tree.heading("#4", text='Difficulty', anchor='w')
tree.column("#4", stretch="no")
tree.pack()

tree.insert("", "end", values=["IT Badge", "Track Computer", "$1.50", "2"])
tree.insert("", "end", values=["Selfless Badge", "Track Yourself", "$100.50", "10"])
tree.insert("", "end", values=["Tracking Badge", "Track Animal", "$4.50", "7"])

tree.bind("<Return>", lambda e: select())

root.mainloop()