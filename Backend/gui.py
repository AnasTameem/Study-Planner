import tkinter as tk
from tkinter import simpledialog, messagebox
from tracker import StudyTracker
from models.learning import Learning
from models.subjects import Subject
from models.topic import Topic
from models.sub_topic import SubTopic
from exceptions import DuplicateError
import theme

SAVE_FILE = "study_data.json"
c = theme.LIGHT   # fixed palette, light mode only


def status_color(status):
    s = status.lower()
    if "progress" in s:
        return c["amber"]
    if "complet" in s:
        return c["success"]
    return c["muted"]


class StudyTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(theme.APP_NAME)
        self.root.geometry("900x600")
        self.root.minsize(700, 500)
        self.root.maxsize(900, 600)
        self.root.configure(bg=c["bg"])

        self.tracker = self.load_tracker()
        self.path = []   # [] = root, [learning], [learning, subject], [learning, subject, topic]

        self.show_landing()

    # ---------------- persistence ----------------

    def load_tracker(self):
        try:
            return StudyTracker.load_from_file(SAVE_FILE)
        except FileNotFoundError:
            return StudyTracker()

    def save_and_quit(self):
        self.tracker.save_to_file(SAVE_FILE)
        self.root.destroy()

    # ---------------- screen scaffolding ----------------

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def topbar(self, show_back=True):
        bar = tk.Frame(self.root, bg=c["surface"], height=40)
        bar.pack(fill="x", side="top")
        if show_back and self.path:
            tk.Button(bar, text="←", command=self.go_back, bg=c["surface"],
                      fg=c["text"], relief="flat", font=theme.FONT_HEADER,
                      bd=0, padx=10).pack(side="left", pady=4)
        tk.Label(bar, text=theme.APP_NAME, bg=c["surface"], fg=c["muted"],
                  font=theme.FONT_CAPTION).pack(pady=10)
        tk.Frame(self.root, bg=c["border"], height=1).pack(fill="x")

    def go_back(self):
        self.path.pop()
        self.render()

    def render(self):
        """Redraw whatever screen matches the current self.path depth."""
        self.clear()
        self.topbar()
        depth = len(self.path)
        if depth == 0:
            self.render_list_screen(
                title="My Learning", subtitle_fn=lambda: f"{len(self.tracker)} learnings in progress",
                items=list(self.tracker), breadcrumb=None, sidebar_items=None,
                add_label="+ New learning", add_fn=self.add_learning,
                open_fn=lambda item: self.open_item(item), delete_fn=self.delete_learning,
            )
        elif depth == 1:
            learning = self.path[0]
            self.render_list_screen(
                title=learning.name, subtitle_fn=lambda: f"{len(learning)} subjects",
                items=list(learning), breadcrumb="My Learning",
                sidebar_items=list(self.tracker), sidebar_active=learning,
                add_label="+ New subject", add_fn=self.add_subject,
                open_fn=lambda item: self.open_item(item), delete_fn=self.delete_subject,
            )
        elif depth == 2:
            learning, subject = self.path
            self.render_list_screen(
                title=subject.name, subtitle_fn=lambda: f"{len(subject)} topics",
                items=list(subject), breadcrumb=f"My Learning / {learning.name}",
                sidebar_items=list(learning), sidebar_active=subject,
                add_label="+ New topic", add_fn=self.add_topic,
                open_fn=lambda item: self.open_item(item), delete_fn=self.delete_topic,
            )
        elif depth == 3:
            learning, subject, topic = self.path
            done = sum(1 for st in topic if st.done)
            self.render_grid_screen(
                title=topic.name, subtitle=f"{done} of {len(topic)} sub-topics done",
                items=list(topic), breadcrumb=f"My Learning / {learning.name} / {subject.name}",
                sidebar_items=list(subject), sidebar_active=topic,
                add_fn=self.add_subtopic, delete_fn=self.delete_subtopic,
            )

    def open_item(self, item):
        """Drill into a clicked row (Learning -> Subject -> Topic). SubTopics never open."""
        self.path.append(item)
        self.render()

    def jump_sidebar(self, item):
        """Sidebar click: replace the last path element with a sibling."""
        if not self.path:
            return
        self.path[-1] = item
        self.render()

    # ---------------- generic list screen (My Learning / Learning / Subject) ----------------

    def render_list_screen(self, title, subtitle_fn, items, breadcrumb, add_label, add_fn,
                            open_fn, delete_fn, sidebar_items=None, sidebar_active=None):
        body = tk.Frame(self.root, bg=c["bg"])
        body.pack(fill="both", expand=True)

        if sidebar_items is not None:
            self.build_sidebar(body, sidebar_items, sidebar_active)
            content = tk.Frame(body, bg=c["bg"])
            content.pack(side="left", fill="both", expand=True)
        else:
            content = body

        header = tk.Frame(content, bg=c["bg"])
        header.pack(fill="x", padx=theme.SPACING_LG, pady=(theme.SPACING_LG, theme.SPACING_SM))

        if breadcrumb:
            tk.Label(header, text=breadcrumb, bg=c["bg"], fg=c["muted"],
                      font=theme.FONT_CAPTION).pack(anchor="w")
        title_row = tk.Frame(header, bg=c["bg"])
        title_row.pack(fill="x")
        tk.Label(title_row, text=title, bg=c["bg"], fg=c["text"],
                  font=theme.FONT_TITLE).pack(side="left")
        tk.Button(title_row, text=add_label, command=add_fn, bg=c["accent"], fg="white",
                   relief="flat", font=theme.FONT_LABEL, padx=14, pady=4).pack(side="right")
        tk.Label(header, text=subtitle_fn(), bg=c["bg"], fg=c["muted"],
                  font=theme.FONT_BODY).pack(anchor="w")

        list_frame = tk.Frame(content, bg=c["bg"])
        list_frame.pack(fill="both", expand=True, padx=theme.SPACING_LG)

        for item in items:
            self.build_row(list_frame, item, open_fn, delete_fn)

    def build_row(self, parent, item, open_fn, delete_fn):
        row = tk.Frame(parent, bg=c["surface"], highlightbackground=c["border"],
                         highlightthickness=1, bd=0)
        row.pack(fill="x", pady=6)

        text_col = tk.Frame(row, bg=c["surface"])
        text_col.pack(side="left", padx=16, pady=10, fill="x", expand=True)
        name_lbl = tk.Label(text_col, text=item.name, bg=c["surface"], fg=c["text"],
                             font=theme.FONT_HEADER, anchor="w", cursor="hand2")
        name_lbl.pack(anchor="w")
        tk.Label(text_col, text=item.status, bg=c["surface"], fg=status_color(item.status),
                  font=theme.FONT_CAPTION, anchor="w").pack(anchor="w")

        bar_bg = tk.Frame(row, bg=c["border"], width=110, height=6)
        bar_bg.pack(side="left", padx=6)
        bar_bg.pack_propagate(False)
        fill_w = max(2, int(110 * item.progress / 100))
        bar_fill_color = c["success"] if item.progress == 100 else (c["amber"] if item.progress > 0 else c["border"])
        tk.Frame(bar_bg, bg=bar_fill_color, width=fill_w, height=6).place(x=0, y=0)

        tk.Label(row, text=f"{item.progress:.0f}%", bg=c["surface"], fg=c["muted"],
                  font=theme.FONT_CAPTION, width=5).pack(side="left")

        tk.Button(row, text="🗑", command=lambda: self.confirm_delete(item, delete_fn),
                   bg=c["surface"], fg=c["danger"], relief="flat", bd=0,
                   font=theme.FONT_BODY).pack(side="right", padx=16)

        name_lbl.bind("<Button-1>", lambda e: open_fn(item))
        row.bind("<Button-1>", lambda e: open_fn(item))

    def build_sidebar(self, parent, sibling_items, active_item):
        sb = tk.Frame(parent, bg=c["sidebar"], width=200)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text=theme.APP_NAME, bg=c["sidebar"], fg=c["text"],
                  font=theme.FONT_HEADER).pack(anchor="w", padx=16, pady=(20, 12))

        self.sidebar_button(sb, "My Learning", active=(len(self.path) == 0),
                              command=lambda: self.go_home())

        for item in sibling_items:
            self.sidebar_button(sb, item.name, active=(item is active_item),
                                  command=lambda i=item: self.jump_sidebar(i))

    def sidebar_button(self, parent, label, active, command):
        bg = c["accent"] if active else c["sidebar"]
        fg = "white" if active else c["text"]
        tk.Button(parent, text=label, command=command, bg=bg, fg=fg, relief="flat",
                   font=theme.FONT_LABEL, anchor="w", padx=16, pady=8).pack(fill="x", padx=8, pady=2)

    def go_home(self):
        self.path = []
        self.render()

    # ---------------- grid screen (Topic -> SubTopics checklist) ----------------

    def render_grid_screen(self, title, subtitle, items, breadcrumb, add_fn, delete_fn,
                            sidebar_items, sidebar_active):
        body = tk.Frame(self.root, bg=c["bg"])
        body.pack(fill="both", expand=True)

        self.build_sidebar(body, sidebar_items, sidebar_active)
        content = tk.Frame(body, bg=c["bg"])
        content.pack(side="left", fill="both", expand=True)

        header = tk.Frame(content, bg=c["bg"])
        header.pack(fill="x", padx=theme.SPACING_LG, pady=(theme.SPACING_LG, theme.SPACING_SM))
        tk.Label(header, text=breadcrumb, bg=c["bg"], fg=c["muted"],
                  font=theme.FONT_CAPTION).pack(anchor="w")
        title_row = tk.Frame(header, bg=c["bg"])
        title_row.pack(fill="x")
        tk.Label(title_row, text=title, bg=c["bg"], fg=c["text"],
                  font=theme.FONT_TITLE).pack(side="left")
        tk.Button(title_row, text="+ New sub-topic", command=add_fn, bg=c["accent"], fg="white",
                   relief="flat", font=theme.FONT_LABEL, padx=14, pady=4).pack(side="right")
        tk.Label(header, text=subtitle, bg=c["bg"], fg=c["muted"],
                  font=theme.FONT_BODY).pack(anchor="w")

        grid = tk.Frame(content, bg=c["bg"])
        grid.pack(fill="both", expand=True, padx=theme.SPACING_LG)
        for i, st in enumerate(items):
            row, col = divmod(i, 2)
            self.build_subtopic_card(grid, st, delete_fn, row, col)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

    def build_subtopic_card(self, parent, st, delete_fn, row, col):
        card = tk.Frame(parent, bg=c["surface"], highlightbackground=c["border"], highlightthickness=1)
        card.grid(row=row, column=col, sticky="ew", padx=6, pady=6)

        check_var = tk.BooleanVar(value=st.done)
        def on_toggle():
            if check_var.get():
                st.mark_done()
            else:
                st.mark_undone()
            self.render()

        tk.Checkbutton(card, variable=check_var, command=on_toggle, bg=c["surface"],
                        activebackground=c["surface"]).pack(side="left", padx=10)

        text_col = tk.Frame(card, bg=c["surface"])
        text_col.pack(side="left", fill="x", expand=True, pady=10)
        tk.Label(text_col, text=st.name, bg=c["surface"], fg=c["text"],
                  font=theme.FONT_HEADER, anchor="w").pack(anchor="w")
        tk.Label(text_col, text=st.status, bg=c["surface"], fg=status_color(st.status),
                  font=theme.FONT_CAPTION, anchor="w").pack(anchor="w")

        tk.Button(card, text="🗑", command=lambda: self.confirm_delete(st, delete_fn),
                   bg=c["surface"], fg=c["danger"], relief="flat", bd=0,
                   font=theme.FONT_BODY).pack(side="right", padx=10)

    # ---------------- add actions ----------------

    def add_learning(self):
        name = self.ask_string("New Learning", "Learning name:")
        if not name:
            return
        try:
            self.tracker.add_learning(Learning(name, ""))
            self.render()
        except DuplicateError as e:
            messagebox.showerror("Error", str(e))

    def add_subject(self):
        name = self.ask_string("New Subject", "Subject name:")
        if not name:
            return
        try:
            self.path[0].add_subject(Subject(name, ""))
            self.render()
        except DuplicateError as e:
            messagebox.showerror("Error", str(e))

    def add_topic(self):
        name = self.ask_string("New Topic", "Topic name:")
        if not name:
            return
        try:
            self.path[1].add_topic(Topic(name, ""))
            self.render()
        except DuplicateError as e:
            messagebox.showerror("Error", str(e))

    def add_subtopic(self):
        name = self.ask_string("New Sub-topic", "Sub-topic name:")
        if not name:
            return
        try:
            self.path[2].add_subtopic(SubTopic(name, ""))
            self.render()
        except DuplicateError as e:
            messagebox.showerror("Error", str(e))

    # ---------------- delete actions + confirmation popup ----------------

    def confirm_delete(self, item, delete_fn):
        popup = tk.Toplevel(self.root)
        popup.title("")
        popup.configure(bg=c["surface"])
        popup.transient(self.root)
        popup.resizable(False, False)

        popup_w, popup_h = 320, 140

        # calculate center relative to the MAIN window, not the screen
        self.root.update_idletasks()   # ensures root's current size/position are accurate
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()

        x = root_x + (root_w // 2) - (popup_w // 2)
        y = root_y + (root_h // 2) - (popup_h // 2)
        popup.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        popup.grab_set()   # modal — blocks the main window until this closes

        tk.Label(popup, text="Are you sure you want to delete this item?",
                  bg=c["surface"], fg=c["text"], font=theme.FONT_BODY,
                  wraplength=280, justify="center").pack(pady=(24, 16), padx=16)

        btn_row = tk.Frame(popup, bg=c["surface"])
        btn_row.pack()

        tk.Button(btn_row, text="Cancel", command=popup.destroy, bg=c["surface"],
                   fg=c["text"], relief="solid", bd=1, padx=16, pady=6).pack(side="left", padx=8)

        def do_delete():
            delete_fn(item)
            popup.destroy()
            self.render()

        tk.Button(btn_row, text="Yes, delete", command=do_delete, bg=c["accent"],
                   fg="white", relief="flat", padx=16, pady=6).pack(side="left", padx=8)
    def delete_learning(self, item):
        self.tracker.remove_learning(item.name)

    def delete_subject(self, item):
        self.path[0].remove_subject(item.name)

    def delete_topic(self, item):
        self.path[1].remove_topic(item.name)

    def delete_subtopic(self, item):
        self.path[2].remove_subtopic(item.name)

    # ---------------- landing screen ----------------

    def show_landing(self):
        self.clear()
        tk.Frame(self.root, bg=c["surface"], height=1).pack(fill="x")

        frame = tk.Frame(self.root, bg=c["bg"])
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=theme.APP_NAME, bg=c["bg"], fg=c["text"],
                  font=("Segoe UI", 24, "bold")).pack(pady=(160, 4))
        tk.Label(frame, text="Formulated by New AI Horizons", bg=c["bg"], fg=c["muted"],
                  font=theme.FONT_CAPTION).pack()

        tk.Button(frame, text="Get started", command=self.render, bg=c["accent"], fg="white",
                   relief="flat", font=theme.FONT_LABEL, padx=24, pady=8).pack(pady=24)

        tk.Label(frame, text="Loads your saved progress automatically", bg=c["bg"],
                  fg=c["muted"], font=theme.FONT_CAPTION).pack()

    def ask_string(self, title, prompt):
        """Custom replacement for simpledialog.askstring — centered, no min/max buttons."""
        result = {"value": None}

        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg=c["surface"])
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.attributes("-toolwindow", True)   # Windows-only: strips min/max buttons, keeps just close

        popup_w, popup_h = 320, 160
        self.root.update_idletasks()
        root_x, root_y = self.root.winfo_x(), self.root.winfo_y()
        root_w, root_h = self.root.winfo_width(), self.root.winfo_height()
        x = root_x + (root_w // 2) - (popup_w // 2)
        y = root_y + (root_h // 2) - (popup_h // 2)
        popup.geometry(f"{popup_w}x{popup_h}+{x}+{y}")
        popup.grab_set()

        tk.Label(popup, text=prompt, bg=c["surface"], fg=c["text"],
                  font=theme.FONT_BODY).pack(pady=(20, 8), padx=16)

        entry = tk.Entry(popup, font=theme.FONT_BODY, relief="solid", bd=1)
        entry.pack(padx=16, fill="x")
        entry.focus_set()

        btn_row = tk.Frame(popup, bg=c["surface"])
        btn_row.pack(pady=16)

        def on_cancel():
            popup.destroy()

        def on_ok():
            result["value"] = entry.get().strip()
            popup.destroy()

        tk.Button(btn_row, text="Cancel", command=on_cancel, bg=c["surface"],
                   fg=c["text"], relief="solid", bd=1, padx=16, pady=6).pack(side="left", padx=8)
        tk.Button(btn_row, text="OK", command=on_ok, bg=c["accent"],
                   fg="white", relief="flat", padx=16, pady=6).pack(side="left", padx=8)

        entry.bind("<Return>", lambda e: on_ok())
        popup.wait_window()   # pauses here until popup.destroy() is called (Cancel or OK)
        return result["value"]

        
if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.save_and_quit)   # save on the window's X button too, not just a dedicated Quit button
    root.mainloop()