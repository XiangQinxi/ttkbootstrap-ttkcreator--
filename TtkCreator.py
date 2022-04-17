"""
汉化作者：XiangQinxi

"""


import shutil
import json
from uuid import uuid4
from pathlib import Path
import ttkbootstrap as ttk
from tkinter import Frame
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askopenfilename, asksaveasfilename
from ttkbootstrap.themes import standard, user
from ttkbootstrap.style import ThemeDefinition
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import *
from ttkbootstrap.dialogs import Messagebox


class ThemeCreator(ttk.Window):
    def __init__(self):
        super().__init__("ttk 主题创建器")
        self.configure_frame = ttk.Frame(self, padding=(10, 10, 5, 10))
        self.configure_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        self.demo_frame = ttk.Frame(self, padding=(5, 10, 10, 10))
        self.demo_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        self.setup_theme_creator()
        self.demo_widgets = DemoWidgets(self, self.style)
        self.demo_widgets.pack(fill=BOTH, expand=YES)

    def setup_theme_creator(self):
        # application menu
        self.menu = ttk.Menu()
        self.theme_menu = ttk.Menu()
        self.theme_menu.add_cascade(label="主题", menu=self.menu)
        self.menu.add_command(label="保存", command=self.save_theme)
        self.menu.add_command(label="重置", command=self.change_base_theme)
        self.menu.add_command(label="导入", command=self.import_user_themes)
        self.menu.add_command(label="导出", command=self.export_user_themes)
        self.about_menu = ttk.Menu()
        self.about_menu.add_command(label="关于作者", command=self.about_dialog)
        self.theme_menu.add_cascade(label="关于", menu=self.about_menu)
        self.configure(menu=self.theme_menu)

        # theme configuration settings
        ## user theme name
        f1 = ttk.Frame(self.configure_frame, padding=(5, 2))
        ttk.Label(f1, text="名字", width=12).pack(side=LEFT)
        self.theme_name = ttk.Entry(f1)
        ToolTip(self.theme_name, text="主题名字", bootstyle=(PRIMARY, INVERSE))
        self.theme_name.insert(END, "新主题")
        self.theme_name.pack(side=LEFT, fill=X, expand=YES)
        f1.pack(fill=X, expand=YES)

        ## base theme
        f2 = ttk.Frame(self.configure_frame, padding=(5, 2))
        ttk.Label(f2, text="基本主题", width=12).pack(side=LEFT)
        self.base_theme = ttk.Combobox(f2, values=self.style.theme_names())
        ToolTip(self.base_theme, text="主题基本模板", bootstyle=(PRIMARY, INVERSE))
        self.base_theme.insert(END, "litera")
        self.base_theme.pack(side=LEFT, fill=X, expand=YES)
        f2.pack(fill=X, expand=YES, pady=(0, 15))
        self.base_theme.bind("<<ComboboxSelected>>", self.change_base_theme)

        ## color options
        self.color_rows = []
        for color in self.style.colors.label_iter():
            row = ColorRow(self.configure_frame, color, self.style)
            self.color_rows.append(row)
            ToolTip(row, text="主题配置", bootstyle=(PRIMARY, INVERSE))
            row.pack(fill=BOTH, expand=YES)
            row.bind("<<ColorSelected>>", self.create_temp_theme)

    def about_dialog(self):
        self.ad = Messagebox.ok(message="原作者：israel-dryer\n汉化作者: XiangQinxi\nttkbootstrap版本：1.7.4", title="关于汉化作者")

    def create_temp_theme(self, *_):
        """Creates a temp theme using the current configure settings and
        changes the theme in tkinter to that new theme.
        """
        themename = "temp_" + str(uuid4()).replace("-", "")[:10]
        colors = {}
        for row in self.color_rows:
            colors[row.label["text"]] = row.color_value
        definition = ThemeDefinition(themename, colors, self.style.theme.type)
        self.style.register_theme(definition)
        self.style.theme_use(themename)
        self.update_color_patches()

    def change_base_theme(self, *_):
        """Sets the initial colors used in the color configuration"""
        themename = self.base_theme.get()
        self.style.theme_use(themename)
        self.update_color_patches()

    def update_color_patches(self):
        """Updates the color patches next to the color code entry."""
        for row in self.color_rows:
            row.color_value = self.style.colors.get(row.label["text"])
            row.update_patch_color()

    def export_user_themes(self):
        """Export user themes saved in the user.py file"""
        inpath = Path(user.__file__)
        outpath = asksaveasfilename(
            initialdir="/",
            initialfile="user.py",
            filetypes=[("python", "*.py")],
        )
        if outpath:
            shutil.copyfile(inpath, outpath)
            Messagebox.ok(
                parent=self,
                title="导出",
                message="用户主题已被导出。",
            )

    def import_user_themes(self):
        """Import user themes into the user.py file. Any existing data
        in the user.py file will be overwritten."""
        outpath = Path(user.__file__)
        inpath = askopenfilename(
            initialdir="/",
            initialfile="user.py",
            filetypes=[("python", "*.py")],
        )
        confirm = Messagebox.okcancel(
            title="导入",
            message="导入将覆盖现有的用户主题。要导入吗？",
        )
        if confirm == "OK" and inpath:
            shutil.copyfile(inpath, outpath)
            Messagebox.ok(
                parent=self,
                title="导出",
                message="用户主题已导入。",
            )

    def save_theme(self):
        """Save the current settings as a new theme. Warn using if
        saving will overwrite existing theme."""
        name = self.theme_name.get().lower().replace(" ", "")

        if name in user.USER_THEMES:
            result = Messagebox.okcancel(
                title="保存主题",
                alert=True,
                message=f"覆盖现有主题 {name}?",
            )
            if result == "Cancel":
                return

        colors = {}
        for row in self.color_rows:
            colors[row.label["text"]] = row.color_value

        theme = {name: {"type": self.style.theme.type, "colors": colors}}
        user.USER_THEMES.update(theme)
        standard.STANDARD_THEMES[name] = theme[name]

        # save user themes to file
        formatted = json.dumps(user.USER_THEMES, indent=4)
        out = 'USER_THEMES = ' + formatted
        filepath = user.__file__
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(out)

        definition = ThemeDefinition(name, colors, self.style.theme.type)
        self.style.register_theme(definition)
        self.style.theme_use(name)
        new_themes = []
        for themename in self.style.theme_names():
            if not themename.startswith("temp"):
                new_themes.append(themename)
        self.base_theme.configure(values=new_themes)
        Messagebox.ok(f"主题 {name} 已经创建完成", "保存主题")


class ColorRow(ttk.Frame):
    def __init__(self, master, color, style):
        super().__init__(master, padding=(5, 2))
        self.colorname = color
        self.style = style

        self.label = ttk.Label(self, text=color, width=12)
        self.label.pack(side=LEFT)
        self.patch = Frame(
            master=self, background=self.style.colors.get(color), width=15
        )
        self.patch.pack(side=LEFT, fill=BOTH, padx=2)
        self.entry = ttk.Entry(self, width=12)
        self.entry.pack(side=LEFT, fill=X, expand=YES)
        self.entry.bind("<FocusOut>", self.enter_color)
        self.color_picker = ttk.Button(
            master=self,
            text="...",
            bootstyle=SECONDARY,
            command=self.pick_color,
        )
        self.color_picker.pack(side=LEFT, padx=2)

        # set initial color value and patch color
        self.color_value = self.style.colors.get(color)
        self.update_patch_color()

    def pick_color(self):
        """Callback for when a color is selected from the color chooser"""
        color = askcolor(color=self.color_value)
        if color[1]:
            self.color_value = color[1]
            self.update_patch_color()
        self.event_generate("<<ColorSelected>>")

    def enter_color(self, *_):
        """Callback for when a color is typed into the entry"""
        try:
            self.color_value = self.entry.get().lower()
            self.update_patch_color()
        except:
            self.color_value = self.style.colors.get(self.label["text"])
            self.update_patch_color()
        self.event_generate("<<ColorSelected>>")

    def update_patch_color(self):
        """Update the color patch frame with the color value stored in
        the entry widget."""
        self.entry.delete(0, END)
        self.entry.insert(END, self.color_value)
        self.patch.configure(background=self.color_value)


class DemoWidgets(ttk.Frame):
    """Builds a frame containing an example of most ttkbootstrap widgets
    with various styles and states applied.
    """

    ZEN = """美胜于丑。
    显性比隐性好。
    简单总比复杂好。
    复杂总比隐晦好
    平的比嵌套的好。
    稀疏比密集好。
    可读性很重要。
    特殊情况不足以违反规则。
    尽管实用胜过纯洁。
    错误永远不应该悄无声息地过去。
    除非明确沉默。
    面对模棱两可的情况，拒绝猜测的诱惑。
    应该有一种——最好只有一种——显而易见的方法来做到这一点。
    除非一开始你不是很明显。
    现在总比没有好。
    虽然永远不会比现在更好。
    如果实现很难解释，那就不是个好主意。
    如果实现很容易解释，这可能是一个好主意。
    名称空间是一个非常好的主意——让我们做更多的工作吧！"""

    def __init__(self, master, style):
        super().__init__(master)

        self.style: ttk.Style = style
        self.create_left_frame()
        self.create_right_frame()

    def create_right_frame(self):
        container = ttk.Frame(self)
        container.pack(side=RIGHT, fill=BOTH, expand=YES, padx=5)

        # demonstrates various button styles
        btn_group = ttk.Labelframe(
            master=container, text="按钮", padding=(10, 5)
        )
        btn_group.pack(fill=X)

        menu = ttk.Menu(self)
        for i, t in enumerate(self.style.theme_names()):
            menu.add_radiobutton(label=t, value=i)

        default = ttk.Button(master=btn_group, text="实心按钮")
        default.pack(fill=X, pady=5)
        default.focus_set()

        mb = ttk.Menubutton(
            master=btn_group,
            text="实心菜单按钮",
            bootstyle=SECONDARY,
            menu=menu,
        )
        mb.pack(fill=X, pady=5)

        cb = ttk.Checkbutton(
            master=btn_group,
            text="实心工具按钮",
            bootstyle=(SUCCESS, TOOLBUTTON),
        )
        cb.invoke()
        cb.pack(fill=X, pady=5)

        ob = ttk.Button(
            master=btn_group, text="轮廓按钮", bootstyle=(INFO, OUTLINE)
        )
        ob.pack(fill=X, pady=5)

        mb = ttk.Menubutton(
            master=btn_group,
            text="轮廓菜单按钮",
            bootstyle=(WARNING, OUTLINE),
            menu=menu,
        )
        mb.pack(fill=X, pady=5)

        cb = ttk.Checkbutton(
            master=btn_group,
            text="轮廓工具按钮",
            bootstyle="success-outline-toolbutton",
        )
        cb.pack(fill=X, pady=5)

        lb = ttk.Button(master=btn_group, text="链接按钮", bootstyle=LINK)
        lb.pack(fill=X, pady=5)

        cb1 = ttk.Checkbutton(
            master=btn_group,
            text="圆形开关",
            bootstyle=(SUCCESS, ROUND, TOGGLE),
        )
        cb1.invoke()
        cb1.pack(fill=X, pady=5)

        cb2 = ttk.Checkbutton(
            master=btn_group, text="方形开关", bootstyle=(SQUARE, TOGGLE)
        )
        cb2.pack(fill=X, pady=5)
        cb2.invoke()

        input_group = ttk.Labelframe(
            master=container, text="其他输入小部件", padding=10
        )
        input_group.pack(fill=BOTH, pady=(10, 5), expand=YES)
        entry = ttk.Entry(input_group)
        entry.pack(fill=X)
        entry.insert(END, "输入组件")

        password = ttk.Entry(master=input_group, show="•")
        password.pack(fill=X, pady=5)
        password.insert(END, "password")

        spinbox = ttk.Spinbox(master=input_group, from_=0, to=100)
        spinbox.pack(fill=X)
        spinbox.set(45)

        cbo = ttk.Combobox(
            master=input_group,
            text=self.style.theme.name,
            values=self.style.theme_names(),
        )
        cbo.pack(fill=X, pady=5)
        cbo.current(self.style.theme_names().index(self.style.theme.name))

        de = ttk.DateEntry(input_group)
        de.pack(fill=X)

    def create_left_frame(self):
        """Create all the left frame widgets"""
        container = ttk.Frame(self)
        container.pack(side=LEFT, fill=BOTH, expand=YES, padx=5)

        # demonstrates all color options inside a label
        color_group = ttk.Labelframe(
            master=container, text="主题颜色选项", padding=10
        )
        color_group.pack(fill=X, side=TOP)
        for color in self.style.colors:
            cb = ttk.Button(color_group, text=color, bootstyle=color)
            cb.pack(side=LEFT, expand=YES, padx=5, fill=X)

        # demonstrates all radiobutton widgets active and disabled
        cr_group = ttk.Labelframe(
            master=container, text="单击按钮 & 单选按钮", padding=10
        )
        cr_group.pack(fill=X, pady=10, side=TOP)
        cr1 = ttk.Checkbutton(cr_group, text="选中")
        cr1.pack(side=LEFT, expand=YES, padx=5)
        cr1.invoke()
        cr2 = ttk.Checkbutton(cr_group, text="未选中")
        cr2.pack(side=LEFT, expand=YES, padx=5)
        cr3 = ttk.Checkbutton(cr_group, text="失效", state=DISABLED)
        cr3.pack(side=LEFT, expand=YES, padx=5)
        cr4 = ttk.Radiobutton(cr_group, text="选中", value=1)
        cr4.pack(side=LEFT, expand=YES, padx=5)
        cr4.invoke()
        cr5 = ttk.Radiobutton(cr_group, text="取消选择", value=2)
        cr5.pack(side=LEFT, expand=YES, padx=5)
        cr6 = ttk.Radiobutton(
            cr_group, text="失效", value=3, state=DISABLED
        )
        cr6.pack(side=LEFT, expand=YES, padx=5)

        # demonstrates the treeview and notebook widgets
        ttframe = ttk.Frame(container)
        ttframe.pack(pady=5, fill=X, side=TOP)
        table_data = [
            ("South Island, New Zealand", 1),
            ("Paris", 2),
            ("Bora Bora", 3),
            ("Maui", 4),
            ("Tahiti", 5),
        ]
        tv = ttk.Treeview(
            master=ttframe, columns=[0, 1], show="headings", height=5
        )
        ToolTip(tv, text="树视图组件", bootstyle=(PRIMARY, INVERSE))
        for row in table_data:
            tv.insert("", END, values=row)

        tv.selection_set("I001")
        tv.heading(0, text="城市")
        tv.heading(1, text="等价")
        tv.column(0, width=300)
        tv.column(1, width=70, anchor=CENTER)
        tv.pack(side=LEFT, anchor=NE, fill=X)

        nb = ttk.Notebook(ttframe)
        ToolTip(nb, text="笔记本组件", bootstyle=(PRIMARY, INVERSE))
        nb.pack(side=LEFT, padx=(10, 0), expand=YES, fill=BOTH)
        nb_text = (
            "这是一个笔记本标签。\n你能在这里面放入一些你想放入的组件."
        )
        nb.add(ttk.Label(nb, text=nb_text), text="标签 1", sticky=NW)
        nb.add(
            child=ttk.Label(nb, text="一个笔记本的标签"),
            text="标签 2",
            sticky=NW,
        )
        nb.add(ttk.Frame(nb), text="标签 3")
        nb.add(ttk.Frame(nb), text="标签 4")
        nb.add(ttk.Frame(nb), text="标签 5")

        # text widget
        txt = ttk.Text(master=container, height=5, width=50, wrap="none")
        ToolTip(txt, text="文本组件", bootstyle=(PRIMARY, INVERSE))
        txt.insert(END, DemoWidgets.ZEN)
        txt.pack(side=LEFT, anchor=NW, pady=5, fill=BOTH, expand=YES)

        # demonstrates scale, progressbar, and meter, and scrollbar widgets
        lframe_inner = ttk.Frame(container)
        lframe_inner.pack(fill=BOTH, expand=YES, padx=10)
        scale = ttk.Scale(
            master=lframe_inner, orient=HORIZONTAL, value=75, from_=100, to=0
        )
        scale.pack(fill=X, pady=5, expand=YES)

        ttk.Progressbar(
            master=lframe_inner,
            orient=HORIZONTAL,
            value=50,
        ).pack(fill=X, pady=5, expand=YES)

        ttk.Progressbar(
            master=lframe_inner,
            orient=HORIZONTAL,
            value=75,
            bootstyle="success-striped",
        ).pack(fill=X, pady=5, expand=YES)

        m = ttk.Meter(
            master=lframe_inner,
            metersize=150,
            amountused=45,
            subtext="仪表部件",
            bootstyle="info",
            interactive=True,
        )
        m.pack(pady=10)

        sb = ttk.Scrollbar(
            master=lframe_inner,
            orient=HORIZONTAL,
        )
        sb.set(0.1, 0.9)
        sb.pack(fill=X, pady=5, expand=YES)

        sb = ttk.Scrollbar(
            master=lframe_inner, orient=HORIZONTAL, bootstyle="danger-round"
        )
        sb.set(0.1, 0.9)
        sb.pack(fill=X, pady=5, expand=YES)


if __name__ == "__main__":

    creator = ThemeCreator()
    creator.mainloop()
