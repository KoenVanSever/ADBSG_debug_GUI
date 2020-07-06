#!/home/koenvs/anaconda3/bin/python3
#/usr/bin/python3

import gi
import time
#import pango

gi.require_version ('Gtk', '3.0')
from gi.repository import Gtk

plot_50_nr = 0
plot_hf_nr = 0
plot_filter_50_nr = 0

class PopupWindow(Gtk.MessageDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, message_type = Gtk.MessageType.QUESTION, buttons = Gtk.ButtonsType.NONE)
        box = self.get_message_area()
        self.question = Gtk.Label(label = kwargs["label"] if "label" in kwargs.keys() else "Questions undefined")
        self.feedback = Gtk.Entry()
        box.pack_start(self.question, True, True, 10)
        box.pack_start(self.feedback, True, True, 10)
        # builder_dialog = Gtk.Builder()
        # builder_dialog.add_from_file("builder/dialog_window.ui")
        # self.window = builder_dialog.get_object("dialog_prompt")
        # self.feedback.connect("activate", self.on_activate_entry, val)

    # def on_activate_entry(self, test, val):
    #     val = self.get_feedback()
    #     self.destroy()
    #     return value

    def get_feedback(self):
        return self.feedback.get_text().rstrip()

    def set_question(self, arg):
        self.question.set_label(arg)
        return self.question

    def onDestroy(self):
        pass

class VerifyWindow(Gtk.MessageDialog):
    def yes_print(self, arg):
        return("yes")
    
    def no_print(self, arg):
        return("no")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, message_type = Gtk.MessageType.QUESTION, buttons = Gtk.ButtonsType.YES_NO)
        box = self.get_message_area()
        self.question = Gtk.Label()
        box.pack_start(self.question, True, True, 10)
        # how can I find back the objects for yes_button and no_button in a better way?
        self.no_button = self.get_children()[0].get_children()[1].get_children()[0].get_children()[0]
        self.yes_button = self.get_children()[0].get_children()[1].get_children()[0].get_children()[1]
        # self.yes_button.connect("clicked", self.yes_print)
        # self.no_button.connect("clicked", self.no_print)

    def on_activate_yes(self, arg):
        pass

    def set_question(self, arg):
        self.question.set_label(arg)
        return self.question

class RxWindow(Gtk.Dialog):
    def __init__(self, clipboard, *args, **kwargs):
        # initial tasks:
        super().__init__(*args, **kwargs)
        self.clipboard = clipboard
        self.set_default_geometry(640, 480)

        # get two main GObjects
        cont = self.get_content_area()
        act = self.get_action_area()

        # create default layout
        self.notebook = Gtk.Notebook()
        button_box = Gtk.ButtonBox()
        cont.add(Gtk.Label(label = "UNDER CONSTRUCTION", use_underline = True))
        cont.add(self.notebook)
        act.add(button_box)
        self.cancel_button = Gtk.Button(label = "Cancel")
        #self.cancel_button.connect("clicked", self.get_root_window().destroy)
        button_box.pack_end(self.cancel_button, True, True, 5)
        self.general_buffer = Gtk.TextBuffer(text = "No information given yet")
        general_text = Gtk.TextView(justification = 3, valign = Gtk.Align.FILL, buffer = self.general_buffer)
        self.general_button = Gtk.Button(label = "Copy to clipboard")
        text = self.get_general_text()
        self.general_button.connect("clicked", self._set_clipboard, self.clipboard, text)
        vbox_general = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, vexpand = True)
        vbox_general.pack_start(general_text, True, True, 5)
        vbox_general.pack_end(self.general_button, False, False, 5)
        self.notebook.append_page(vbox_general, self.NotebookLabel(label = "General"))        

    def get_general_text(self):
        start = self.general_buffer.get_start_iter()
        end = self.general_buffer.get_end_iter()
        return self.general_buffer.get_text(start, end, False).rstrip()

    def set_general_text(self, text):
        self.general_buffer.set_text(text)
        return text

    def add_plot_50(self, image_path):
        global plot_50_nr
        image_plot_50 = Gtk.Image.new_from_file(image_path)
        plot_50_button = Gtk.Button(label = "Copy to clipboard")
        plot_50_button.connect("clicked", self._set_clipboard, self.clipboard, image_plot_50.get_pixbuf())
        vbox_plot_50 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, vexpand = True)
        vbox_plot_50.pack_start(image_plot_50, True, True, 5)
        vbox_plot_50.pack_end(plot_50_button, False, False, 5)        
        self.notebook.append_page(vbox_plot_50, self.NotebookLabel(label = f"Plot 50Hz {plot_50_nr}"))
        plot_50_nr += 1

    def add_plot_filter_50(self, image_path):
        global plot_filter_50_nr
        image_plot_filter_50 = Gtk.Image.new_from_file(image_path)
        plot_filter_50_button = Gtk.Button(label = "Copy to clipboard")
        plot_filter_50_button.connect("clicked", self._set_clipboard, self.clipboard, image_plot_filter_50.get_pixbuf())
        vbox_plot_filter_50 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, vexpand = True)
        vbox_plot_filter_50.pack_start(image_plot_filter_50, True, True, 5)
        vbox_plot_filter_50.pack_end(plot_filter_50_button, False, False, 5)        
        self.notebook.append_page(vbox_plot_filter_50, self.NotebookLabel(label = f"Plot 50Hz Filter {plot_filter_50_nr}"))
        plot_filter_50_nr += 1

    def add_plot_hf(self, image_path):
        global plot_hf_nr
        image_plot_hf = Gtk.Image.new_from_file(image_path)
        plot_hf_button = Gtk.Button(label = "Copy to clipboard")
        plot_hf_button.connect("clicked", self._set_clipboard, self.clipboard, image_plot_hf.get_pixbuf())
        vbox_plot_hf = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, vexpand = True)
        vbox_plot_hf.pack_start(image_plot_hf, True, True, 5)
        vbox_plot_hf.pack_end(plot_hf_button, False, False, 5)        
        self.notebook.append_page(vbox_plot_hf, self.NotebookLabel(label = f"Plot hf {plot_hf_nr}"))
        plot_hf_nr += 1

    def _set_clipboard(self, arg, clipboard, item):
        if type(item) == str:
            clipboard.set_text(item, -1)
            print("copied text to clipboard")
        elif type(item) == gi.overrides.GdkPixbuf.Pixbuf:
            clipboard.set_image(item)
            print("copied image to clipboard")

    # INNER CLASS

    class NotebookLabel(Gtk.Label):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

    NotebookLabel.set_css_name("notebook_label")
        

# class RxWindow(Gtk.Dialog):
#     def __init__(self, *args, **kwargs):
#         b = Gtk.Builder()
#         b.add_from_file("safeled_debug_app/rx_window.ui")
#         self.window = b.get_object("rx_dialog")
#         self.window.show_all()

def main():
    # dialog_test = PopupWindow(parent = None)
    # verify_test = VerifyWindow(parent = None)
    # verify_test.set_question("Test?")
    # dialog_test.connect("destroy", Gtk.main_quit)
    # dialog_test.show_all()
    # dialog_test.run()
    # value = dialog_test.get_feedback()
    # dialog_test.destroy()
    # verify_test.show_all()
    # l = verify_test.get_children()[0].get_children()
    # print(l[0].get_children())
    # print(l[1].get_children()[0].get_children()[0])
    # verify_test.run()
    # print(value)
    # print(dialog_test.get_children())
    # verify_test.destroy()
    test = Gtk.Window()
    rx = RxWindow(None, parent = test, title = "Rx Readout")
    rx.set_general_text("Overwritten by command")
    print(rx.get_general_text())
    rx.add_plot_50("test/plots/plot_50_l0_507760.png")
    rx.add_plot_hf("test/plots/plot_hf_l0_507760.png")
    rx.show_all()
    rx.run()
    #Gtk.main_quit()
    #Gtk.main

if __name__ == "__main__": main()