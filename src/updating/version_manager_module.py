import csv
import subprocess, sys, os

from time import sleep

from updating import usb_storage

version_matrix_file = './versions/platform-software-matrix.txt'

usb_remote_path = '/media/usb/'
remote_cache = './remoteCache/'

platform_origin_url = 'https://github.com/YetiTool/console-raspi3b-plus-platform.git'
easycut_origin_url = 'https://github.com/YetiTool/easycut-smartbench.git'
version_manager_origin_url = 'https://github.com/YetiTool/smartbench-version-manager.git'

platform_usb_remote_bundle = ''
easycut_usb_remote_bundle = ''
version_manager_usb_remote_bundle = ''

os.environ['PYTHONUNBUFFERED'] = "1"

### SYNTAX GUIDE

## Use variables: platform, easycut, version_manager to specify which repo the function should action in

## Successful bash exit codes are typically == 0

### REPO PATHS

home_dir="/home/pi/"
easycut_path = home_dir + "easycut-smartbench/"
platform_path = home_dir + "console-raspi3b-plus-platform/"
version_manager_path = home_dir + "smartbench-version-manager/"


class VersionManager(object):

    current_platform_version = ''
    current_easycut_version = ''
    current_version_manager_version = ''

    latest_platform_version = ''
    latest_platform_beta = ''
    latest_easycut_version = ''
    latest_easycut_beta = ''
    latest_version_manager_version = ''
    latest_version_manager_beta = ''

    def __init__(self, screen_manager):

        self.sm = screen_manager

        self.usb_stick = usb_storage.USB_storage(self.sm)
        self.usb_stick.enable()

        # need to build in: 
        # also what happens if: - do fetch, lose wifi, checkout tag/branch/etc? 

        # CONNECTIVITY CHECKS, i.e. if wifi or if usb: add usb

        # Simplify what update we look for from now on: Standardize update packages from version x.x.x onwards to look for 
        # SmartBench-SW-update...zip, and then unpack that to find git repo zips, and then unpack those accordingly. 

    def run_in_shell(self, repo, cmd):

        if repo == 'platform': dir_path = platform_path
        elif repo == 'easycut': dir_path = easycut_path
        elif repo == 'version_manager': dir_path = version_manager_path
        elif repo == 'home': dir_path = home_dir

        full_cmd = 'cd ' + dir_path + ' && ' + cmd

        self.sm.get_screen('more_details').add_to_verbose_buffer('Send: ' + str(full_cmd))

        proc = subprocess.Popen(full_cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            shell = True
        )

        stdout, stderr = proc.communicate()
        exit_code = int(proc.returncode)

        self.sm.get_screen('more_details').add_to_verbose_buffer('Receive: ' + str(exit_code) + str(stdout) + str(stderr))

        if exit_code == 0:
            bool_out = True
        else:
            bool_out = False

        return [str(bool_out), (stdout), (stderr)]


    def outcome_to_screens(self, *args):
        # initial debug test
        self.sm.get_screen('updating').add_to_user_friendly_buffer(args)

    def check_connections(self):
        # Keep tabs on wifi connection
        self.check_wifi_connection(1)
        # self.poll_wifi = Clock.schedule_interval(self.check_wifi_connection, self.WIFI_CHECK_INTERVAL)

        # Set up and keep tabs on usb connection
        self.check_USB_status(1)
        # self.poll_USB = Clock.schedule_interval(self.check_USB_status, 0.25)


    def standard_update(self):
        self.set_remotes()
        self._clone_backup_repos_from_URL() # if wifi available

        if self.prepare_for_update():
            fetch_outcome = self._fetch_tags_for_all_repos()

            self.outcome_to_screens(fetch_outcome[1:])

            if fetch_outcome[0]:

                # get latest non-beta versions 
                self.refresh_latest_versions()

                # check compatibility
                if self.compatibility_check(self.latest_platform_version, self.latest_easycut_version):
                    platform_to_checkout = self.latest_platform_version
                    easycut_to_checkout = self.latest_easycut_version
                else:
                    # compatibility check has failed, need to check which is the latest platform version 
                    # compatibile with the software:
                    platform_to_checkout = self._find_compatible_platform(self.latest_easycut_version)
                    easycut_to_checkout = self.latest_easycut_version

                    # will want to update screen to reflect this

                    if self._do_checkout_and_check(self, 'easycut', easycut_to_checkout):
                        if self._do_checkout_and_check(self, 'platform', platform_to_checkout):

                            # double check compatibility of current versions
                            if self.compatibility_check(self.current_platform_version, self.current_easycut_version):
                            
                                # do ansible run, and hopefully do cursory check that it worked??
                                # need to test behaviour of this with & without wifi
                                ansible_outcome = self._do_platform_ansible_run()

                                self.outcome_to_screens(ansible_outcome[1])

                                if ansible_outcome[0]: 
                                    return True

                                else:
                                    # argh, something's gone wrong. need to play with ansible to figure out what should happen next
                                    # in this scenario
                                    pass

                            else:
                                platform_to_checkout = self._find_compatible_platform(self.current_easycut_version)
                                self.outcome_to_screens(platform_to_checkout)
                                if self._do_checkout_and_check(self, 'platform', platform_to_checkout):
                                    if self.compatibility_check(self.current_platform_version, self.current_easycut_version):
                                        ansible_outcome = self._do_platform_ansible_run()
                                        if ansible_outcome[0]: 
                                            return True
                                        else:
                                            # argh, something's gone wrong. need to play with ansible to figure out what should happen next
                                            # in this scenario
                                            pass
                                    else:
                                        # something is going wrong, 
                                        pass
                                else:
                                    # something is going wrong
                                    pass



        # if update is not succcessful for whatever reason, will need to execute a backup plan
        return False

    def _do_checkout_and_check(self, repo, version):
        # do checkout
        # also want to send update messages to screen here...
        checkout_success = self._checkout_new_version(repo, version)
        if checkout_success[0]:

            # confirm new version
            new_current_version = self._current_version(repo)[1]

            # update class variables
            if repo == 'platform': current_platform_version = new_current_version
            if repo == 'easycut': current_easycut_version = new_current_version
            if repo == 'version_manager': current_version_manager_version = new_current_version

            # check current version == latest checked out version
            if version == new_current_version:
                return True

            else:
                return False

        else:
            return False


    ## BETA UPDATES
    # was thinking these for software, but obvs may affect platform as well... how we wanna skin this?? 


    ## CHECK COMPATIBILITY

    version_matrix = None

    def compatibility_check(self, PL_version, SW_version):
        self._load_matrix()
        return self._check_compatibility(PL_version, SW_version)

    # component compatibility functions
    def _load_matrix(self):
        self.version_matrix = csv.DictReader(open(version_matrix_file), delimiter = '\t')
        # reads in as: 'PL\SW': 'v0.1.1', 'v0.0.1': '1', 'v0.0.2': '1', ... etc.

    def _check_compatibility(self, PL_version, SW_version):
        # so get object that has PL/SW: 'vx.x.x'
        dict_object = filter(lambda platform_version: platform_version['PL-SW'] == PL_version, self.version_matrix)[0]

        # return if compatible
        if dict_object[SW_version] == '1':
            return True
        else:
            return False

    def _find_compatible_platform(self, SW_version):
        # this needs checking
        dict_object = filter(lambda software_version: software_version[SW_version] == '1', self.version_matrix)[-1]
        return dict_object['PL-SW']


    ## SET UP REPO
    def set_remotes(self):

        # need to set the usb remote filepaths

        set_up_platform_repo_outcome = self._set_up_usb_repo('platform', usb_remote_path)
        self.outcome_to_screens(set_up_platform_repo_outcome)

        set_up_easycut_repo_outcome = self._set_up_usb_repo('easycut', usb_remote_path)
        self.outcome_to_screens(set_up_easycut_repo_outcome)

        set_up_version_manager_repo_outcome = self._set_up_usb_repo('version_manager', usb_remote_path)
        self.outcome_to_screens(set_up_version_manager_repo_outcome)

        platform_origin_outcome = self._set_origin_URL('platform')
        self.outcome_to_screens(platform_origin_outcome)

        easycut_origin_outcome = self._set_origin_URL('easycut')
        self.outcome_to_screens(easycut_origin_outcome)

        version_manager_origin_outcome = self._set_origin_URL('version_manager')
        self.outcome_to_screens(version_manager_origin_outcome)

        # if set_up_platform_repo_outcome[0]:
        #     print(set_up_platform_repo_outcome[:-1]) # when screens are set up, print this outcome to details screen

        # if set_up_easycut_repo_outcome[0]:
        #     print(set_up_easycut_repo_outcome[:-1]) # when screens are set up, print this outcome to details screen

        # if set_up_version_manager_repo_outcome[0]:
        #     print(set_up_version_manager_repo_outcome[:-1]) # when screens are set up, print this outcome to details screen

        # if platform_origin_outcome[0]:
        #     print(platform_origin_outcome[:-1]) # when screens are set up, print this outcome to details screen

        # if easycut_origin_outcome[0]:
        #     print(easycut_origin_outcome[:-1]) # when screens are set up, print this outcome to details screen

        # if version_manager_origin_outcome[0]:
        #     print(version_manager_origin_outcome[:-1]) # when screens are set up, print this outcome to details screen

    ## CHECK REPO QUALITY

    def prepare_for_update(self):

        platform_fsck_outcome = self._fsck_repo('platform')
        easycut_fsck_outcome = self._fsck_repo('easycut')
        version_manager_fsck_outcome = self._fsck_repo('version_manager')

        if not platform_fsck_outcome[0]:
            print(platform_fsck_outcome) # when screens are set up, print this outcome to details screen
            # try repair based on outcome
            # if it doesn't succeed, then can return False and quit the function
            if not self.standard_repair_procedure(platform): return False

        if not easycut_fsck_outcome[0]:
            print(easycut_fsck_outcome) # when screens are set up, print this outcome to details screen
            # try repair based on outcome
            if not self.standard_repair_procedure(easycut): return False

        if not version_manager_fsck_outcome[0]:
            print(version_manager_fsck_outcome) # when screens are set up, print this outcome to details screen
            # try repair based on outcome
            if not self.standard_repair_procedure(version_manager): return False

        return True

    def standard_repair_procedure(self, repo):
        # git-repair
        repair_outcome = self._repair_repo(repo)
        # git prune
        prune_outcome = self._prune_repo(repo)
        # git gc 
        gc_outcome = self._gc_repo(repo)
        # git fsck and report
        fsck_outcome = self._fsck_reop(repo)

        # print details of repair to screen
        if (repair_outcome[0] and prune_outcome[0] and gc_outcome[0] and fsck_outcome[0]):
            return True

        else:
            print 'something failed...check details...may need to reclone'
            # send all outcome deets to screen
            return False

    def extreme_repair_procedure(self, repo):

        bundle_extension = ''

        if repo == 'platform': 
            path = platform_path
            origin = platform_origin_url
            usb_origin = ''
        elif repo == 'easycut': 
            path = easycut_path
            origin = easycut_origin_url
            usb_origin = ''
        elif repo == 'version_manager': 
            path = version_manager_path
            origin = version_manager_origin_url
            usb_origin = ''

        # rename existing dir, so that it becomes '-corrupted', which keeps it separate to backup dirs
        self.run_in_shell('home', 'mv -f ' + path + ' ' + path + '-corrupted')

        # then try: 
        #    git clone from URL
        #    git clone from USB repo
        #    git clone from backup repo

        clone_from_url_outcome = self._clone_fresh_repo(origin)
        if not clone_from_url_outcome[0]:
            clone_from_usb_outcome = self._clone_fresh_repo(usb_origin)
            if not clone_from_usb_outcome[0]:
                self._clone_fresh_repo(path + '-backup' + bundle_extension)




    ## FETCH TAGS AND CHECKOUT 
    def refresh_latest_versions(self):

            platform_version_list = bash('get_tag_list platform')
            easycut_version_list = bash('get_tag_list easycut')
            version_manager_version_list = bash('get_tag_list version_manager')

            self.latest_platform_version = str([tag for tag in platform_version_list if "beta" not in tag][0])
            self.latest_platform_beta = str([tag for tag in platform_version_list if "beta" in tag][0])

            self.latest_easycut_version = str([tag for tag in easycut_version_list if "beta" not in tag][0])
            self.latest_easycut_beta = str([tag for tag in easycut_version_list if "beta" in tag][0])

            self.latest_version_manager_version = str([tag for tag in version_manager_version_list if "beta" not in tag][0])
            self.latest_version_manager_beta = str([tag for tag in version_manager_version_list if "beta" in tag][0])

#-------------------------------------------------------------------------------------------------------------------

    ### CORE GIT COMMANDS
    ##--------------------------------------------------------------------------------------------------------------

    def _go_to_dir(self, repo):

        if repo == 'platform':
            self.run_in_shell('cd ' + platform_path)
        elif repo == 'easycut':
            self.run_in_shell('cd ' + easycut_path)
        elif repo == 'version_manager':
            self.run_in_shell('cd ' + version_manager_path)
        elif repo == 'home':
            self.run_in_shell('cd ' + home_dir)            

    ### FETCH

    ## fetch tags  

    def _fetch_tags(self, repo):
        # fetch tags from all remotes (including any temporary USB repos)
        # tries twice, just on the off-chance that there's a brief loss of connection or similar
        success = self.run_in_shell(repo, 'git fetch --all -t')
        if success[0]: 
            return_success
        else:
            sleep(10)
            self.run_in_shell(repo, 'git fetch --all -t')

    ## fetch tags for all repositories

    def _fetch_tags_for_all_repos(self):

        platform_success = self._fetch_tags('platform')
        easycut_success = self._fetch_tags('easycut')
        version_manager_success = self._fetch_tags('version_manager')

        return [platform_success, easycut_success, version_manager_success]

    ## return list of 10 most recent tags

    def _get_tag_list(self, repo):
        return self.run_in_shell(repo, 'git tag --sort=-refname |head -n 10')

    ### DEBUGGING

    ## get fsck output

    def _fsck_repo(self, repo):
        return self.run_in_shell(repo, 'git fsck --lost-found')

    ### PREPATORY COMMANDS

    ## set up temporary repository from USB
    # arguments: argument 1 is the repo we're setting up for, argument 2 is the usb filepath

    def _set_up_usb_repo(self, repo, usb_remote_path):
        return self.run_in_shell(repo, 'git remote add temp_repository ' + usb_remote_path)

    # set origin URL (just in case)
    def _set_origin_URL(self, repo):
        
        if repo == 'platform':
            origin_url = platform_origin_url
        elif repo == 'easycut':
            origin_url = easycut_origin_url
        elif repo == 'version_manager':
            origin_url = version_manager_origin_url

        return self.run_in_shell(repo, 'git remote set-url origin ' + origin_url)

    # describe current tag
    def _current_version(self, repo):
        return self.run_in_shell(repo, 'git describe --tags')       


    ### DO UPDATES

    ## CHECKOUT NEW VERSIONS
    def _checkout_new_version(self, repo, version):
        return self.run_in_shell(repo, 'git checkout ' + version + ' -f')  


    ## PLATFORM ANSIBLE RUN
    def _do_platform_ansible_run(self):
        return self.run_in_shell('/home/pi/console-raspi3b-plus-platform/ansible/templates/ansible-start.sh')


    ### REPAIR AND BACKUPS
    def _clone_fresh_repo(self, origin):
        return self.run_in_shell('home', 'git clone ' + origin)

    # arguments are origin = git URL (or bundle to clone), target = backup target directory
    def _clone_backup_repo(self, origin, target):
        if os.path.exists(home_dir + target):
            self.outcome_to_screens('backup repo ' + target + ' already exists')
            return True
        else:
            self.outcome_to_screens('Creating backup repository in ' + target + '...')
            outcome = self.run_in_shell('home', 'git clone --bare ' + origin + ' ' + home_dir + target)

            if outcome[0]: 
                self.outcome_to_screens('\tBackup repository ' + target + ' created successfully')
            else:
                self.outcome_to_screens('\tBackup repository could not be created. Check details for more information.')

            return outcome[0]

    # set up backups with git clone
    def _clone_backup_repos_from_URL(self):
        platform_success = self._clone_backup_repo(platform_origin_url, 'console-raspi3b-plus-platform-backup')
        easycut_success = self._clone_backup_repo(easycut_origin_url, 'easycut-smartbench-backup')
        version_manager_success = self._clone_backup_repo(version_manager_origin_url, 'smartbench-version-manager-backup')

        return platform_success, easycut_success, version_manager_success

    def _clone_backup_repos_from_USB(self):
        platform_success = self._clone_backup_repo(platform_usb_remote_bundle, 'console-raspi3b-plus-platform-backup')
        easycut_success = self._clone_backup_repo(easycut_usb_remote_bundle, 'easycut-smartbench-backup')
        version_manager_success = self._clone_backup_repo(version_manager_usb_remote_bundle, 'smartbench-version-manager-backup')

        return platform_success, easycut_success, version_manager_success
    
    # need a create bundles section, and then a clone from bundles section

    # git-repair
    def _repair_repo(self, repo):
        initial_run_success = self.run_in_shell(repo, 'git-repair --force')
        if initial_run_success[0] != 0:
            install_success = self.run_in_shell(repo, 'sudo aptitude install git-repair')
            if install_success[0] == 0:
                return self.run_in_shell(repo, 'git-repair --force')
            else:
                return install_success
        else:
            return initial_run_success

    # git prune
    def _prune_repo(self, repo):
        return self.run_in_shell(repo, 'git prune')

    # git gc --aggressive
    def _gc_repo(self, repo):
        return self.run_in_shell(repo, 'git gc --aggressive')

# -----------------------------------------------------------------------------------------------
# CONNECTIONS TO REMOTES
# -----------------------------------------------------------------------------------------------

    def check_wifi_connection(self):

        try:
            f = os.popen('hostname -I')
            first_info = f.read().strip().split(' ')[0]
            if len(first_info.split('.')) == 4:
                return True
            else:
                return False

        except:
            return False

    def check_USB_path(self):

        if self.usb_stick.is_available():
            # if os.path.exists():
            #     return True
            pass
        else:
            return False
