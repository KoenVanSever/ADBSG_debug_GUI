#!/home/koenvs/anaconda3/envs/pygtk/bin/python
#/home/koenvs/anaconda3/bin/python3
#/usr/bin/python3

import classes.popupwindow as puw
import classes.safeserial as sfs
import gi
import time
import datetime as dt
import platform
import classes.asp as asp
import os
import glob

gi.require_version ('Gtk', '3.0')
from gi.repository import Gtk, Gdk

DEFAULT_PROD_ID_SUPPLIER = "06"
DEFAULT_PROD_ID_NUMBER = "0000001"
ALC_THRESHOLD = 5

# define global
serial_port = None
ret_answer = None
term_level = None
completion = None
clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

# test serial function --> not used any more
def test_serial():
    try:
        serial_port
    except NameError:
        return "Port not opened yet"
    else:
        return "Port opened correctly"

# wait depending on product line
def wait_prod():
    if hpc_stat.get_active():
        time.sleep(1.3)
    elif fo_stat.get_active():
        time.sleep(1)
    else:
        #sleep default value at least
        time.sleep(1)

#builder actions out of glade and take top level window object
builder = Gtk.Builder()
builder.add_from_file("data/debug_window_temp.ui")
window = builder.get_object("DebugWindow")
pixb = Gtk.Image().new_from_file("data/icon.png").get_pixbuf()
window.set_icon(pixb)
window.move(200,50)

#CSS styling of app
screen = Gdk.Screen.get_default()
provider = Gtk.CssProvider()
style_context = Gtk.StyleContext()
style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
provider.load_from_path("data/safeled_debug_app.css")

#manage port selection on base of system used
port_sel = builder.get_object("port_selection")
if platform.system() == "Linux":
    port_sel.set_text("/dev/ttyUSB0")
else:
    port_sel.set_text("COM1")

#get gobjects were you need to work with
# !! TODO : look into putting all this in one line
interface = builder.get_object("interface")
arg_ent = builder.get_object("arg_entry")
arg2_ent = builder.get_object("arg2_entry")
led_ent = builder.get_object("led_entry")
pid_ent = builder.get_object("pid_entry")
hpc_stat = builder.get_object("toggle_hpc")
fo_stat = builder.get_object("toggle_failopen")
int_scroll_vadj = builder.get_object("interface_scroll_vadj")
int_vadj = builder.get_object("interface_vadj")
man_ent = builder.get_object("search_entry")
# builder.add_objects_from_file("builder/debug_window_temp.ui~", ("DebugWindow"))

# set default year/week pid_ent
year = dt.date.today().isocalendar()[0]
yr = str(int(year)-2000)
wk = str(dt.date.today().isocalendar()[1])
final_string = yr + wk + DEFAULT_PROD_ID_SUPPLIER + DEFAULT_PROD_ID_NUMBER
pid_ent.set_text(final_string)

# lambda function to easily print information in the interface
print_interface = lambda a : interface.do_insert_at_cursor(interface, a)

#handler class for all actions in the window
class Handler():
    def onDestroy(self, *args):
        Gtk.main_quit()

    def cmd_openport(self, *args):
        global serial_port
        port_s = port_sel.get_text().rstrip()
        serial_port = sfs.SafeSerial(timeout = 10, port = port_s)
        temp = serial_port.get_settings()
        string = str(temp["baudrate"]) + " " + str(temp["bytesize"]) + temp["parity"] + str(temp["stopbits"])
        print_interface(f"Port opened: {serial_port.port} with {string}\n")

    def cmd_open_passwd(self, *args):
        # !! TODO : the way this is tackled is straigh up shit, special method inside safeserial is bullshit, this could be way better
        try:
            first_open = serial_port.open_admin()
            print_interface(first_open)
            global term_level
            temp = first_open.split("\n")
            term_level = temp.pop(len(temp)-1)
        except NameError:
            print_interface("Port not opened yet\n")
        except AttributeError:
            print_interface("Port not opened yet\n")
        # except serial.serialutil.SerialException:
        #     interface.do_insert_at_cursor(interface, "Reopen port first")

        # !! TODO : Completion loading for manual entry
        # load menu for search entry
        # search_ent = Gtk.ListStore(str)
        # serial_port.write_reg("help")
        # wait_prod()
        # ret = serial_port.read_print_buffer()
        # for line in ret:
        #     l = line.split("-")
        #     if len(l) >= 2:
        #         search_ent.append(l[0].rstrip().lstrip())
        # global completion
        # completion = Gtk.EntryCompletion()
        # completion.set_model(search_ent)
        # man_ent.set_completion(completion)
        # serial_port.read_print_buffer()

    def cmd_help(self, *args):
        # !! TODO : help is not fully printing debug this issue
        print(term_level)
        serial_port.write_reg("help")
        wait_prod()
        print_interface(serial_port.read_print_buffer())
        wait_prod()
        print_interface(serial_port.read_print_buffer())

    def cmd_exit(self, *args):
        serial_port.write_reg("exit")
        serial_port.close()
        print_interface("Port closed\n")

    def cmd_setPID(self, *args):
        # !! TODO : DEAL WITH THE PROMPT from setPID !! --> RESOLVED, could be more efficient though, not sure about global ret_answer, method within class, ...
        if hpc_stat.get_active():
            p_ent = pid_ent.get_buffer().get_text().rstrip()
            if len(p_ent) != 13:
                print_interface("\nFaulty PID entry, action aborted\nChuck(3)> ")
                raise Exception("Faulty PID entry")
            serial_port.write_reg(f"setPID {p_ent}")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
            verify_win = puw.VerifyWindow(parent = window)
            verify_win.set_question("Are you sure you want to change PID number?")
            def yes_ret(self):
                global ret_answer 
                ret_answer = "yes"
            def no_ret(self):
                global ret_answer
                ret_answer = "no"
            verify_win.yes_button.connect("clicked", yes_ret)
            verify_win.no_button.connect("clicked", no_ret)
            verify_win.show_all()
            verify_win.run()
            verify_win.destroy()
            serial_port.write_reg(f"{ret_answer}", True)
            serial_port.extra_return(1)
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
        else:
            print_interface("Only possible for HPC\nChuck(3):> ")
        
    def cmd_getPID(self, *args):
        if hpc_stat.get_active():
            serial_port.write_reg("getPID")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
        else:
            print_interface("Only possible for HPC\n{term_level}")

    def cmd_getccr(self, *args):
        serial_port.write_reg("getccr")
        time.sleep(0.1)
        print_interface(serial_port.read_print_buffer())

    def cmd_ledinfo(self, *args):
        l_ent = led_ent.get_buffer().get_text().rstrip()
        a_ent = arg_ent.get_buffer().get_text().rstrip()
        serial_port.write_reg(f"ledinfo {l_ent} {a_ent}")
        data = self._data_stream(0.1, 1 if int(a_ent) != 3 else 5)
        print_interface(data)

    def cmd_asp_off(self, *args):
        serial_port.write_reg("asp off")
        time.sleep(0.1)
        print_interface(serial_port.read_print_buffer())

    def cmd_asp_on(self, *args):
        serial_port.write_reg("asp on")
        time.sleep(0.1)
        print_interface(serial_port.read_print_buffer())

    def cmd_calibccrlo(self, *args):
        if hpc_stat.get_active():
            serial_port.write_reg("calibCCRlo 2000")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
        elif fo_stat.get_active():
            serial_port.write_reg("calibccrlo 2000")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
        else:
            print_interface(f"Please specify which converter type you are using\n{term_level}")

    def cmd_calibccrhi(self, *args):
        if hpc_stat.get_active():
            serial_port.write_reg("calibCCRhi 6600")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
        elif fo_stat.get_active():
            serial_port.write_reg("calibccrhi 6600")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
        else:
            print_interface(f"Please specify which converter type you are using\n{term_level}")

    def cmd_calibccr(self, *args):
        if hpc_stat.get_active():
            serial_port.write_reg("calibCCRsave yes")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
        elif fo_stat.get_active():
            serial_port.write_reg("calibccrsave yes")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
        else:
            print_interface(f"Please specify which converter type you are using\n{term_level}")

    def cmd_setTXpower(self, *args):
        if hpc_stat.get_active():
            a_ent = arg_ent.get_buffer().get_text().rstrip()
            serial_port.write_reg(f"setTXpower {a_ent}")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
        else:
            print_interface("Only possible for HPC\n{term_level}")

    def cmd_getledstatus(self, *args):
        # !! TODO : not showing, fix this --> RESOLVED
        l_ent = led_ent.get_buffer().get_text().rstrip()
        serial_port.write_reg(f"getledstatus {l_ent}")
        time.sleep(0.1)
        print_interface(serial_port.read_print_buffer())

    def cmd_ledinactivate(self, *args):
        l_ent = led_ent.get_buffer().get_text().rstrip()
        serial_port.write_reg(f"ledinactivate {l_ent}")
        time.sleep(1.5)
        print_interface(serial_port.read_print_buffer())

    def cmd_ledcalib(self, *args):
        # !! TODO : check compatibility in real-life
        l_ent = led_ent.get_buffer().get_text().rstrip()
        if int(l_ent) != 4 and int(l_ent) != 1:
            print_interface("Please adjust to LED entry to 1 or 4\nChuck(3):> ")
            return
        else:
            serial_port.write_reg(f"ledcalib {l_ent}")
            time.sleep(0.1)
            print_interface(serial_port.read_print_buffer())
            # !! TODO : incorporate_dialogwindow into new class? --> resolved working, could be better though
            value = ""
            dialog_low = puw.PopupWindow(parent = window)
            dialog_low.set_question("What's the measured current value in mA?")
            def on_activate_entry(s, win):
                nonlocal value
                value = win.get_feedback().rstrip()
                win.destroy()
            dialog_low.feedback.connect("activate", on_activate_entry, dialog_low)
            dialog_low.connect("destroy", on_activate_entry, dialog_low)
            # dialog_low.feedback.connect("activate", on_activate_entry, value_low, dialog_low)
            dialog_low.show_all()
            dialog_low.run()
            del dialog_low
            print(value)
            if value != "":
                serial_port.write_reg(f"{value}", True)
                serial_port.extra_return(1)
                time.sleep(0.1)
            else:
                print_interface("\nSomething went wrong, please try again")
                raise Exception("broken out of ledcalib during low value reading")
            print_interface(serial_port.read_print_buffer())
            value = ""
            dialog_high = puw.PopupWindow(parent = window)
            dialog_high.set_question("What's the measured current value in mA?")
            dialog_high.show_all()
            dialog_high.feedback.connect("activate", on_activate_entry, dialog_high)
            dialog_high.connect("destroy", on_activate_entry, dialog_high)
            dialog_high.run()
            del dialog_high
            if value != "":
                serial_port.write_reg(f"{value}", True)
                serial_port.extra_return(1)
                time.sleep(0.1)
            else:
                print_interface("\nSomething went wrong, please try again")
                raise Exception("broken out of ledcalib during low value reading")
            print_interface(serial_port.read_print_buffer())
            
    def cmd_clear(self, *args):
        int_buf = interface.get_buffer()
        int_buf.delete(int_buf.get_start_iter(), int_buf.get_end_iter())
        print_interface(f"{term_level}")

    def hpc_toggle(self, *args):
        # !! TODO : NEED TO DOUBLECLICK at the moment, otherwise infinite loop
        # !! TODO : interacts strangely with the CSS as well
        fo_stat.set_active(False)
        
    def fo_toggle(self, *args):
        # !! TODO : NEED TO DOUBLECLICK at the moment, otherwise infinite loop
        # !! TODO : interacts strangely with the CSS as well
        hpc_stat.set_active(False)

    def read_buffer(self, *args):
        print_interface(serial_port.read_print_buffer())
        print_interface(f"\n{term_level}")

    def cmd_setledovr(self, *args):
        l_ent = led_ent.get_buffer().get_text().rstrip()
        a_ent = arg_ent.get_buffer().get_text().rstrip()
        serial_port.write_reg(f"setledovr {l_ent} {a_ent}")
        time.sleep(0.1)
        print_interface(serial_port.read_print_buffer())

    def cmd_setledovr2(self, *args):
        l_ent = led_ent.get_buffer().get_text().rstrip()
        a_ent = arg_ent.get_buffer().get_text().rstrip()
        serial_port.write_reg(f"setledovr2 {l_ent} {a_ent}")
        time.sleep(0.1)
        print_interface(serial_port.read_print_buffer())

    def cmd_recvtest(self, *args):
        # print_interface(f"Not implemented yet\n{term_level}")
        # this code shuts down the window upon running?
        # !! TODO : investigate this!
        serial_port.write_reg("recvtest")
        data = self._data_stream(0.2, 5)
        print_interface(data)

    def cmd_params_dump(self, *args):
        serial_port.write_reg("params dump")
        time.sleep(0.2)
        print_interface(serial_port.read_print_buffer())
        # print_interface(f"Not implemented yet\n{term_level}")

    def cmd_rx(self, *args):
        #delete files from possible previous runs
        files = glob.glob(f"{os.getcwd()}/plots/*.png")
        for x in files:
            os.remove(x)
        #reset plot numbers from possible previous runs
        puw.plot_50_nr = 0
        puw.plot_hf_nr = 0

        #send the correct command
        a2_ent = arg2_ent.get_text().rstrip()
        a2_ent_list = a2_ent.split(" ")
        if len(a2_ent_list) != 2:
            print_interface(f"Wrong number of arguments\n{term_level}")
            raise Exception("Wrong number of arguments")
        serial_port.write_reg(f"rx {a2_ent}")

        #determining read time (command arguments have serious influence on reading length)
        extra = None
        if int(a2_ent_list[1]) == 0 or int(a2_ent_list[1]) == 1:
            extra = 0
        elif int(a2_ent_list[1]) == 2:
            extra = 7
        else:
            extra = 14
        reps = int(round(int(a2_ent_list[0])/20 + extra, 0))
        data = self._data_stream(0.2, reps if reps != 0 else 1)
        # print_interface(data)

        #create rx data class and window to plot calculated data
        rx = asp.Rx(data, {a2_ent_list[0]}, {a2_ent_list[1]}, threshold_level = ALC_THRESHOLD)
        global clipboard
        rx_win = puw.RxWindow(clipboard, parent = window, title = f"rx {a2_ent} ouput", modal = True)
        rx_win.set_general_text(str(rx))
        pl_50 = rx.plot_adc_data_50_all()
        pl_hf = rx.plot_adc_data_hf_all()
        for e in pl_50:
            rx_win.add_plot_50(f"{e}.png")
        for e in pl_hf:
            rx_win.add_plot_hf(f"{e}.png")
        rx_win.show_all()
        rx_win.cancel_button.connect("clicked", lambda a, b: b.destroy(), rx_win)
        rx_win.run()

        # print_interface(f"Not implemented yet\n{term_level}")

    def cmd_read_log(self, *args):
        a2_ent = arg2_ent.get_text().rstrip()
        serial_port.write_reg(f"read_log {a2_ent}")
        time.sleep(1)
        print_interface(serial_port.read_print_buffer())

    def cmd_readvolt(self, *args):
        serial_port.write_reg("readvolt")
        time.sleep(0.1)
        print_interface(serial_port.read_print_buffer())

    def act_manEnt(self, *args):
        # !! TODO: Works but completion not implemented yet!
        command = man_ent.get_text().rstrip()
        serial_port.write_reg(command)
        time.sleep(0.1)
        print_interface(serial_port.read_print_buffer())

    def edge_over(self, *args):
        #print("test edge")
        pass

    def edge_reached(self, *args):
        #print("test reached")
        pass

    def _data_stream(self, sleep_time, repetitions):
        ret = ""
        for i in range(repetitions):
            time.sleep(sleep_time)
            ret += serial_port.read_print_buffer()
            print(f"repititions for buffer reading: {i+1}")
        return ret

#Connect handler methods with glade builder .ui file!            
builder.connect_signals(Handler())

def main():
    #window.connect("destroy", Gtk.main_quit)
    #window quit include in the handler class (method onDestroy)
    window.show_all()
    Gtk.main()
    files = glob.glob(f"{os.getcwd()}/plots/*.png")
    for x in files:
        os.remove(x)

if __name__ == "__main__": main()
