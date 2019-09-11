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
        self.diskids = []
    def show(self):
        print(self.headers.rstrip())
        for i in self.items:
            print(i.rstrip())
    def save(self, f):
        f.write(self.headers.strip()+'\n')
        for i in self.items:
            f.write(i.rstrip()+'\n')
gm = GrubMenu()

def deleteBoot(d):
    tags = []
    for i in range(len(gm.names)):
        if gm.names[i]=='OSShield': continue
        tags.append((gm.names[i], gm.diskids[i]))
    code, tag = d.menu("OS shield can not be deleted.\n\nDelete the boot option: ",
                       choices= tags
                      )
    if code == d.OK:
        # 'tags' now contains a list of the toppings chosen by the user
        idx = gm.names.index(tag)
        del gm.names[idx]
        del gm.diskids[idx]
        return tag

def detectMSBoot(partition):
    wdir = tempfile.mkdtemp(prefix='efidXX')
    res = False
    
    cmd = ['mount', partition, wdir] # mount
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data, err = proc.communicate()
    rc = proc.returncode
    
    dest = os.path.join(wdir, 'EFI/Microsoft/Boot/bootmgfw.efi')
    if os.path.isfile(dest): res = True
    
    cmd = ['umount', wdir] #umount
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
            if detectMSBoot(partition) or True:
                res.append(uuid)
    return res
    
def detectBoot(d): #display/detectl new boot option EFI/Microsoft/Boot/bootmgfw.efi
    #find a ESP partiion, mount it to tmp direct
    gentry = '''menuentry "{0}" {{
  insmod ext2
  insmod chain
  search --no-floppy --fs-uuid --set=vmroot {1}
  #chainloader ($vmroot)/EFI/BOOT/loadvmm.efi
  chainloader ($vmroot)/EFI/Microsoft/Boot/bootmgfw.efi
}}\n''' #{0} name, {1} UUID
    cmd = ['blkid'] #or use 'parted' first for GPT partions
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data, err = proc.communicate()
    rc = proc.returncode
    if (rc != 0):
        d.msgbox("Can not find disk UUID, return ...")
        return -1, None
    data = data.decode('utf-8')
    res1 = parseBlkid(data)
    res = []
    for uid in res1:
        if uid in gm.diskids: continue
        res.append(uid)
        
    if len(res) ==0:
        d.msgbox("Can not find new bootable Windows disk, return ...")
        return -1, None
        
    counter = 1
    tags = [ (str(res.index(r)+1), r) for r in res] 
    code, tag = d.menu("Choose this disk:",
                       choices= tags
                      )
    if code == d.OK:
        # 'tags' now contains a list of the toppings chosen by the user
        idx = int(tag) -1
        rc, name = d.inputbox(text="Please input the name of this boot option:", init="windows")
        if rc == d.OK:
            gm.names.append(name)
            gm.diskids.append(res[idx])
            gm.items.append(gentry.format(name, res[idx]))
    return 0, data

def detailBoot(d, item=None):
    if item==None:
        txt = '\n'.join( [', '.join([str(i), 'Name:'+gm.names[i], 'Disk UUID:'+gm.diskids[i]]) for i in range(len(gm.names))])
        #import pdb; pdb.set_trace()
        d.msgbox(txt, height=20, width=80)

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

def saveGrub(filename='/tmp/a.grub'):
    with open(filename, "w") as f:
        gm.save(f)
       
def parseGrub(filename):
    with open(filename, "r") as f:
        item = ''
        name = ''
        disk_uuid = ''
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
                    item += line
                    gm.items.append(item)
                    gm.names.append(name)
                    item = ''
                    name = ''
                    disk_uuid = ''
                else :
                    item += line
                    if 'search --no-floppy --fs-uuid' in line:
                        disk_uuid =  re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', item)[-1]
                        gm.diskids.append(disk_uuid)
    assert(len(gm.names) >0 and len(gm.names)==len(gm.diskids))
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
        tags = [("1)", "print/review details"),
                                ("2)", "detect Windows and install new boot option"),
                                ("3)", "delete boot option"),
                                ("4)", "save & exit"),
                                ("5)", "quit without save"),
                                ]
        while True:
            tag = bootmenu(d, tags)
            if tag =='1)': detailBoot(d)
            elif tag == '2)': detectBoot(d)
            elif tag == '3)': deleteBoot(d)
            if tag =='4)' or tag =='exit': 
                saveGrub()
                break
            if tag =='5)': break
        gm.show()
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
