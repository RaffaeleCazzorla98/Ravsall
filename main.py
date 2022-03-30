import os
import time
import json
import threading
import tkinter
from tkinter import messagebox
import pynput
import ctypes

PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

command_list = []
command_read = []
isRunning = True
startTime = 0
mouse_x_old = 0
mouse_y_old = 0
mouse_t_old = 0


def on_key_press(key):
    if key == pynput.keyboard.Key.esc:
        global isRunning
        isRunning = False
        mouse = pynput.mouse.Controller()
        mouse.click(pynput.mouse.Button.left)
        return False
    command_list.append((
        "press",
        (str(key).strip("'"),),
        time.time()-startTime
    ))


def on_key_release(key):
    command_list.append((
        "release",
        (str(key).strip("'"),),
        time.time()-startTime
    ))


def on_mouse_click(x,y,button,pressed):
    global mouse_x_old
    global mouse_y_old
    global mouse_t_old
    if not isRunning:
        return False
    if not pressed:
        return True
    if mouse_x_old == x and mouse_y_old == y:
        if time.time() - mouse_t_old > 0.3:
            command_list.append((
                "click",
                (x, y, str(button)),
                time.time() - startTime
            ))
        else:
            command_list.pop(0)
            command_list.append((
                "double-click",
                (x, y, str(button)),
                time.time() - startTime
            ))
    else:
        command_list.append((
            "click",
            (x, y, str(button)),
            time.time() - startTime
        ))
    mouse_x_old = x
    mouse_y_old = y
    mouse_t_old = time.time()


def start_key_listen():

    with pynput.keyboard.Listener(on_press=on_key_press,on_release=on_key_release) as listener:
        listener.join()


def start_mouse_listen():

    with pynput.mouse.Listener(on_click=on_mouse_click) as listener:
        listener.join()


def toFile(Command_list,path):
    with open(path,"w") as f:
        f.write(json.dumps(Command_list))


def unicode_convert(input_data):

    if isinstance(input_data, dict):
        return {unicode_convert(key): unicode_convert(value) for key, value in input_data.iteritems()}
    elif isinstance(input_data, list):
        return [unicode_convert(element) for element in input_data]
    elif isinstance(input_data, str):
        return input_data
    else:
        return input_data


def ExecuteCommandsFile(path):

    path = unicode_convert(path)
    if path[2] != ":":

        path = os.path.join(os.path.dirname(__file__), path)


    with open(path) as f:

         Command_read = json.loads(f.read())
    Commands_read = unicode_convert(command_read)

    mouse = pynput.mouse.Controller()
    keyboard = pynput.keyboard.Controller()

    buttons = {
        "Button.left": pynput.mouse.Button.left,
        "Button.right": pynput.mouse.Button.right
    }

    sTime = 0

    for command in command_read:

        print(command[0])
        print(command[1])
        print(command[2])

        if command[0] == "click":

            mouse.position = (command[1][0], command[1][1])

            time.sleep(0.1)

            mouse.click(buttons[command[1][2]])

        elif command[0] == "double-click":

            mouse.position = (command[1][0], command[1][1])

            time.sleep(0.1)

            mouse.click(buttons[command[1][2]], 2)

        elif command[0] == "press":

            if command[1][0][:3] == "Key":

                keyboard.press(eval(command[1][0], {}, {
                    "Key": pynput.keyboard.Key
                }))
            else:

                if "<255>" == command[1][0]:
                    continue
                print(command[1][0])


                keyboard.press(command[1][0])

        elif command[0] == "release":

            if command[1][0][:3] == "Key":

                keyboard.release(eval(command[1][0], {}, {
                    "Key": pynput.keyboard.Key
                }))
            else:

                if "<255>" == command[1][0]:
                    continue
                print(command[1][0])


                keyboard.release(command[1][0])

        time.sleep(command[2] - sTime)

        sTime = command[2]


class TKDemo:
    def __init__(self):
        self.top = tkinter.Tk()
        self.top.title('Ravsall')
        self.top.geometry('500x250')

        frame1 = tkinter.Frame(self.top)
        frame1.pack(side='top')
        l1 = tkinter.Label(frame1,
                           text='1----Operazione di registrazione】\ Premi Esc per uscire，le combinazioni di tastiera non sono supportate')

        l1.pack()
        b1 = tkinter.Button(frame1,
                            text='Record',
                            width=15, height=2,
                            command=self.recordOp)
        b1.pack()
        frame2 = tkinter.Frame(self.top)
        frame2.pack(side='bottom')
        l2 = tkinter.Label(frame2,
                           text='【2----Esegui Operazione】')
        l2.pack()
        b2 = tkinter.Button(frame2,
                            text='Esegui',
                            width=15, height=2,
                            command=self.execOp)
        b2.pack()
        l3 = tkinter.Label(frame2,
                           text='Inserisci numero di esecuzioni')
        l3.pack()
        self.count = tkinter.StringVar()
        e1 = tkinter.Entry(frame2, textvariable=self.count)
        e1.pack()

        self.top.mainloop()

    def recordOp(self):
        self.top.iconify()
        global startTime
        startTime = time.time()
        key_listen_thread = threading.Thread(target=start_key_listen)
        mouse_listen_thread = threading.Thread(target=start_mouse_listen)

        key_listen_thread.start()
        mouse_listen_thread.start()

        key_listen_thread.join()
        mouse_listen_thread.join()

        toFile(command_list, "./commands.json")

        global isRunning
        isRunning = True
        command_list.clear()
        self.top.deiconify()
        print("Registrazione riuscita！")
        tkinter.messagebox.showinfo('Suggerimento', 'Registrato con successo！')

    def execOp(self):
        self.top.iconify()
        path = 'commands.json'
        count = self.count.get()
        if count.isdigit():
            for i in range(int(count)):
                ExecuteCommandsFile(path)
            print("Registrazione riuscita!" % (int(count)))
            tkinter.messagebox.showinfo('Prompt', "Eseguito"  (int(count)))
        elif len(count) == 0:
            ExecuteCommandsFile(path)
            print("Esecuzione riuscita!")
            tkinter.messagebox.showinfo('Richiesta', 'Eseguito！\n1volta！')
        else:
            print("Impossibile eseguire！inserisci un numero")
            tkinter.messagebox.showerror('prompt', 'Impossibile eseguire！\nDigita un numero！')
        self.top.deiconify()


def main():
    TKDemo()


if __name__ == "__main__":
    main()
