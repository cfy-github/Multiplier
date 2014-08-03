#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import os

addon_path = 'B:/Jogos/steam/steamapps/common/dota 2 beta/dota/addons/'
addon_name = 'CSP'
dev_path = u'D:/Programação/dota2mods/Multiplier'
npcs_to_copy = ['npc_abilities_custom.txt', 'npc_abilities_override.txt']
languages_to_copy = ['addon_english.txt']

def copyFile(src, dest):
    try:
        shutil.copy(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('Error: %s' % e)
    # eg. source or destination doesn't exist
    except IOError as e:
        print('Error: %s' % e.strerror)


def updateAddons():
    print '==== Updating Addon Folder ===='
    if os.path.exists(addon_path + addon_name):
        print 'Removing dir: ' + addon_path + addon_name
        shutil.rmtree(addon_path)
        os.makedirs(addon_path)
    for f in npcs_to_copy:
        print 'Copying file: ' + f
        copyFile(dev_path + '/tools/generator/' + f, dev_path + '/' + addon_name + '/scripts/npc/' + f)
    for f in languages_to_copy:
        print 'Copying file: ' + f
        copyFile(dev_path + '/tools/generator/' + f, dev_path + '/' + addon_name + '/resource/' + f)
    print 'Copying addon to folder: ' + addon_path + addon_name
    shutil.copytree(dev_path + '/CSP', addon_path + addon_name)

if __name__ == "__main__":
    updateAddons()
