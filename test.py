import click
import ofx
from click.testing import CliRunner
import shutil
import unittest
import os
import sh
from sh import git


class TestOFX(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def create_of_folders(self):
        os.mkdir('addons')
        os.mkdir('apps')
        os.mkdir('libs')

    def testList(self):
        with self.runner.isolated_filesystem():
            # Test listing installed addons
            result = self.runner.invoke(ofx.cli, ['list'])

            # Test that not being in a of dir returns an error
            assert result.exit_code == 2

            # Test that being in an empty of dir returns empty list
            self.create_of_folders()

            result = self.runner.invoke(ofx.cli, ['list'])
            assert len(result.output) == 0

            #Test listing some addons
            os.mkdir('addons/ofxCV')
            os.mkdir('addons/ofxTest')
            open('addons/fakefile.txt', 'w')

            result = self.runner.invoke(ofx.cli, ['list'])
            assert 'ofxCV' in result.output
            assert 'ofxTest' in result.output
            assert 'fakeFile' not in result.output

            #Check listing works form subfolder
            ofx.os.chdir('apps')
            result = self.runner.invoke(ofx.cli, ['list'])
            assert 'ofxCV' in result.output

    def testInfo(self):
        with self.runner.isolated_filesystem():
            self.create_of_folders()

            result = self.runner.invoke(ofx.cli, ['info', 'ofxCV'])
            assert 'ofxCv' in result.output

            result = self.runner.invoke(ofx.cli, ['info', 'nonsense'])
            assert "No addon " in result.output

    def _testInstallSpecificAddon(self):
        with self.runner.isolated_filesystem():
            self.create_of_folders()

            result = self.runner.invoke(ofx.cli, ['install', 'ofxmidi'])
            assert result.exit_code == 0
            assert "Clone done" in result.output
            assert os.path.exists('addons/ofxMidi/src')

            result = self.runner.invoke(ofx.cli, ['install', 'ofxmidi'])
            assert result.exit_code == 0
            assert "already installed and up to date" in result.output

            result = self.runner.invoke(ofx.cli, ['install', 'nonsenseAddon'])
            assert "No addon named nonsenseAddon found" in result.output

            shutil.rmtree('addons/ofxMidi')
            result = self.runner.invoke(ofx.cli, ['install', 'OFXMIDI@0.7.4'])
            assert "Clone done" in result.output
            assert "0.7.4 checked out" in result.output
            os.chdir('addons/ofxMidi')
            assert "250fbc5d005a7b0a6a48b885b478cdfa8f9fb23d" in sh.git('rev-parse', 'HEAD')
            os.chdir('../../')

            result = self.runner.invoke(ofx.cli, ['install', 'ofxmidi'])
            assert "Addon ofxMidi is already installed but is not up to date" in result.output

            shutil.rmtree('addons/ofxMidi')
            result = self.runner.invoke(ofx.cli, ['install', 'danomatika/OFXMIDI@0.7.4'])
            assert "Clone done" in result.output

            # TODO: Does not work yet, but should!!
            # shutil.rmtree('addons/ofxMidi')
            # result = self.runner.invoke(ofx.cli, ['install', 'OFXMIDI@90b47b5f1c879f4fdc9a19b60ccc1a682da269e6'])
            # assert "Clone done" in result.output

            # shutil.rmtree('addons/ofxMidi')
            # result = self.runner.invoke(ofx.cli, ['install', 'OFXMIDI@90b47b5f1c8'])
            # assert "Clone done" in result.output

            # shutil.rmtree('addons/ofxMidi')
            # result = self.runner.invoke(ofx.cli, ['install', 'OFXMIDI@90b47b5f1c8'])
            # assert "Clone done" in result.output

            # shutil.rmtree('addons/ofxMidi')
            # result = self.runner.invoke(ofx.cli, ['install', 'https://github.com/danomatika/ofxMidi.git'])
            # assert "Clone done" in result.output

            # shutil.rmtree('addons/ofxMidi')
            # result = self.runner.invoke(ofx.cli, ['install', 'https://github.com/danomatika/ofxMidi.git@0.7.4'])
            # assert "Clone done" in result.output
    
    def testInstallAddonDependencies(self):
        with self.runner.isolated_filesystem():
            self.create_of_folders()

            result = self.runner.invoke(ofx.cli, ['install', 'ofxtimeline'])
            assert result.exit_code == 0
            print result.output
            assert "ofxTimeline: Clone done" in result.output
            assert "ofxTween: Clone done" in result.output
            assert os.path.exists('addons/ofxTimeline/src')
            assert os.path.exists('addons/ofxTween/src')

    
    def testInstallAppDependencies(self):
        with self.runner.isolated_filesystem():
            self.create_of_folders()
            os.chdir('apps')
            with open('description.json', 'w') as f:
                f.write('{ "ADDON_DEPENDENCIES": [ "ofxMidi@0.7.4", "OFXSYPHON"] }')

            result = self.runner.invoke(ofx.cli, ['install'])
            assert "ofxMidi: Clone done" in result.output
            assert "0.7.4 checked out" in result.output
            assert "ofxSyphon: Clone done" in result.output
            assert os.path.exists('../addons/ofxMidi/src')
            assert os.path.exists('../addons/ofxSyphon/src')

if __name__ == '__main__':
    unittest.main()
