import csv

version_matrix_file = './versions/platform-software-matrix.txt'

class VersionManager(object):

    def __init__(self, screen_manager):

        self.sm = screen_manager

        # print(self.compatibility_check_sequence())


## CHECK COMPATIBILITY

    version_matrix = None

    def compatibility_check_sequence(self):
        self._load_matrix()
        self._check_compatibility('v0.0.10', 'v1.4.2')


    def _load_matrix(self):
        self.version_matrix = csv.DictReader(open(version_matrix_file))

    # reads in as: 'PL/SW': 'v0.1.1', 'v0.0.1': '1', 'v0.0.2': '1', ... etc.

    def _check_compatibility(self, PL_version, SW_version):
    # so get object that has PL/SW: 'vx.x.x'
        dict_object = filter(lambda platform_version: platform_version['PL/SW'] == PL_version, self.version_matrix)[0]

        if dict_object[SW_version] == '1':
            return True
        else:
            return False