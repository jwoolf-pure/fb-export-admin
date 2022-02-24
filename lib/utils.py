import logging
import yaml
import os
import argparse
from argparse import RawTextHelpFormatter
import json
import sys
from lib import sessions
from lib.export import Exports
from lib.exportrules import ExportRules
from lib.rest_client import fb_init_session, fb_get_filesystems
from lib.exceptions import *
from lib.rest_client import *


def setup_logging():
    console_error_level = 'DEBUG'
    logger = logging.getLogger('pure_export')
    logger.setLevel(console_error_level)

    ch = logging.StreamHandler()
    ch.setLevel(console_error_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s ==> %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def validate_remote(remotes):
    for remote in remotes.split(','):
        config = sessions.list_sessions([remote])[remote]
        fb = fb_init_session(config)
        filesystems = fb_get_filesystems(fb, names=['JWoolf-NFS-Test1', 'test'])
        print(json.dumps(filesystems, indent=4))


def read_array_shares(remotes, names=None):
    retObj = {}
    for remote in remotes.split(','):
        retObj[remote] = []
        config = sessions.list_sessions([remote])[remote]
        fb = fb_init_session(config)
        filesystems = fb_get_filesystems(fb, names)
        for filesystem in filesystems:
            retObj[remote].append({'name': filesystem['name'], 'rules': filesystem['nfs']['rules']})
    return retObj


def get_group_shares(group):
    try:
        with open('settings.yaml', 'r') as f:
            fshares = yaml.load(f, Loader=yaml.FullLoader)
        try:
            group = fshares['SHARES'][group]
        except:
            raise SettingsGroupException(group)
    except:
        raise YamlReadException(group)

    retObj = {}
    for remote in group:
        retObj[remote] = []
        config = sessions.list_sessions([remote])[remote]
        fb = fb_init_session(config)
        filesystems = fb_get_filesystems(fb, group[remote])
        for filesystem in filesystems:
            retObj[remote].append({'name': filesystem['name'], 'rules': filesystem['nfs']['rules']})
    return retObj


def determine_run_mode_and_execute():
    parser = argparse.ArgumentParser(prog='pure_exports',
                                     usage='pure_exports [options]',
                                     description="""
                                     
  Example Runmodes:

  Print rules for array1 to stdout                                     
  pure_exportadm --remotes <array1> --printonly

  Test/Apply rules and ONLY print the results for all shares
  pure_exportadm --file_shares all --operation add -rules rw,root_squash --targets 10.10.0.0/16,10.10.10.10 --printonly --remotes <array1>,<array2>

  Apply rules
  pure_exportadm --file_shares share1,share2,share3 --operation add -rules rw,root_squash --targets 10.10.0.0/16,10.10.10.10 --remotes <array1>,<array2>

  Test/Apply rules from a file and only print result
  pure_exportadm --operation add --rules rw,no_root_squash --targets 10.10.10.0/24,10.20.30.40 --load_from_file <file.json>  --printonly

  Affect the changes on the array without --printonly
  pure_exportadm --operation add --rules rw,no_root_squash --targets 10.10.10.0/24,10.20.30.40 --load_from_file <file.json> 

  Load Affect changes that are in a saved file
  pure_exportadm --load_from_file <file.json> --operation add_file

  Add new FlashBlade credentials
  pure_exportadm --add_remote <name> --remote_address <ip address> --api_token <token>
  
  Read from file and write to array
  python ./pure_exportadm.py --load_from_file blah2 --operation add_file

  Add from a file giving add arguments and only printing result not executing
  python ./pure_exportadm.py --load_from_file nfsrules.json --rules rw,no_root_squash --targets 10.20.30.40,10.99.10.0/24 --operation add --printonly

                                     """, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--remotes', help='Name of storage array(s) comma delimited e.g. array1,array2', required=False)
    parser.add_argument('--file_shares', help='Name of shares to operate on or "all" for all file shares.',
                        required=False)
    parser.add_argument('--group_shares', help='Name of shares to operate on or "all" for all file shares.',
                        required=False)
    parser.add_argument('--operation', help='Operation to perform. "add" or "remove"', required=False)
    parser.add_argument('--rules', help='Rules for shares to add. Comma delimited list e.g. rw,root_squash',
                        required=False)
    parser.add_argument('--targets', help='Target addresses or networks to add. Comma delimited list.')
    parser.add_argument('--printonly', help='Only print output', action='store_true')
    parser.add_argument('--force_target', help='Only print output', action='store_true')
    parser.add_argument('--load_from_file', help='Read rules from file and apply to the remote(s)', required=False)
    parser.add_argument('--add_remote', help='Remote to add')
    parser.add_argument('--remote_address', help='IP address of the remote to add.')
    parser.add_argument('--api_token', help='API token of array to add.')
    parser.add_argument('--version', help='Get Version.', action='store_true')
    args = parser.parse_args()

    logger = setup_logging()

    VERSION = 1.6

    if args.version:
        print("pure_exportadm: Version: {}".format(VERSION))
        sys.exit(0)

    ###
    ### Add operation
    ###
    if args.operation == 'add':

        if not args.group_shares and not args.targets and not args.load_from_file:
            parser.print_help()
            sys.exit(1)

        if not args.remotes and not args.group_shares and not args.load_from_file:
            parser.print_help()
            sys.exit(1)

        if not args.rules or not args.targets:
            parser.print_help()
            sys.exit(1)

        if args.group_shares:
            try:
                shares = get_group_shares(args.group_shares)
            except YamlReadException as e:
                logger.critical(e)
            except SettingsGroupException as e:
                logger.critical(e)

        if args.file_shares == 'all':
            names = None
            shares = read_array_shares(args.remotes, names)
        else:
            if args.file_shares:
                names = args.file_shares.split(',')
                shares = read_array_shares(args.remotes, names)

        if args.load_from_file:
            try:
                f = open(args.load_from_file, 'r')
            except FileNotFoundError:
                logger.critical("Can load open file " + args.load_from_file)
                sys.exit(1)
            except:
                logger.critical("Can load open file " + args.load_from_file)
                sys.exit(1)

            shares = eval(f.read())
            f.close()
        try:
            shares
        except NameError:
            raise SharesNotDefined()

        retObj = {}
        for remote in shares:
            eRules = ExportRules(remote, logger)
            for fshare in shares[remote]:
                fshare['rules'] = fshare['rules'].lstrip(' ').rstrip(' ')
                eRules.add_export(fshare['name'], fshare['rules'])
            eRules.define_targets(args.targets, args.rules)
            eRules.apply_rules_targets(args.force_target)
            retObj[remote] = eRules.write_rules()

        if args.printonly:
            print(json.dumps(retObj, indent=4))
            sys.exit()
        else:
            print(json.dumps(retObj, indent=4))
            logger.info("Adding targets ...")
            for array in retObj:
                config = sessions.list_sessions([array])[array]
                try:
                    fb = fb_init_session(config)
                except FBInitException as e:
                    logger.critical("Did not establish session with " + array)
                    logger.critical(e)
                    sys.exit(1)
                for share in retObj[array]:
                    share['rules'] = share['rules'].lstrip(' ').rstrip(' ')
                    try:
                        apply_new_rule(fb, share['name'], share['rules'])
                    except ApplyRulesException as e:
                        logger.critical("Did not apply rule for " + array)
                        logger.critical(e)
                        sys.exit(1)
        logger.info("Complete.")
        sys.exit()

    ###
    ### Read in array shares and print results
    ###
    if not args.operation and args.printonly:

        if not args.group_shares and not args.load_from_file and not args.remotes:
            parser.print_help()
            sys.exit(1)

        if args.load_from_file:
            parser.print_help()
            sys.exit(1)

        if args.group_shares:
            try:
                shares = get_group_shares(args.group_shares)
                print(json.dumps(shares, indent=4))
                sys.exit()

            except YamlReadException as e:
                logger.critical(e)
            except SettingsGroupException as e:
                logger.critical(e)

        names = None
        if args.file_shares:
            names = args.file_shares.split(',')
        shares = read_array_shares(args.remotes, names)
        print(json.dumps(shares, indent=4))
        sys.exit()

    ###
    ### Apply rules from a saved file.
    ###
    if args.operation == 'add_file' and args.load_from_file and not args.printonly:

        if args.load_from_file:
            try:
                f = open(args.load_from_file, 'r')
            except:
                logger.critical("Can load open file " + args.load_from_file)
                sys.exit(1)
            shares = eval(f.read())
            f.close()

        logger.info("Adding targets ...")
        for array in shares:
            config = sessions.list_sessions([array])[array]
            try:
                fb = fb_init_session(config)
            except FBInitException as e:
                logger.critical("Did not establish session with " + array)
                logger.critical(e)
                sys.exit(1)

            for remote in shares:
                for share in shares[remote]:
                    share['rules'] = share['rules'].lstrip(' ').rstrip(' ')
                    try:
                        apply_new_rule(fb, share['name'], share['rules'])
                    except ApplyRulesException as e:
                        logger.critical("Did not apply rule for " + array)
                        logger.critical(e)
                        sys.exit(1)
        logger.info("Complete.")
        sys.exit()

    ###
    ### Delete targets operation
    ###
    if args.operation == 'delete':

        if not args.group_shares and not args.targets and not args.load_from_file:
            parser.print_help()
            sys.exit(1)

        if not args.remotes and not args.group_shares and not args.load_from_file:
            parser.print_help()
            sys.exit(1)

        if not args.targets:
            parser.print_help()
            sys.exit(1)

        if args.group_shares:
            try:
                shares = get_group_shares(args.group_shares)
            except YamlReadException as e:
                logger.critical(e)
            except SettingsGroupException as e:
                logger.critical(e)

        if args.file_shares == 'all':
            names = None
            shares = read_array_shares(args.remotes, names)
        else:
            if args.file_shares:
                names = args.file_shares.split(',')
                shares = read_array_shares(args.remotes, names)

        if args.load_from_file:
            try:
                f = open(args.load_from_file, 'r')
            except:
                logger.critical("Can load open file " + args.load_from_file)
                sys.exit(1)
            shares = eval(f.read())
            f.close()

        try:
            shares
        except NameError:
            raise SharesNotDefined()
        retObj = {}
        for remote in shares:
            eRules = ExportRules(remote, logger)
            for fshare in shares[remote]:
                fshare['rules'] = fshare['rules'].lstrip(' ').rstrip(' ')
                eRules.add_export(fshare['name'], fshare['rules'])
            eRules.define_targets(args.targets, '')
            eRules.delete_targets()
            retObj[remote] = eRules.write_rules()

        if args.printonly:
            print(json.dumps(retObj, indent=4))
            sys.exit()
        else:
            print(json.dumps(retObj, indent=4))
            logger.info("Deleting targets ...")
            for array in retObj:
                config = sessions.list_sessions([array])[array]
                try:
                    fb = fb_init_session(config)
                except FBInitException as e:
                    logger.critical("Did not establish session with " + array)
                    logger.critical(e)

                for share in retObj[array]:
                    share['rules'] = share['rules'].lstrip(' ').rstrip(' ')
                    try:
                        apply_new_rule(fb, share['name'], share['rules'])
                    except ApplyRulesException as e:
                        logger.critical("Did not apply rule for " + array)
                        logger.critical(e)
                        sys.exit(1)
        logger.info("Complete.")
        sys.exit()

    ###
    ### Add remote.
    ###
    if args.add_remote and args.remote_address and args.api_token:
        add_remote(args.add_remote, args.remote_address, args.api_token)


def main():
    determine_run_mode_and_execute()
