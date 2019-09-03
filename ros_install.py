#! /usr/bin/env python3

import locale
from dialog import Dialog
import os, sys, subprocess
from time import sleep
import re
import tempfile

class GrubMenu():
    def __init__(self):
        self.headers = ''
        self.items=[]
        self.names = []
    def show(self):
        print(self.headers.rstrip())
        for i in self.items:
            print(i.rstrip())
gm = GrubMenu()

def detectMSBoot(partition):
    wdir = tempfile.mkdtemp()
    res = False
    
    cmd = ['sudo', 'mount', partition, wdir] # mount
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data, err = proc.communicate()
    rc = proc.returncode
    
    dest = os.path.join(wdir, 'EFI/Microsoft/Boot/bootmgfw.efi')
    if os.path.isfile(dest): res = True

    cmd = ['sudo', 'umount', wdir] #umount
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data, err = proc.communicate()

    #shutil.rmtree(wdir) #do no remove it in case it is still mounted
    return res

def parseBlkid(s):
    res = []
    ls = s.split('\n')
    ls = [ l.strip() for l in ls]
    for line in ls:
        if 'PARTLABEL="EFI System Partition"' in line:
            ws = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
            uuid = ws[1].split('=')[1].strip('"')
            partition = ws[0][:-1]
            if detectMSBoot(partition):
                res.append(uuid)
    return res
    
def detectBoot(d): #display/detectl new boot option EFI/Microsoft/Boot/bootmgfw.efi
    #find a ESP partiion, mount it to tmp direct
    gentry = '''menuentry "{0}" {
  insmod ext2
  insmod chain
  search --no-floppy --fs-uuid --set=vmroot {1}
  chainloader ($vmroot)/EFI/BOOT/loadvmm.efi
}''' #{0} name, {1} UUID
    cmd = ['blkid'] #or use 'parted' first for GPT partions
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data, err = proc.communicate()
    rc = proc.returncode
    if (rc != 0):
        d.msgbox("Can not find disk UUID, return ...")
        return -1, None
    data = data.decode('utf-8')
    res = parseBlkid(data)
    d.msgbox("Found EFI boot partitions:\n"+ '\n'.join(res))
    return 0, data

def detailBoot(d, item=None):
    if item==None:
        txt = '\n'.join( [' '+ i + ' ' for i in gm.names])
        #import pdb; pdb.set_trace()
        d.msgbox(txt)

def bootmenu(d, tags): #display current boot menu, and new option
    # We could put non-empty items here (not only the tag for each entry)
    code, tag = d.menu("select your command:",
                       choices= tags
                      )
    if code == d.OK:
        # 'tags' now contains a list of the toppings chosen by the user
        print(tag)
        return tag
    else:
        return "exit"

def parseGrub(filename):
    with open(filename, "r") as f:
        item = ''
        name = ''
        while True:
            line = f.readline()
            if not line: break
            if not item:
                if line.strip()[:9] == 'menuentry':
                    item = line
                    name = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', item)[1]
                else:
                    gm.headers += line
            else:
                if line.strip()[0]=='}':
                    gm.items.append(item)
                    gm.names.append(name)
                    item = ''
                else :
                    item += line
    #import pdb; pdb.set_trace()
    #pass
    #gm.show()
    #print (gm.names)
    
def main():
    # This is almost always a good thing to do at the beginning of your programs.
    locale.setlocale(locale.LC_ALL, '')

    d = Dialog(dialog="dialog")
    d.set_background_title("OS shield installation")
    parseGrub(sys.argv[1])

    # In pythondialog 3.x, you can compare the return code to d.OK, Dialog.OK or
    # "ok" (same object). In pythondialog 2.x, you have to use d.DIALOG_OK, which
    # is deprecated since version 3.0.0.
    if d.yesno("Are you REALLY sure you want to run installation?") == d.OK:
        d.msgbox("This will only update boot menu on your USB key...")
        tags = [("1)", "print details"),
                                ("2)", "detect and install new boot option"),
                                ("3)", "delete boot option"),
                                ("4)", "exit"),
                                ]
        while True:
            tag = bootmenu(d, tags)
            if tag =='1)': detailBoot(d)
            elif tag == '2)': detectBoot(d)
            if tag =='4)' or tag =='exit': break

    else:
        d.msgbox("To rebooting, press any key ...")
        sleep(0.5)
        #TODO: call reboot
    
def test():
    parseGrub('/tmp/grub.cfg')
        
if __name__ == '__main__':
    main()
    #test()
    sys.exit(0)        
