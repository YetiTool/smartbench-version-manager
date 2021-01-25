'''
Created on 3 Feb 2018

- Stolen from easycut repo for doing USB updates

WARNINGS:
- For Linux, make sure that /media/usb/ dir has already been created
- Windows for debug, assumes a single default path which may or may not change - check default variable
- Insecure for Linux
- Don't forget to disable() when not in use, since there's a clock running on it

@author: Ed
'''

from kivy.clock import Clock
import sys, os, subprocess


usb_remote_path = '/media/usb/'
remoteCache_path = './remoteCache/'

remote_cache_platform = remoteCache_path + "console-raspi3b-plus-platform/"
remote_cache_easycut = remoteCache_path + "easycut-smartbench/"
remote_cache_version_manager = remoteCache_path + "smartbench-version-manager/"

class USB_storage(object):
    
    # Default paths
    windows_usb_path = "E:\\" 
    linux_usb_path = "/media/usb/"

    # For debug
    IS_USB_VERBOSE = True
    
    poll_usb_event = None
    mount_event = None
    stick_enabled = False
 
    alphabet_string = 'abcdefghijklmnopqrstuvwxyz'
 
    def __init__(self, screen_manager, version_manager):
        
        self.sm = screen_manager
        self.vm = version_manager

        if sys.platform == "win32":
            self.usb_path = self.windows_usb_path
        else:
            self.usb_path = self.linux_usb_path

    def enable(self):
        print 'enable usb'
        if self.stick_enabled != True:
            self.start_polling_for_usb()
            self.stick_enabled = True

    def disable(self):
        self.stick_enabled = False
        self.stop_polling_for_usb()
        if self.is_usb_mounted_flag == True:
            if sys.platform != "win32":
                self.unmount_linux_usb()
    
    def is_available(self):
        
        files_in_usb_dir = []
        try:
            files_in_usb_dir = os.listdir(self.usb_path)
        except:
            pass
        if files_in_usb_dir:
            return True
        else:
            return False
    
    def get_path(self):
        return self.usb_path
    
    def start_polling_for_usb(self):
        self.poll_usb_event = Clock.schedule_interval(self.get_USB, 0.25)
    
    def stop_polling_for_usb(self):
        if self.poll_usb_event != None: Clock.unschedule(self.poll_usb_event)
        if self.mount_event != None: Clock.unschedule(self.mount_event)

    is_usb_mounted_flag = False
    is_usb_mounting = False

    def get_USB(self, dt):
        
        # Polled by Clock to enable button if USB storage device is present, if so, mount or unmount as necessary
        # Linux
        if sys.platform != "win32":
            try:
                files_in_usb_dir = os.listdir(self.linux_usb_path)
                
                # If files are in directory
                if files_in_usb_dir:
                    self.is_usb_mounted_flag = True
                    if self.IS_USB_VERBOSE: print 'USB: OK'

                # If directory is empty
                else:
                    if self.IS_USB_VERBOSE: print 'USB: NONE'

                    # UNmount the usb if: it is mounted but not present (since the directory is empty)
                    if self.is_usb_mounted_flag:
                        self.unmount_linux_usb()
                    
                    # IF not mounted and location empty, scan for device
                    else:
                        # read devices dir
                        devices = os.listdir('/dev/')
#                         for device in devices:
                        for char in self.alphabet_string:
                            if ('sd' + char) in devices: # sda is a file to a USB storage device. Subsequent usb's = sdb, sdc, sdd etc
                                self.stop_polling_for_usb() # temporarily stop polling for USB while mounting, and attempt to mount
                                if self.IS_USB_VERBOSE: print 'Stopped polling'
                                self.mount_event = Clock.schedule_once(lambda dt: self.mount_linux_usb('sd' + char), 1) # allow time for linux to establish filesystem after os detection of device
                                break
            except (OSError):
                pass

    def unmount_linux_usb(self):

        unmount_command = 'echo posys | sudo umount -fl '+ self.linux_usb_path

        try:
            os.system(unmount_command)
                       
        except:
            if self.IS_USB_VERBOSE: print 'FAILED: Could not UNmount USB'

        def check_linux_usb_unmounted():
            if sys.platform != "win32":

                files_in_usb_dir = os.listdir(self.linux_usb_path)
                
                # If files are in directory
                if files_in_usb_dir:
                    self.is_usb_mounted_flag = True
                    if self.IS_USB_VERBOSE: print 'USB: STILL MOUNTED'

                # If directory is empty
                else:      
                    if self.IS_USB_VERBOSE: print 'USB: UNMOUNTED'
                    self.is_usb_mounted_flag = False
                    Clock.unschedule(poll_for_dismount)
  
        
        poll_for_dismount = Clock.schedule_interval(lambda dt: check_linux_usb_unmounted(), 0.5)
    
    def mount_linux_usb(self, device):

        if self.mount_event != None: Clock.unschedule(self.mount_event)
        if self.IS_USB_VERBOSE: print 'Attempting to mount'

        mount_command = "echo posys | sudo mount /dev/" + device + "1 " + self.linux_usb_path # TODO: NOT SECURE
        try:
            os.system(mount_command)
            self.is_usb_mounted_flag = True
            self.start_polling_for_usb() # restart checking for USB
            if self.IS_USB_VERBOSE: print 'USB: MOUNTED'

            else:
                pass

        except:
            if self.IS_USB_VERBOSE: print 'FAILED: Could not mount USB'        
            self.is_usb_mounted_flag = False
            self.start_polling_for_usb()  # restart checking for USB


    def import_remotes_from_usb(self):

        print 'start import function'
        try:
            # look for new SB file name first
            # have made this really quite flexible, in case of future preferences!
            zipped_file_name = (self.run_in_shell("find /media/usb/ -maxdepth 2 -name '*mart*ench*pdate*.zip'")[1]).strip('\n')

            # clear out the remoteCache directory if there's anything in it
            if os.path.exists(remoteCache_path + '*/'): self.run_in_shell('sudo rm ' + remoteCache_path + '*/ -r')
            unzip_dir_command = 'unzip -o -q ' + zipped_file_name + ' -d ' + remoteCache_path
            self.run_in_shell(unzip_dir_command)

            # find all the repos in the remoteCache path and if they are there, set flag in vm.
            if (os.path.exists(remote_cache_platform) and
                os.path.exists(remote_cache_easycut) and
                os.path.exists(remote_cache_version_manager)):
                self.vm.use_usb_remote =  True

            else:
                self.vm.use_usb_remote =  False

        except:
            self.vm.use_usb_remote =  False

    def run_in_shell(self, cmd):

        self.vm.el.format_command(cmd)

        proc = subprocess.Popen(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            shell = True
        )

        stdout, stderr = proc.communicate()
        exit_code = int(proc.returncode)

        print(str(exit_code))
        print(str(stdout))
        print(str(stderr))

        self.vm.el.format_ouputs(exit_code, stdout, stderr)

        if exit_code == 0:
            bool_out = True
        else:
            bool_out = False

        return [bool_out, stdout, stderr]
