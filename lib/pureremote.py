#!/usr/bin/env python3

"""
Supporting logic for the pureremote command
"""

from lib import sessions
from lib import display


SESSION_TITLES = [
    'Remote',
    'Address',
]


def add_remote(name, address, token):
    """
    Add a remote array configuration
    """

    name = name
    config = {
        'address': address,
        'api_token': token,
    }

    try:
        sessions.add_session(name, config)
    except AssertionError as e:
        pass

    display.print_display(SESSION_TITLES, [{
        'Remote': name,
        'Address': address,
    }])


def setattr_remote(name, address, token):
    """
    Modify a remote array configuration
    """


    try:
        info = sessions.list_sessions()
    except AssertionError as e:
        pass

    config = info[name]
    for attr in ('address', 'api_token'):

        config['api_token'] = token
        config['address'] = address

    try:
        sessions.add_session(name, config, overwrite=True)
    except AssertionError as e:
        pass

    display.print_display(SESSION_TITLES, [{
        'Remote': name,
        'Address': config['address'],
    }])


def remove_remote(name):
    """
    Remove a remote array configuration
    """

    try:
        sessions.remove_session(name)
    except AssertionError as e:
        pass

    display.print_display(['Remote'], [{
        'Remote': name,
    }])

def list_remotes(args):
    """
    List all remote array configurations
    """

    try:
        info = sessions.list_sessions()
    except AssertionError as e:
        pass

    data = []
    for name in sorted(info.keys()):
        data.append({
            'Remote': name,
            'Address': info[name]['address']
        })

    display.print_display(SESSION_TITLES, data, csv=args.csv, show_titles=args.show_titles)


def test_remotes(args):
    """
    Test all remote array configurations
    """

    try:
        info = sessions.list_sessions()
    except AssertionError as e:
        args._parser.error(e)

    # get our list of names to check
    if hasattr(args, 'names') and len(args.names) > 0:
        names = args.names
    else:
        # default to all configurations
        names = sorted(info.keys())

    data = []
    for name in names:
        array = {}
        address = None
        details = 'Successfully connected to array!'
        if name not in info:
            details = 'Remote array "{}" has not been configured'.format(name)
        else:
            address = info[name]['address']
            try:
                fb = rest_client.fb_init_session(info[name])
                array = rest_client.fb_get_array_info(fb)
            except Exception as e:
                details = 'Could not connect to remote array'

        data.append({
            'Remote': name,
            'Address': address,
            'Array Name': array.get('name'),
            'Array Version': array.get('version'),
            'Details': details,
        })
    titles = [
        'Remote',
        'Address',
        'Array Name',
        'Array Version',
        'Details',
    ]
    display.print_display(titles, data)
