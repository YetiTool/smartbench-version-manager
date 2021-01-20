import csv, os

version_matrix_file = './versions/platform-software-matrix.txt'

run_core_git_functions = './src/updating/do.sh src/updating/core_git_functions.sh '

usb_remote = '/media/usb/'

platform_origin_url = 'https://github.com/YetiTool/console-raspi3b-plus-platform.git'
easycut_origin_url = 'https://github.com/YetiTool/easycut-smartbench.git'
version_manager_origin_url = 'https://github.com/YetiTool/smartbench-version-manager.git'

def bash(self, func_plus_args):
    return (str(os.popen(run_core_git_functions + func_plus_args).read()).split('\n'))

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

    ## need to build in: 
    # - double fetch attempts (as sometimes can just be a dodge connection
    # also what happens if: - do fetch, lose wifi, checkout tag/branch/etc? 

    ## STANDARD UPDATE PROCEDURE
    def standard_update(self):
        self.set_remotes()
        if self.prepare_for_update():
            fetch_outcome = bash('fetch_tags_for_all_repos')

            if fetch_outcome[-1] == int(True):

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
                                if bash('do_platform_ansible_run'):
                                    return True

                                else:
                                    # argh, something's gone wrong. need to play with ansible to figure out what should happen next
                                    # in this scenario
                                    pass

                            else:
                                platform_to_checkout = self._find_compatible_platform(self.current_easycut_version)
                                if self._do_checkout_and_check(self, 'platform', platform_to_checkout):
                                    if self.compatibility_check(self.current_platform_version, self.current_easycut_version):
                                        if bash('do_platform_ansible_run'):
                                            return True

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
        checkout_success = bash('checkout_new_version ' + repo + ' ' + version)
        if checkout_success[-1] == int(True):

            # confirm new version
            new_current_version = bash('current_version ' + repo)[0]

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




    ## FACTORY SET-UP FUNCTIONS

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
        pass

    ## SET UP REPO

    def set_remotes(self):

        set_up_platform_repo_outcome = bash('set_up_usb_repo platform ' + usb_remote)
        set_up_easycut_repo_outcome = bash('set_up_usb_repo easycut ' + usb_remote)
        set_up_version_manager_repo_outcome = bash('set_up_usb_repo version_manager ' + usb_remote)

        platform_origin_outcome = bash('set_origin_URL platform ' + platform_origin_url)
        easycut_origin_outcome = bash('set_origin_URL easycut ' + easycut_origin_url)
        version_manager_origin_outcome = bash('set_origin_URL version_manager ' + version_manager_origin_url)

        if set_up_platform_repo_outcome[-1] == int(False):
            print(set_up_platform_repo_outcome[:-1]) # when screens are set up, print this outcome to details screen

        if set_up_easycut_repo_outcome[-1] == int(False):
            print(set_up_easycut_repo_outcome[:-1]) # when screens are set up, print this outcome to details screen

        if set_up_version_manager_repo_outcome[-1] == int(False):
            print(set_up_version_manager_repo_outcome[:-1]) # when screens are set up, print this outcome to details screen

        if platform_origin_outcome[-1] == int(False):
            print(platform_origin_outcome[:-1]) # when screens are set up, print this outcome to details screen

        if easycut_origin_outcome[-1] == int(False):
            print(easycut_origin_outcome[:-1]) # when screens are set up, print this outcome to details screen

        if version_manager_origin_outcome[-1] == int(False):
            print(version_manager_origin_outcome[:-1]) # when screens are set up, print this outcome to details screen

        return True

    ## CHECK REPO QUALITY

    def prepare_for_update(self):

        platform_fsck_outcome = bash('fsck_repo platform')
        easycut_fsck_outcome = bash('fsck_repo easycut')
        version_manager_fsck_outcome = bash('fsck_repo version_manager')

        if platform_fsck_outcome[-1] == int(False):
            print(platform_fsck_outcome[:-1]) # when screens are set up, print this outcome to details screen
            # try repair based on outcome
            # if it doesn't succeed, then can return False and quit the function
            if not self.standard_repair_procedure(platform): return False

        if easycut_fsck_outcome[-1] == int(False):
            print(easycut_fsck_outcome[:-1]) # when screens are set up, print this outcome to details screen
            # try repair based on outcome
            if not self.standard_repair_procedure(easycut): return False

        if version_manager_fsck_outcome[-1] == int(False):
            print(version_manager_fsck_outcome[:-1]) # when screens are set up, print this outcome to details screen
            # try repair based on outcome
            if not self.standard_repair_procedure(version_manager): return False

        return True


    ## REPAIR FUNCTIONS

    def standard_repair_procedure(self, repo):
        # git-repair
        repair_outcome = bash('repair_repo ' + repo)
        # git prune
        prune_outcome = bash('prune_repo ' + repo)
        # git gc 
        gc_outcome = bash('gc_repo ' + repo)
        # git fsck and report
        fsck_outcome = bash('fsck_repo ' + repo)

        # print details of repair to screen
        if ((repair_outcome[-1])*(prune_outcome[-1])*(gc_outcome[-1])*(fsck_outcome[-1])) == int(False):
            print 'something failed...check details...may need to reclone'
            return False

        else:
            return True

    def extreme_repair_procedure(self):

        #...best way to do this? 
        # rename existing dir, so that it becomes '-corrupted' or something
        # then try: 
        #    git clone from URL
        #    git clone from USB repo
        #    git clone from backup repo

        pass


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

