import click
import os
import re
import urllib2
import simplejson
import shutil
import sh
from sh import git

def error(string="Error: "):
    return click.style(string, fg='red')


def warning(string="Warning: "):
    return click.style(string, fg='yellow')


def ok(string="OK: "):
    return click.style(string, fg='green')


def note(string):
    return string


def find_of_root():
    path = os.getcwd()
    while(path != os.path.abspath(os.sep)):
        if os.path.isdir(os.path.join(path, "addons")):
            if os.path.isdir(os.path.join(path, "apps")):
                if os.path.isdir(os.path.join(path, "libs")):
                    break
        path = os.path.abspath(os.path.join(path, os.pardir))

    if path == os.path.abspath(os.sep):
        return None

    return path


class Addon:
    def __init__(self, json):
        self.name = json['name']
        self.name_l = self.name.lower()
        self.description = json['description'] or ''
        self.description_l = self.description.lower()
        self.owner = json['owner']
        self.owner_l = self.owner.lower()
        self.category = json['category']
        self.category_l = self.category.lower()
        self.homepage = json['homepage']
        self.clone_url = json['clone_url']
        self.latest_commit = json['latest_commit']

    def print_short(self):
        print self.name, '-', self.description.encode('utf-8')

    def print_long(self):
        print self.name
        print '=' * len(self.name)
        print self.description.encode('utf-8')
        print
        print 'Owner     :', self.owner
        print 'Category  :', self.category
        print 'Homepage  :', self.homepage
        print 'Clone URL :', self.clone_url


class AddonsRegistry(object):
    def __init__(self, api_url):
        self.url = api_url

    def call_api(self, query):
        #print self.API_URL+query
        f = urllib2.urlopen(self.url+query)
        json = simplejson.load(f)
        return json

    def search(self, name):
        match = re.match("^(?:(?P<owner_name>\\w+)/)?(?P<addon_name>\\w+)", name, re.I)

        owner_name = match.group('owner_name')
        addon_name = match.group('addon_name')

        if owner_name:
            json = self.call_api("addon/"+owner_name+"/"+addon_name)
        else:
            json = self.call_api("addon/"+addon_name)
        if not json:
            return None
        return Addon(json)

    def get_version_from_name(self, string):
        match = re.match("^(?:(?P<owner_name>\\w+)/)?(?P<addon_name>\\w+)(?:@(?P<version>[\\w\.]+))?", string, re.I)
        return match.group('version')


class OFRoot(object):
    def __init__(self, path, url):
        self.path = path
        self.addon_registry = AddonsRegistry(url)

        if not self.path:
            raise click.UsageError('You don\'t seem to be in a openframeworks folder')
        if not os.path.exists(self.get_addon_path()):
            raise click.UsageError('You don\'t seem to be in a openframeworks folder')

    def get_addon_path(self):
        return os.path.join(self.path, 'addons')

    def get_installed_addons(self):
        addons = []
        for n in sorted(os.listdir(self.get_addon_path())):
            if os.path.isdir(os.path.join(self.get_addon_path(), n)):
                addons.append(n)
        return addons

    def remove_addon(self, addon):
        addonPath = os.path.join(self.get_addon_path(), addon.name)
        shutil.rmtree(addonPath)

    def install_addon(self, addon, version):
        addonPath = os.path.join(self.get_addon_path(), addon.name)
        if os.path.isdir(addonPath):
            # Folder already exists
            if not os.path.isdir(os.path.join(addonPath, '.git')):
                raise Exception('WARNING',
                                'ALREADY_INSTALLED_UNLINKED',
                                'Addon %s is already installed, but it\'s state is unknown.\nPlease reinstall with:\n' % addon.name + note('ofx reinstall %s' % addon.name))
            else:
                os.chdir(addonPath)
                currentSha = sh.git('rev-parse', 'HEAD').rstrip()
                remoteSha = addon.latest_commit['sha']

                if currentSha == remoteSha:
                    raise Exception('OK',
                                    'ALREADY_INSTALLED',
                                    'Addon %s is already installed and up to date' % addon.name)
                else:
                    raise Exception('WARNING',
                                    'ALREADY_INSTALLED_OUTDATED',
                                    'Addon %s is already installed but is not up to date. Consider running:\n' % addon.name + note("ofx update %s" % addon.name))
        else:
            print '>> Cloning %s' % addon.clone_url
            os.chdir(self.get_addon_path())
            git.clone(addon.clone_url)
            os.chdir(addonPath)

            sha = sh.git('rev-parse', 'HEAD').rstrip()
            if not sha:
                raise Exception('ERROR', 'CLONE_ERROR', "Something went wrong while cloning from "+addon.clone_url)
            else:
                print ok()+addon.name + ": Clone done"
                #print version
                if version is not None:
                    #Look for at tag with this name
                    tags = git.tag()
                    #print tags
                    if version in tags:
                        git.checkout(version)
                        print ok() + addon.name + ": %s checked out" % version
                    else:
                        raise Exception('ERROR',
                                        'UNKNOWN_VERSION',
                                        'No version named %s found for %s' % (version, addon.name))
                self.install_dependencies(addon)
            return True

    def install_dependencies(self, addon):
        #Read the addon_config.mk
        configPath = os.path.join(self.get_addon_path(), addon.name, 'addon_config.mk')
        if not os.path.exists(configPath):
            print warning()+addon.name+" is missing addon_config.mk file"
            return

        config = self.parse_addon_config_file(configPath)
        if config['dependecies']:
            print ">> Installing dependecies of "+addon.name+": "+', '.join(config['dependecies'])

            for dependency in config['dependecies']:
                #print dependency
                try:
                    addon = self.addon_registry.search(dependency)
                    version = self.addon_registry.get_version_from_name(dependency)
                    self.install_addon(addon, version)

                except Exception as exc:
                    if exc[0] == 'OK':
                        print ok()+exc[2]
                    elif exc[0] == 'ERROR':
                        print error()+exc[2]
                    elif exc[0] == 'WARNING':
                        print warning()+exc[2]
                    else:
                        print exc
                        pass

    def update_addon(self, addon):
        addonPath = os.path.join(self.get_addon_path(), addon.name)
        os.chdir(addonPath)
        git.checkout('master')
        git.pull()

    def parse_addon_config_file(self, path):
        f = open(path, 'r')
        dependecies = []
        for line in f:
            depsSearch = re.findall("ADDON_DEPENDENCIES\\s*\\+?=\\s*(?:([\\w/\.@]+)\\W)+", line, re.I)
            if depsSearch:
                for dep in depsSearch:
                    dependecies.append(dep)

        return {
            "dependecies": dependecies
        }


@click.group()
@click.option('--of-root', envvar='OF_ROOT', default=None, help="Overwrite path to of root")
@click.option('--of-api-url', envvar='OF_API_URL', default="http://ofxaddons.com/api/v2/", help="Overwrite url to ofxaddons.com api")
#@click.option('--debug/--no-debug', default=False,
#              envvar='REPO_DEBUG')
@click.pass_context
def cli(ctx, of_root, of_api_url):
    print of_api_url
    if not of_root:
        of_root = find_of_root()
    ctx.obj = OFRoot(of_root, of_api_url)


@cli.command()
@click.argument('name')
@click.pass_obj
def info(obj, name):
    """Returns info about an installed addon"""
    addon = obj.addon_registry.search(name)
    addonPath = os.path.join(obj.get_addon_path(), addon.name)
    if os.path.isdir(addonPath):
        addon.print_long()
    pass


@cli.command()
@click.argument('name')
@click.pass_obj
def install(obj, name):
    """Installs an addon"""

    #Find addon
    addon = obj.addon_registry.search(name)
    version = obj.addon_registry.get_version_from_name(name)
    if not addon:
        print error()+"No addon named %s found" % name
    else:
        try:
            obj.install_addon(addon, version)
        except Exception as exc:
            if exc[0] == 'OK':
                print ok()+exc[2]
            elif exc[0] == 'ERROR':
                print error()+exc[2]
            elif exc[0] == 'WARNING':
                print warning()+exc[2]
            else:
                print exc
                pass
    pass


@cli.command()
@click.argument('name')
@click.pass_obj
def reinstall(obj, name):
    """Reinstalls an addon"""

    #Find addon
    addon = obj.addon_registry.search(name)
    version = obj.addon_registry.get_version_from_name(name)
    if not addon:
        print error()+"No addon named %s found" % name
        return

    if not os.path.isdir(os.path.join(obj.get_addon_path(), addon.name)):
        print error()+'Addon "%s" not installed.' % name
        return

    obj.remove_addon(addon)

    try:
        obj.install_addon(addon, version)
    except Exception as exc:
        if exc[0] == 'OK':
            print ok()+exc[2]
        elif exc[0] == 'ERROR':
            print error()+exc[2]
        elif exc[0] == 'WARNING':
            print warning()+exc[2]
        else:
            print exc
            pass

    pass


@cli.command()
@click.argument('name')
@click.pass_obj
def update(obj, name):
    """Update an addon"""

    #Find addon
    addon = obj.addon_registry.search(name)
    if not addon:
        print error()+"No addon named %s found" % name
        return

    if not os.path.isdir(os.path.join(obj.get_addon_path(), addon.name)):
        print error()+'Addon "%s" not installed.' % name
        return

    obj.update_addon(addon)
    pass


@cli.command()
@click.argument('name')
@click.pass_obj
def search(obj, name):
    """Search for an addon"""
    addon = obj.addon_registry.search(name)
    if not addon:
        print error()+"No addon named %s found" % name
    else:
        print addon.print_long()
    pass


@cli.command()
@click.pass_obj
def list(obj):
    """List installed addons"""
    addons = obj.get_installed_addons()
    for addon in addons:
        print addon
    pass
