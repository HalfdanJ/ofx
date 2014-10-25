import click
import ofx
from click.testing import CliRunner
import fake_filesystem
import fake_filesystem_shutil
import unittest


class TestOFX(unittest.TestCase):
    def setUp(self):

        self.runner = CliRunner()

        self.fk = fake_filesystem.FakeFilesystem()
        self.fk.CreateDirectory('/of')

        ofx.os = fake_filesystem.FakeOsModule(self.fk)

    def create_of_folders(self):
        self.fk.CreateDirectory('/of/addons')
        self.fk.CreateDirectory('/of/apps')
        self.fk.CreateDirectory('/of/libs')

    def testList(self):
        """ Test ofx list"""
        ofx.os.chdir('/of')

        # Test listing installed addons
        result = self.runner.invoke(ofx.cli, ['list'])

        # Test that not being in a of dir returns an error
        print result.output
        print result.exit_code
        assert result.exit_code == 2

        # Test that being in an empty of dir returns empty list
        self.create_of_folders()

        result = self.runner.invoke(ofx.cli, ['list'])
        assert len(result.output) == 0

        #Test listing some addons
        self.fk.CreateDirectory('/of/addons/ofxCV')
        self.fk.CreateDirectory('/of/addons/ofxTest')
        self.fk.CreateFile('fakeFile')

        result = self.runner.invoke(ofx.cli, ['list'])
        assert 'ofxCV' in result.output
        assert 'ofxTest' in result.output
        assert 'fakeFile' not in result.output

        #Check listing works form subfolder
        ofx.os.chdir('/of/apps')
        result = self.runner.invoke(ofx.cli, ['list'])
        assert 'ofxCV' in result.output



if __name__ == '__main__':
     unittest.main()