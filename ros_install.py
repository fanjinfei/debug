#! /usr/bin/env python3

import locale
from dialog import Dialog
import sys
from time import sleep

class GrubMenu():
    def __init__(self):
        self.headers = ''
        self.items=[]
        self.names = []
    def show(self):
        print(self.headers.rstrip())
        for i in self.items:
            print(i.rstrip())
        
def newBoot(d): #display new boot option
    pass

def detailBoot(d, item):
    pass

def bootmenu(d, tags): #display current boot menu, and new option
    # We could put non-empty items here (not only the tag for each entry)
    code, tag = d.menu("select your command:",
                       choices=[("1)", "print details"),
                                ("2)", "detect and install new boot option"),
                                ("3)", "delete boot option"),
                                ("4)", "exit"),
                                ]
                      )
    if code == d.OK:
        # 'tags' now contains a list of the toppings chosen by the user
        print(tag)
        return tag

def parseGrub(filename):
    gm = GrubMenu()
    with open(filename, "r") as f:
        item = ''
        while True:
            line = f.readline()
            if not line: break
            if not gm.items:
                gm.headers += line
            else:
                if line[:9] == 'menuentry':
                    item = line
                elif line.strip()[0]=='}':
                    gm.items.append(item)
                else :
                    item += line
    gm.show()
    
def main():
    # This is almost always a good thing to do at the beginning of your programs.
    locale.setlocale(locale.LC_ALL, '')

    d = Dialog(dialog="dialog")
    d.set_background_title("OS shield installation")


    # In pythondialog 3.x, you can compare the return code to d.OK, Dialog.OK or
    # "ok" (same object). In pythondialog 2.x, you have to use d.DIALOG_OK, which
    # is deprecated since version 3.0.0.
    if d.yesno("Are you REALLY sure you want to run installation?") == d.OK:
        d.msgbox("This will only update boot menu on your USB key...")
        tags = [("Catsup", "",             False),
                                      ("Mustard", "",            False),
                                      ("Pesto", "",              False),
                                      ("Mayonnaise", "",         True),
                                      ("Horse radish","",        True),
                                      ("Sun-dried tomatoes", "", True)]
        while True:
            tag = bootmenu(d, tags)
            if tag =='4)': break

    else:
        d.msgbox("To rebooting, press any key ...")
        sleep(0.5)
        #TODO: call reboot
    
def test():
    parseGrub('/tmp/grub.cfg')
        
if __name__ == '__main__':
    #main()
    test()
    sys.exit(0)        
