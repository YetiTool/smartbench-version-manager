import csv, os

version_matrix_file = './versions/platform-software-matrix.txt'

run_core_git_functions = './src/updating/draft_eval_func.sh src/updating/core_git_functions.sh '

usb_remote = '/media/usb/'

platform_origin_url = 'https://github.com/YetiTool/console-raspi3b-plus-platform.git'
easycut_origin_url = 'https://github.com/YetiTool/easycut-smartbench.git'
version_manager_origin_url = 'https://github.com/YetiTool/smartbench-version-manager.git'

class VersionManager(object):

    def __init__(self, screen_manager):

        self.sm = screen_manager

    ## STANDARD UPDATE PROCEDURE

    self.set_remotes()
    if self.prepare_for_update():
        fetch_outcome = os.popen(run_core_git_functions + 'fetch_tags_for_all_repos').read()




    ## FACTORY SET-UP FUNCTIONS

    ## CHECK COMPATIBILITY

    version_matrix = None

    def compatibility_check_sequence(self, PL_version, SW_version):
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

    ## SET UP REPO

    def set_remotes(self):

        set_up_platform_repo_outcome = os.popen(run_core_git_functions + 'set_up_usb_repo platform' + usb_remote).read()
        set_up_easycut_repo_outcome = os.popen(run_core_git_functions + 'set_up_usb_repo easycut' + usb_remote).read()
        set_up_version_manager_repo_outcome = os.popen(run_core_git_functions + 'set_up_usb_repo version_manager' + usb_remote).read()

        platform_origin_outcome = os.popen(run_core_git_functions + 'set_origin_URL platform' + platform_origin_url).read()
        easycut_origin_outcome = os.popen(run_core_git_functions + 'set_origin_URL easycut' + easycut_origin_url).read()
        version_manager_origin_outcome = os.popen(run_core_git_functions + 'set_origin_URL version_manager' + version_manager_origin_url).read()

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

        platform_fsck_outcome = os.popen(run_core_git_functions + 'fsck_repo platform').read()
        easycut_fsck_outcome = os.popen(run_core_git_functions + 'fsck_repo easycut').read()
        version_manager_fsck_outcome = os.popen(run_core_git_functions + 'fsck_repo version_manager').read()

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
        repair_outcome = os.popen(run_core_git_functions + 'repair_repo ' + repo).read()
        # git prune
        prune_outcome = os.popen(run_core_git_functions + 'prune_repo ' + repo).read()
        # git gc 
        gc_outcome = os.popen(run_core_git_functions + 'gc_repo ' + repo).read()
        # git fsck and report
        fsck_outcome = os.popen(run_core_git_functions + 'fsck_repo ' + repo).read()

        # print details of repair to screen
        if ((repair_outcome[-1])*(prune_outcome[-1])*(gc_outcome[-1])*(fsck_outcome[-1])) == int(False):
            print 'something failed...check details...may need to reclone'

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
    def latest_versions(self):
            sw_version_list = (str(os.popen("git tag --sort=-refname |head -n 10").read()).split('\n'))
            self.latest_sw_version = str([tag for tag in sw_version_list if "beta" not in tag][0])
            self.latest_sw_beta = str([tag for tag in sw_version_list if "beta" in tag][0])

