#! /usr/bin/python3
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.ttk import Treeview, Scrollbar
from os import listdir, remove, execl
from shutil import rmtree, make_archive
from getpass import getuser, getpass
from os.path import isdir, basename, join, abspath
from time import sleep
import os
from sys import executable, argv
from s3_utils.simple_tree import DirTree, is_s3_dir
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError as e:
    print("Unable to import boto3\n%s" % e)
    exit()


class S3Zilla:
    def __init__(self, master):
        #Frame.__init__(self, master)
        # self.service_name = 's3'
        # self.use_ssl = False
        # self.endpoint_url = 'http://10.5.41.189:9090'
        # self.ak = 'O3X91G71GPGA4QG36V28'
        # self.sk = 'qA1FpiOuNUqDxq3vOiTZDispICubnLi29PRuexqG'
        
        ### 测试
        self.service_name = 's3'
        self.use_ssl = False
        self.endpoint_url = 'http://10.5.41.14:7480'
        self.ak = 'HH4QU2FLODUU5P991G47'
        self.sk = 'WrnVmVf9CpAwrWR5CPWELmAvksjeyYMqn1koY4q0'
        error_msg = "Ensure S3 is configured on your machine:"
        try:
            self.s3 = boto3.resource(service_name=self.service_name,
                                     use_ssl=self.use_ssl,
                                     endpoint_url=self.endpoint_url,   
                                     aws_access_key_id = self.ak,
                                     aws_secret_access_key = self.sk)
        except Exception as e:
            print("%s: %s" % (error_msg, e))
            exit(1)
        try:
            self.s3c = boto3.client(service_name=self.service_name,
                                     use_ssl=self.use_ssl,
                                     endpoint_url=self.endpoint_url,   
                                     aws_access_key_id = self.ak,
                                     aws_secret_access_key = self.sk)
        except Exception as err:
            print("%s: %s" % (error_msg, err))
            exit(1)
        self.colors = {
            'light-grey': '#D9D9D9',
            'blue': '#2B547E',
            'black': '#000000',
            'red': '#FF3346',
            'grey': '#262626',
            'cyan': '#80DFFF'
        }
        self.master = master
        self.master.title("商汤科技 aws S3 File Transfer Client")
        self.master.configure(bg=self.colors['grey'])
        self.master.geometry("885x645")
        menu = Menu(self.master)
        menu.config(
            background=self.colors['grey'],
            fg=self.colors['light-grey']
        )
        self.master.config(menu=menu)
        file = Menu(menu)
        file.add_command(
            label="Exit",
            command=self.quit
        )
        menu.add_cascade(
            label="File",
            menu=file
        )
        refresh = Menu(menu)
        refresh.add_command(
            label="Local",
            command=self.refresh_local
        )
        refresh.add_command(
            label="S3",
            command=self.refresh_s3
        )
        menu.add_cascade(label="Refresh", menu=refresh)
        self.dir, self.drp_sel, self.bucket_name = '', '', ''
        self.folder_path = StringVar()
        self.dropdown = StringVar()
        self.dropdown_data = self.populate_dropdown()
        if not self.dropdown_data:
            self.dropdown_data = ['none available']
        self.deleted = False
        self.local_sel, self.s3_sel = ([] for i in range(2))
        self.title_label = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            font="Helvetica 10 bold",
            width=120
        )
        self.local_label = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            text="LOCAL FILE SYSTEM",
            font="Helvetica 10 bold underline",
            width=60
        )
        self.s3_label = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            text="AMAZON  S3",
            font="Helvetica 10 bold underline",
            underline=True,
            width=60
        )
        self.dropdown_box = OptionMenu(
            master,
            self.dropdown,
            *self.dropdown_data,
            command=self.set_drop_val
        )
        self.dropdown_box.configure(
            fg=self.colors['light-grey'],
            bg=self.colors['blue'],
            width=27,
            highlightbackground=self.colors['black'],
            highlightthickness=2
        )
        self.browse_button = Button(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['blue'],
            text="Browse",
            width=30,
            highlightbackground=self.colors['black'],
            highlightthickness=2,
            command=self.load_dir
        )
        self.browse_label = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            text="No directory selected",
            width=37,
            font="Helvetica 10"
        )
        self.bucket_label = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            text="No bucket selected",
            width=37,
            font="Helvetica 10"
        )
        self.refresh_btn_local = Button(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['blue'],
            text="REFRESH",
            width=30,
            highlightbackground=self.colors['black'],
            highlightthickness=2,
            command=self.refresh_local
        )
        self.refresh_btn_s3 = Button(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['blue'],
            text="REFRESH",
            width=30,
            highlightbackground=self.colors['black'],
            highlightthickness=2,
            command=self.refresh_s3
        )
        self.explorer_label_local = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['blue'],
            width=30,
            text="Local File System:  "
        )
        self.explorer_label_s3 = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['black'],
            width=30,
            text="S3 File System"
        )
        ### 鼠标点击的项目列表
        # self.ex_loc = Listbox(
        #     master,
        #     fg=self.colors['cyan'],
        #     bg=self.colors['black'],
        #     width=49,
        #     height=18,
        #     highlightcolor=self.colors['black'],
        #     selectmode="multiple",
        #     exportselection=0
        # )


        # self.ex_s3 = Listbox(     # use TreeView instead
        #     master,
        #     fg=self.colors['cyan'],
        #     bg=self.colors['black'],
        #     width=49,
        #     height=18,
        #     highlightcolor=self.colors['black'],
        #     selectmode="multiple",
        #     exportselection=0
        # )

        self.upload_button = Button(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['blue'],
            text="Upload ->",
            width=20,
            highlightbackground=self.colors['black'],
            highlightthickness=2,
            command=self.upload
        )
        self.download_button = Button(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['blue'],
            text="<- Download",
            width=20,
            highlightbackground=self.colors['black'],
            highlightthickness=2,
            command=self.download
        )
        self.delete_local = Button(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['red'],
            text="DELETE",
            width=20,
            highlightbackground=self.colors['black'],
            command=self.delete_local_records
        )
        self.delete_s3 = Button(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['red'],
            text="DELETE",
            width=20,
            highlightbackground=self.colors['black'],
            command=self.delete_s3_records
        )
        self.found_label_local = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            text="found local",
            width=54
        )
        self.found_label_s3 = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            text="found s3",
            width=54
        )
        self.status_label = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            text="Hello " + getuser(),
            width=54
        )
        self.create_bucket_label = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            text="New Bucket:",
        )
        self.create_bucket_name = Text(
            master,
            fg=self.colors['cyan'],
            bg=self.colors['black'],
            width=25,
            height=1
        )
        self.create_bucket_button = Button(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['blue'],
            text="Create",
            width=5,
            highlightbackground=self.colors['black'],
            highlightthickness=2,
            command=self.create_bucket
        )
        ## Chiyuan Custom
        self.create_dir_label = Label(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['grey'],
            text="New Folder:",
        )
        self.create_dir_name = Text(
            master,
            fg=self.colors['cyan'],
            bg=self.colors['black'],
            width=15,
            height=1
        )
        self.create_dir_button = Button(
            master,
            fg=self.colors['light-grey'],
            bg=self.colors['blue'],
            text='Create',
            width=3,
            highlightbackground=self.colors['black'],
            highlightthickness=2,
            command=self.create_dir
        )

        # ####### begin grid placement ####### #
        self.title_label.grid(
            row=0,
            sticky=E+W,
            padx=20,
            pady=5
        )
        self.local_label.grid(
            row=0,
            sticky=W,
            padx=8,
            pady=5
        )
        self.s3_label.grid(
            row=0,
            sticky=E,
            padx=0,
            pady=5
        )
        self.browse_button.grid(
            row=1,
            sticky=W,
            padx=86,
            pady=10
        )
        self.dropdown_box.grid(
            row=1,
            sticky=E,
            padx=86,
            pady=5
        )
        self.browse_label.grid(
            row=2,
            sticky=W,
            padx=86,
            pady=5
        )
        self.bucket_label.grid(
            row=2,
            sticky=E,
            padx=86,
            pady=5
        )
        self.refresh_btn_local.grid(
            row=3,
            sticky=W,
            padx=86,
            pady=10
        )
        self.refresh_btn_s3.grid(
            row=3,
            sticky=E,
            padx=86,
            pady=10
        )
        self.explorer_label_local.grid(
            row=4,
            sticky=W,
            padx=20
        )
        self.explorer_label_s3.grid(
            row=4,
            sticky=E,
            padx=20
        )
        # self.ex_loc_tree.grid(
        #     row=4,
        #     sticky=W,
        #     padx=20
        # )
        # self.ex_s3.grid(
        #     row=4,
        #     sticky=E,
        #     padx=20
        # )
        self.upload_button.grid(
            row=5,
            sticky=W,
            padx=224,
            pady=0
        )
        self.download_button.grid(
            row=5,
            sticky=E,
            padx=224,
            pady=0
        )
        self.delete_local.grid(
            row=5,
            sticky=W,
            padx=20,
            pady=0
        )
        self.delete_s3.grid(
            row=5,
            sticky=E,
            padx=20,
            pady=0
        )
        self.found_label_local.grid(
            row=6,
            sticky=W,
            padx=0,
            pady=20
        )
        self.found_label_s3.grid(
            row=6,
            sticky=E,
            padx=0,
            pady=20
        )
        self.status_label.grid(
            row=7,
            sticky=W,
            padx=0,
            pady=20
        )
        self.create_bucket_label.grid(
            row=7,
            sticky=E,
            padx=330,
            pady=0
        )
        self.create_bucket_name.grid(
            row=7,
            sticky=E,
            padx=100,
            pady=0
        )
        self.create_bucket_button.grid(
            row=7,
            sticky=E,
            padx=20,
            pady=0
        )
        ## Chiyuan Customize
        self.create_dir_label.grid(
            row=8,
            sticky=E,
            padx=330,
            pady=0
        )
        self.create_dir_name.grid(
            row=8,
            sticky=E,
            padx=100,
            pady=0
        )
        self.create_dir_button.grid(
            row=8,
            sticky=E,
            padx=20,
            pady=0
        )
        # n1 = "%s files found" % str(self.ex_loc_tree.size())
        # self.set_found_local_label(n1)
        # n2 = "%s files found" % str(self.ex_s3.size())
        # self.set_found_s3_label(n2)

    def quit(self):
        exit()

    # def get_local_sel(self):
    #     items = self.ex_loc_tree.selection()
    #     parents = [self.parent_path(item) for item in items]
    #     item_text = [self.ex_loc_tree.item(i)['text'] for i in items]
    #     return [join(p, i) for p, i in zip(parents, item_text)]

    def get_tree_sel(self, tv_obj):
        items = tv_obj.selection()
        parents = [self.parent_path(tv_obj, item) for item in items]
        item_text = [tv_obj.item(i)['text'] for i in items]
        return [join(p, i) for p, i in zip(parents, item_text)]

    # def get_s3_sel(self):
    #     return [self.ex_s3.get(i) for i in self.ex_s3.curselection()]

    def set_drop_val(self, selection):
        self.drp_sel = selection

    def delete_local_records(self):
        files = self.get_local_sel()
        if not files:
            message = "Please select a file(s) to delete"
            self.set_status_label(message)
        else:
            self.del_local(files)

    def del_local(self, files_remaining):
        if len(files_remaining) > 0:
            f = files_remaining.pop(0)
            if not isdir(self.dir + "/" + f):
                try:
                    remove("%s/%s" % (self.dir, f))
                except Exception as err:
                    self.set_status_label("%s" % err)
                    self.status_label.update_idletasks()
                self.del_local(files_remaining)
            else:
                try:
                    rmtree("%s/%s" % (self.dir, f))
                except Exception as e:
                    self.set_status_label("%s" % e)
                    self.status_label.update_idletasks()
                self.del_local(files_remaining)
        self.deleted = True
        self.refresh_local()

    def delete_s3_records(self):
        removal = ''
        if not self.drp_sel:
            m = "Please select a bucket..."
            self.set_status_label(m)
        else:
            removal = self.get_s3_sel()
        if not removal:
            m = "Please select at least 1 object to delete"
            self.set_status_label(m)
        else:
            bucket = self.s3.Bucket(self.drp_sel)
            for rm in removal:
                for k in bucket.objects.all():
                    if k.key != rm:
                        continue
                    k.delete()
                    break
            self.deleted = True
            self.refresh_s3()

    def load_dir(self):
        self.dir = askdirectory()
        self.init_local_tree()
        self.set_local_browse_label(self.dir)
        #self.refresh_local()

    def refresh_local(self):
        if not self.dir:
            m = "Use the browse button to select a directory"
            self.set_status_label(m)
        else:
            self.set_local_browse_label(self.dir)
            #self.ex_loc_tree.delete(0, 'end')
            x = self.dir + "/"
            d = [f if not isdir(x+f) else f + '/' for f in sorted(listdir(x))]
            self.ex_loc_tree.insert('end', *d)
            if not self.deleted:
                m = "Hello %s" % getuser()
            else:
                m = "FINISHED DELETING"
                self.deleted = False
            self.set_status_label(m)
            n = "%s files found" % str(self.ex_loc_tree.size())
            self.set_found_local_label(n)

    def refresh_s3(self):
        if 'none available' in self.dropdown_data:
            m = "Please create at least one S3 bucket"
            self.set_status_label(m)
        elif not self.drp_sel:
            m = "Please select a bucket from the drop-down list"
            self.set_status_label(m)
        else:
            self.init_s3_tree()

            #self.ex_s3_tree.delete(0, 'end')
            #self.s3_file_list = self.get_bucket_contents()
            #self.ex_s3.insert('end', *self.get_bucket_contents())
            self.set_status_label("Hello %s" % getuser())
            self.set_s3_bucket_label(self.drp_sel)
            n = "%s files found" % str(self.ex_s3_tree.size())
            self.set_found_s3_label(n)
            self.found_label_s3.update_idletasks()
            if not self.deleted:
                m = "Hello %s" % getuser()
            else:
                m = "FINISHED DELETING"
                self.deleted = False
            self.set_status_label(m)

    def finished(self, incoming_message):
        d = "FINISHED %s" % incoming_message
        for letter in enumerate(d):
            self.set_status_label(d[0:letter[0] + 1])
            self.status_label.update_idletasks()
            sleep(.1)

    def upload(self):
        if not self.drp_sel or not self.dir:
            m = "Ensure a local path and S3 bucket are selected"
            self.set_status_label(m)
        #elif not self.get_local_sel():
        elif not self.get_tree_sel(self.ex_loc_tree):
            m = "Ensure files are selected to upload"
            self.set_status_label(m)
        else:
            #s3_sel_path = self.get_s3_sel()[0]
            s3_sel_path = self.get_tree_sel(self.ex_s3_tree)[0]
            # if not isdir(s3_sel_path):
            #     m = "Ensure target path is a directory"
            #     self.set_status_label(m)
            for selection in self.get_tree_sel(self.ex_loc_tree):
                file_ = os.path.split(os.path.abspath(self.dir))[0]
                file_ = join(file_, selection)
                if not isdir(file_):
                    s3_sel_path_ = s3_sel_path[len(self.drp_sel)+1:]
                    self.s3c.upload_file(file_, self.drp_sel, join(s3_sel_path_, basename(file_)))
                else:
                    s3_target = 's3://' + join(s3_sel_path, basename(file_))
                    self.upload_folder(file_, s3_target)
                m = "Uploaded: %s" % selection
                self.set_status_label(m)
                self.status_label.update_idletasks()
            self.refresh_s3()
            self.finished("UPLOAD")

    def download(self):
        if not self.drp_sel or not self.dir:
            m = "Ensure a file and bucket have been selected"
            self.set_status_label(m)
        elif not self.get_s3_sel():
            m = "Ensure files are selected to download"
            self.set_status_label(m)
        else:
            for selection in self.get_s3_sel():
                file_ = "%s/%s" % (self.dir, selection)
                self.s3c.download_file(self.drp_sel, selection, file_)
            self.refresh_local()
            self.finished("DOWNLOAD")

    def get_bucket_contents(self):
        bucket = self.s3.Bucket(self.drp_sel)
        return [s3_file.key for s3_file in bucket.objects.all()]

    def populate_dropdown(self):
        return [bucket.name for bucket in self.s3.buckets.all()]

    def set_local_browse_label(self, incoming):
        if len(incoming) > 35:
            self.browse_label.config(text=basename(incoming) + '/')
        else:
            self.browse_label.config(text=incoming)

    def set_s3_bucket_label(self, incoming):
        self.bucket_label.config(text=incoming)

    def set_status_label(self, incoming):
        self.status_label.config(text=incoming)

    def set_found_local_label(self, incoming):
        self.found_label_local.config(text=incoming)

    def set_found_s3_label(self, incoming):
        self.found_label_s3.config(text=incoming)

    def create_bucket(self):
        self.bucket_name = self.create_bucket_name.get("1.0", END).strip()
        if not self.bucket_name:
            m = "Please enter a new bucket name"
            self.set_status_label(m)
        else:
            pre_exists = False
            try:
                self.s3.create_bucket(Bucket=self.bucket_name)
            except ClientError as ce:
                pre_exists = True
                m = "Bucket name is already in use. "
                m += "Choose a different name."
                self.set_status_label(m)
            if not pre_exists:
                m = "%s created: restarting..." % self.bucket_name
                self.set_status_label(m)
                self.status_label.update_idletasks()
                res = executable
                execl(res, res, *argv)

    # Chiyuan Customize
    def create_dir(self):
        new_path = self.create_dir_name.get("1.0", END).strip()
        if not new_path:
            m = "Please enter a new path"
            self.set_status_label(m)
        else:
            bucket = self.s3.Bucket(self.drp_sel)
            bucket.put_object(Bucket=bucket.name, Key=join(new_path, '.dir_maker'))

            self.refresh_s3()

    def treeviewClick(self, event, tv_obj=None, s3=False):
        for item in tv_obj.selection():
            item_path = tv_obj.item(item)['text']
            parent_path = self.parent_path(tv_obj, item)  # 输出所选行的第一列的值
            if s3:
                print('s3://' + join(parent_path, item_path))
            else:
                print(join(parent_path, item_path))

    def init_local_tree(self):
        self.ex_loc_tree = Treeview(self.master)
        ysb = Scrollbar(self.master, orient='vertical', command=self.ex_loc_tree.yview)
        xsb = Scrollbar(self.master, orient='horizontal', command=self.ex_loc_tree.xview)
        self.ex_loc_tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        # self.ex_loc_tree.grid(
        #     row=100,
        #     sticky=W,
        #     padx=20
        # )
        n1 = "%s files found" % str(self.ex_loc_tree.size())
        self.set_found_local_label(n1)
        self.ex_loc_tree.bind("<ButtonRelease-1>",
                              lambda event, tv_obj=self.ex_loc_tree:
                                self.treeviewClick(event, tv_obj))
        folder_name = basename(self.dir)
        self.ex_loc_tree.heading('#0', text=basename(folder_name), anchor='w')

        abs_path = abspath(self.dir)
        root_node = self.ex_loc_tree.insert('', 'end', text=folder_name, open=True)
        self.process_loc_dir(root_node, abs_path)

        self.ex_loc_tree.grid(row=0, column=0)
        # Set Scrollbar
        # ysb.grid(row=0, column=1, sticky='ns')
        # xsb.grid(row=1, column=0, sticky='ew')
        self.master.grid()

    def init_s3_tree(self):
        self.ex_s3_tree = Treeview(self.master)
        self.ex_s3_tree.column('#0', minwidth=500, stretch=0)
        self.ex_s3_tree.heading('#0', text=self.drp_sel, anchor='w')

        ysb = Scrollbar(self.master, orient='vertical', command=self.ex_s3_tree.yview)
        xsb = Scrollbar(self.master, orient='horizontal', command=self.ex_s3_tree.xview)
        self.ex_s3_tree.configure(yscroll=ysb.set, xscroll=xsb.set)

        n1 = "%s files found" % str(self.ex_s3_tree.size())
        self.ex_s3_tree.grid(
            row=4,
            sticky=E,
            padx=100
        )
        self.set_found_s3_label(n1)
        self.ex_s3_tree.bind("<ButtonRelease-1>",
                             lambda event, tv_obj=self.ex_s3_tree, s3=True:
                                self.treeviewClick(event, tv_obj, s3))

        self.build_s3_tree()

        self.ex_s3_tree.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')

        self.master.grid()

    def process_loc_dir(self, parent, path):
        '''
        :param parent: parent node(TreeView object), used to insert treeview node
        :param path: string object, used to get children strings.
        '''
        for p in listdir(path):
            abspath = join(path, p)
            is_dir = os.path.isdir(abspath)
            oid = self.ex_loc_tree.insert(parent, 'end', text=p, open=False)
            if is_dir:
                self.process_loc_dir(oid, abspath)

    def parent_path(self, tv_obj, item, path=''):
        '''
        Get parent path recursivly.
        Key ref: https://stackoverflow.com/questions/43681006/python-tkinter-treeview-get-return-parent-name-of-selected-item

        :param item: base item
        :param path: not required when first pass
        :return: parent path of the current item
        '''

        parent_iid = tv_obj.parent(item)
        if parent_iid == '':
            return path
        else:
            parent_folder = tv_obj.item(parent_iid)['text']
            path = parent_folder + '/' + path
            return self.parent_path(tv_obj, parent_iid, path)

    def upload_folder(self, folder_path, s3_sel_path):
        # os.system('bash s3_utils/upload_folder.sh {} {} {}'.format(
        #     folder_path, self.drp_sel, s3_sel_path)
        # )
        cmd = 'aws --endpoint-url={} s3 --profile test cp {} {} --recursive'.format(
            self.endpoint_url,
            folder_path,
            s3_sel_path
        )
        os.system(cmd)

    def process_s3_dir(self, par_treeview_node, par_treedir_node):
        '''
        Process s3 dir iteratively and build treeview structure.
        :param parent: parent node(TreeView object), used to insert treeview node
        :param s3_node: parent node(DirTree object), used to get children nodes.
        '''
        children = par_treedir_node.children
        for p in children:
            is_dir = is_s3_dir(p)
            if is_dir:
                ####################    Key Error! Comment parent node modified in loop!       ###############
                #par_treeview_node = self.ex_s3_tree.insert(par_treeview_node, 'end', text=p.node, open=False)

                par_treeview_node_1 = self.ex_s3_tree.insert(par_treeview_node, 'end', text=p.node, open=False)
                self.process_s3_dir(par_treeview_node_1, p)
            else:
                self.ex_s3_tree.insert(par_treeview_node, 'end', text=p.node, open=False)

    def build_s3_tree(self):
        self.s3_file_list = self.get_bucket_contents()
        s3_file_list = [join(self.drp_sel, x) for x in self.s3_file_list]
        self.s3_file_tree = DirTree(s3_file_list)
        self.s3_file_tree.build()

        root_folder = self.s3_file_tree.node
        par_treedir_node = self.s3_file_tree.root
        par_treeview_node = self.ex_s3_tree.insert('', 'end', text=root_folder, open=False)
        self.process_s3_dir(par_treeview_node, par_treedir_node)




if __name__ == "__main__":
    root = Tk()
    s3_zilla = S3Zilla(root)
    root.mainloop()
