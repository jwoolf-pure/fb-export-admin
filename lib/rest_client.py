#!/usr/bin/env python3

"""
Helper functions to help interface with the purity_fb package
"""

import urllib3
from lib.exceptions import *

from purity_fb import (
    PurityFb,
    rest,
    FileSystem,
    NfsRule,
)

# TODO: explain this
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TODO: add logging


def fb_init_session(config):
    fb = PurityFb(config['address'])
    fb.disable_verify_ssl()
    try:
        fb.login(config['api_token'])
        return fb
    except rest.ApiException as e:
        raise FBInitException(e)


def fb_get_array_info(fb):
    arrays = fb.arrays.list_arrays().to_dict()
    return arrays.get('items')[0]


def fb_get_version(fb):
    return fb_get_array_info(fb).get('version')


def fb_get_filesystems(fb, names=None):
    try:
        # list our requested file systems (or all if we're not given a list of names)
        if names is None:
            res = fb.file_systems.list_file_systems().to_dict()
        else:
            res = fb.file_systems.list_file_systems(names=names).to_dict()

        # return the list of filesystems
        if res is None:
            return []
        else:
            return res.get('items')
    except rest.ApiException as e:
        raise FilesystemGetException(e)


def extract_export_rules(filesystems):
    return {
        fs.get('name'): fs.get('nfs').get('rules')
        for fs in filesystems
    }


def apply_new_rule(fb, name, rules):

    new_attr = FileSystem(nfs=NfsRule(rules=rules))
    try:
        ret = fb.file_systems.update_file_systems(name=name, attributes=new_attr).to_dict()
    except rest.ApiException as e:
        raise ApplyRulesException(e)
