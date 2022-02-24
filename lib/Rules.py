import re
import json
from lib.Rule import *
from lib.exceptions import *
from lib.scanrules import ScanRules


class Rules():

    def __init__(self, rules_text, logger):
        self.default_options = 'ro,root_squash,no_all_squash,no_fileid_32bit'

        self.rules_list = []
        self.targets_list = []
        self.logger = logger

        rule_items = rules_text.split(' ')

        # We have an empty rules field for this share... nothing to parse.
        if len(rules_text) == 0:
            return

        rule_position = 1
        for rule_item in rule_items:

            # Is rule_item options?
            if re.match(r'-(.+?)$', rule_item):
                iMatch = re.match(r'-(.+?)$', rule_item)
                tmpRule = Rule(iMatch.group(1), False)
                self.rules_list.append(tmpRule)

            # is it an IP with specific options
            elif re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b\((.+?)\)', rule_item):
                iMatch = re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b\((.+?)\)', rule_item)
                tmpRule = Rule(iMatch.group(2), True)
                tmpRule.add_net_entity(NetEntity(iMatch.group(1), False, rule_position))
                self.rules_list.append(tmpRule)
                rule_position += 1

            # is it a Network with specific options
            elif re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\b\((.+?)\)', rule_item):
                iMatch = re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\b\((.+?)\)', rule_item)
                tmpRule = Rule(iMatch.group(2), True)
                tmpRule.add_net_entity(NetEntity(iMatch.group(1), True, rule_position))
                rule_position += 1
                self.rules_list.append(tmpRule)

            # matches option like:  *(rw, no_root_squash)
            elif re.match(r'\*\((.+)\)$', rule_item):
                iMatch = re.match(r'\*\((.+)\)$', rule_item)
                tmpRule = Rule(iMatch.group(1), True)
                tmpRule.add_net_entity(NetEntity('0.0.0.0/0', True, rule_position))
                rule_position += 1
                self.rules_list.append(tmpRule)

            elif rule_item == '*':
                tmpRule.add_net_entity(NetEntity('0.0.0.0/0', True, rule_position))
                rule_position += 1

            # is it a network
            elif re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\b', rule_item):
                iMatch = re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\b', rule_item)
                tmpRule.add_net_entity(NetEntity(iMatch.group(1), True, rule_position))
                rule_position += 1

            # is it an IP address
            elif re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', rule_item):
                iMatch = re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', rule_item)
                tmpRule.add_net_entity(NetEntity(iMatch.group(1), False, rule_position))
                rule_position += 1

            else:
                raise RuleParseException(rule_item, 'Could not scan in object.')

    def delete_empty_rules(self):
        for i, ro in enumerate(self.rules_list):
            if len(ro.net_objects) == 0:
                try:
                    # explicitly set applied options of next rule so we don't mess up inherited
                    # properties of subsequent rules.
                    self.refactor_paren_type_rule_opts(i)
                    del self.rules_list[i]
                except:
                    # There is no following rule... if we have failed here we can skip.
                    pass

    def does_target_already_exist(self, target_address):
        for ri, ro in enumerate(self.rules_list):
            for i, o in enumerate(ro.net_objects):
                if target_address == o.address:
                    return True
        return False

    def remove_target(self, target_address):
        for ri, ro in enumerate(self.rules_list):
            for i, o in enumerate(ro.net_objects):
                if target_address == o.address:
                    del ro.net_objects[i]

            # If the rule is now empty after deleting an NetEntity then you have to make sure
            # you explicitly set the options for the next rule if one exists.  If not, the except is hit
            # and we dont' need to do anything since there is not next rule.
            if len(ro.net_objects) == 0:
                try:
                    self.refactor_paren_type_rule_opts(i)
                except:
                    pass
                del self.rules_list[ri]

    def insert_network_targets(self, force_target=False):

        for target in self.targets:
            if target.isnetwork:
                self.insert_network_target(target, force_target)
        return True

    def insert_ip_targets(self, force_target=False):

        for target in self.targets:
            if not target.isnetwork:
                self.insert_ip_target(target, force_target)

    def is_ip_inrange_of_rule(self, ip_target, rule):
        for netObj in rule.net_objects:
            if netObj.isnetwork:
                if netObj.is_parent_to_ip(ip_target):
                    return True
        return False

    def ip_in_range_of_network_in_any_rule(self, ip_target):
        for rule in self.rules_list:
            if self.options_equiv(rule.effective_options):
                if self.is_ip_inrange_of_rule(ip_target, rule):
                    return True
        return False

    def ip_range_check(self, ip_target):
        inserted = False
        for rule in self.rules_list:

            if self.is_ip_inrange_of_rule(ip_target, rule):
                if self.options_equiv(rule.effective_options):
                    inserted = True
        return inserted

    def refactor_paren_type_rule_opts(self, rule_pos):
        optset = set()
        for i, rule in enumerate(self.rules_list):
            for option in rule.applied_options.split(','):
                optset.add(option)

        optlist = list(optset)

        if 'rw' in optlist:
            optlist.append('ro')
        if 'ro' in optlist:
            optlist.append('rw')
        if 'root_squash' in optlist:
            optlist.append('no_root_squash')
        if 'no_root_squas' in optlist:
            optlist.append('root_squash')
        if 'fileid_32bit' in optlist:
            optlist.append('no_fileid_32bit')
        if 'no_fileid_32bit' in optlist:
            optlist.append('fileid_32bit')
        if 'all_squash' in optlist:
            optlist.append('no_all_squash')
        if 'no_all_squash' in optlist:
            optlist.append('all_squash')

        start = False
        for i, rule in enumerate(self.rules_list):
            if start:
                list_to_apply = []
                for eff_opt in rule.effective_options.split(','):
                    if eff_opt in optlist:
                        list_to_apply.append(eff_opt)
                rule.set_applied_options(','.join(list_to_apply))
            if i == rule_pos:
                start = True

    def insert_ip_target(self, ip_target, force_target):

        if self.does_target_already_exist(ip_target.address):
            if not force_target:
                raise TargetFoundWarning(ip_target.address)

        # If network target is already exported remove it before re-inserting it. It may be exported incorrectly.
        self.remove_target(ip_target.address)

        # First time ip is in range of network. do options match?  If they do and
        # there is a network in range in this rule then, don't go further.
        if self.ip_range_check(ip_target):
            if not force_target:
                raise TargetNetworkFoundForIPWarning(ip_target.address)

        # Check for rule that is not a paren "()" rule type with equiv options
        for i, rule in enumerate(self.rules_list):

            inserted = False
            ## First try to find any rule that isn't in "()" with equiv rules to insert.
            if self.options_equiv(rule.effective_options) and not rule.is_paren_rule:

                # Is there an IP network in this rule that matches the range of this IP address?
                if self.is_ip_inrange_of_rule(ip_target, rule):

                    # Warn user that we're not adding unless --force_option used
                    if not force_target:
                        raise TargetNetworkFoundForIPWarning(ip_target.address)
                    else:

                        rule.prepend_net_entity(ip_target)
                        inserted = True

                        # Have to refactor everything based on inheritance differences between rule types
                        if len(rule.net_objects) == 1 and rule.is_paren_rule:
                            self.refactor_paren_type_rule_opts(i)
                else:
                    if len(rule.net_objects) > 1 or not rule.is_paren_rule:
                        rule.prepend_net_entity(ip_target)
                        inserted = True
                break

        # Next insert into first place rules match since we couldn't find a rule already created that isn't in ()
        if not inserted:
            for i, rule in enumerate(self.rules_list):
                # Options ok to insert ip
                if self.options_equiv(rule.effective_options):

                    # Is there an IP network in this rule that matches the range of this IP address?
                    if self.is_ip_inrange_of_rule(ip_target, rule):

                        # Warn user that we're not adding unless --force_option used
                        if not force_target:
                            raise TargetNetworkFoundForIPWarning(ip_target.address)
                        else:

                            rule.prepend_net_entity(ip_target)
                            inserted = True

                            # Have to refactor everything based on inheritance differences between rule types
                            if len(rule.net_objects) == 1 and rule.is_paren_rule:
                                self.refactor_paren_type_rule_opts(i)
                    else:
                        if len(rule.net_objects) == 1 and rule.is_paren_rule:
                            # Have to change rule type so have to refactor all rules to account for new type.
                            self.refactor_paren_type_rule_opts(i)
                        rule.prepend_net_entity(ip_target)
                        inserted = True
                    break

        # Need to add a rule as last resort.
        if not inserted:
            # Use options listed for this script run to add new rule.
            tmpRule = Rule(self.options, False)
            tmpRule.add_net_entity(ip_target)
            self.rules_list.append(tmpRule)
            # We added a new Rule, calculate effective options for new rule.
            self.factor_options()
            inserted = True

        # We added a target so, refactor NetEntity positions.
        self.refactor_rule_positions()

    def get_insert_rules(self, ins_target):
        insert_rules = []
        for rule in self.rules_list:

            target = ins_target
            for netEnt in rule.return_entities():

                if netEnt.isnetwork and target.isnetwork:
                    tgt_is_parent = target.is_parent_to(netEnt)
                    if tgt_is_parent['result_successful']:
                        # you have to insert the rule after rule_position
                        insert_rules.append({'target': target.address, 'action': 'after',
                                             'position': tgt_is_parent['rule_position']})

                    netobj_is_parent = netEnt.is_parent_to(target)

                    if netobj_is_parent['result_successful']:
                        # you have to insert the rule before rule_position
                        insert_rules.append({'target': target.address, 'action': 'before',
                                             'position': netobj_is_parent['orule_position']})

        return insert_rules

    def gen_before_after_rules(self, target, insert_rules):
        insert_after = 0
        insert_before = 1000
        for insert_rule in insert_rules:
            if insert_rule['target'] == target.address:
                if insert_rule['action'] == 'before':
                    insert_before = min(insert_before, insert_rule['position'])
                if insert_rule['action'] == 'after':
                    insert_after = max(insert_after, insert_rule['position'])
        return insert_before, insert_after

    def insert_network_target(self, ins_target, force_target=False):
        """
        This is where the smart network insert happens.  We build a set of rules so that we know which order is needed
        to successfully insert a target into a set of rules.  Each NetEntity has a rule_position which is the number
        that it appears in the rule list.  We calculate here by checking if a network being added is part of any other
        network's range.  If it is then, we decide if the network that we're inserting belongs before or after the other
        already added network(s)... we build out a simple list of two vars "insert_before" and "insert_after" and if
        insert_after > insert_before then, there is a conflict with the rule already.... otherwise, do the insert as
        long as we can either match or create a new rule for the new target and re-factor the options while not
        changing the subsequent rules.

        :param ins_target:
        :return:
        """
        if self.does_target_already_exist(ins_target.address):
            if not force_target:
                raise TargetFoundWarning(ins_target.address)

        # First remove the address if it exists in the rules.  It may already be exported with incorrect options.
        self.remove_target(ins_target.address)
        self.factor_options()
        self.refactor_rule_positions()

        # Generate a list of rules we can use to create "insert_before" and "insert_after" to know the positions
        # that a network rule can be inserted.
        insert_rules = self.get_insert_rules(ins_target)

        # We have insert rules for networks that may live inside other networks now.
        # insert_rules
        '''
        [
            {
                "target": "10.10.10.0/24",
                "action": "after",
                "position": 1
            },
            {
                "target": "10.10.10.0/24",
                "action": "before",
                "position": 2
            }
        ]
        '''

        # Look through insert rules and find min and max for before and after inserts in the case
        # that there are more than one of each.
        insert_before, insert_after = self.gen_before_after_rules(ins_target, insert_rules)

        # Everything is calculated.  We need to try to start adding the target.
        if insert_before < insert_after:
            raise NetworkRangeConflict(ins_target.address)

        # There is no network overlapping. First see if you can insert into existing rules.  If so, insert it,
        # If not append it as a new rule at the end of the rules.
        if insert_after == 0 and insert_before == 1000:
            inserted = False
            for rule in reversed(self.rules_list):

                # Rules match, we can append the NetEntity to this rule.
                if self.options_equiv(rule.return_applied_options()):
                    rule.add_net_entity(ins_target)
                    inserted = True
                    break

            # Append a new rule to the bottom
            if not inserted:
                tmpRule = Rule(self.options, False)
                tmpRule.add_net_entity(ins_target)
                self.rules_list.append(tmpRule)
                self.factor_options()
                self.refactor_rule_positions()
            return

        # There is some sort of network overlapping.
        inserted = False
        tgt_found_not_inserting = False

        # Scan rules and find all possible insertion points.
        scanRules = ScanRules(self.rules_list, self.options, insert_before, insert_after)
        scanRules.scan()

        # return the last place in the ruleset that you can insert a network rule.... order matters.
        rule = scanRules.return_insert_options().pop()
        # print(json.dumps(rule, indent=4))
        '''
        rule
        {
            "rule": 1,
            "rule_position": 1,
            "options_match": true,
            "before": 4,
            "after": 2,
            "position": 4
        }
        '''

        # Options match... should be able to insert into existing rule here.
        if rule['options_match']:

            # insert after this target
            if rule['position'] == rule['after'] and rule['position'] < rule['before']:
                self.rules_list[rule['rule']].net_objects.insert(rule['rule_position'] + 1, ins_target)
                inserted = True

            # insert before this target
            # options are the same and should insert before so, this is a redundant rule.
            elif rule['position'] == rule['before'] and rule['position'] >= rule['after']:
                if force_target:
                    self.rules_list[rule['rule']].net_objects.insert(rule['rule_position'], ins_target)
                    inserted = True
                else:
                    tgt_found_not_inserting = True

            elif rule['position'] > rule['after'] and rule['position'] < rule['before']:
                self.rules_list[rule['rule']].net_objects.insert(rule['rule_position'], ins_target)
                inserted = True

        # options don't match... insert new rule if possible.
        else:
            # Can not insert inside same rule because options don't match, generate error
            if rule['position'] == insert_before and self.rules_list[rule['rule']].min_rule_position() <= insert_after:
                self.logger.error("Can not insert into this rule. There is an error in this rule.")
                self.logger.error("Two network ranges are in this rule and can not insert into rule because export \
                                  options do not match.")

            # Can not insert inside same rule because options don't match, generate error
            elif rule['position'] == insert_after and self.rules_list[
                rule['rule']].max_rule_position() >= insert_before:
                self.logger.error("Can not insert into this rule. There is an error in this rule.")
                self.logger.error("Two network ranges are in this rule and can not insert into rule because export \
                                  options do not match.")

            # insert new rule before this one
            elif rule['position'] == insert_before and self.rules_list[rule['rule']].min_rule_position() > insert_after:
                tmpRule = Rule(self.options, False)
                tmpRule.add_net_entity(ins_target)
                self.rules_list.insert(rule['rule'], tmpRule)
                self.refactor_paren_type_rule_opts(rule['rule'])
                inserted = True

            # insert new rule after this one
            elif rule['position'] == insert_after and self.rules_list[rule['rule']].max_rule_position() < insert_before:
                tmpRule = Rule(self.options, False)
                tmpRule.add_net_entity(ins_target)
                self.refactor_paren_type_rule_opts(rule['rule'])
                self.rules_list.insert(rule['rule'] + 1, tmpRule)
                inserted = True

            elif rule['position'] > insert_after and rule['position'] <= insert_before:
                tmpRule = Rule(self.options, False)
                tmpRule.add_net_entity(ins_target)
                self.rules_list.insert(rule['rule'], tmpRule)
                self.refactor_paren_type_rule_opts(rule['rule'])
                inserted = True

        self.refactor_rule_positions()
        self.factor_options()

        if not inserted and not tgt_found_not_inserting:
            raise TargetNotInserted(ins_target.address)

        if tgt_found_not_inserting:
            raise TargetFoundNotForcingWarning(ins_target.address)

    def options_equiv(self, options):

        tgt_options = self.options.split(',')
        obj_options = options.split(',')

        for opt in tgt_options:
            if opt not in obj_options:
                if 'anon' not in opt:
                    return False
        return True

    def write_rules(self):
        ret_string = ''
        for rule in self.rules_list:
            x = rule.return_entities()
            if len(x) > 1 or not rule.is_paren_rule:
                ret_string = ret_string + ' -' + rule.return_applied_options()
                for each in x:
                    ret_string = ret_string + ' ' + each.address
            else:
                ret_string = ret_string + ' ' + x[0].address + '(' + rule.return_applied_options() + ')'

        # When writing rules, replace the 0.0.0.0/0 with a '*' when calculating rules use the other format.
        if '0.0.0.0/0' in ret_string:
            ret_string = ret_string.replace('0.0.0.0/0', '*')

        return ret_string

    def refactor_rule_positions(self):
        count = 1
        for rule in self.rules_list:
            for netObject in rule.return_entities():
                netObject.set_rule_position(count)
                count += 1

    def define_targets_options(self, targets, options):
        self.targets = []
        self.options = options

        for target in targets:
            if re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\b', target):
                iMatch = re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\b', target)
                self.targets.append(NetEntity(target, True, 0))
            elif re.match(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', target):
                self.targets.append(NetEntity(target, False, 0))
            elif target == '*':
                self.targets.append(NetEntity('0.0.0.0/0', True, 0))
            else:
                raise DefineTargetException(target)

    def add_options(self, options):
        self.options = options

    def factor_options(self):
        prev_options = self.default_options
        previous_hyphen_rule_opts = self.default_options
        for rule in self.rules_list:

            effective_opts = self.calculate_effective_options(previous_hyphen_rule_opts, rule.applied_options)
            rule.apply_effective_options(previous_hyphen_rule_opts, effective_opts)

            if not rule.is_paren_rule:
                previous_hyphen_rule_opts = effective_opts

    def calculate_effective_options(self, prev_options, applied_options):
        prev_options = prev_options.split(',')
        applied_options = applied_options.split(',')
        effective_options = prev_options

        if 'ro' in applied_options and 'rw' in prev_options:
            effective_options.remove('rw')
            effective_options.append('ro')
        if 'rw' in applied_options and 'ro' in prev_options:
            effective_options.remove('ro')
            effective_options.append('rw')
        if 'root_squash' in applied_options and 'no_root_squash' in prev_options:
            effective_options.remove('no_root_squash')
            effective_options.append('root_squash')
        if 'no_root_squash' in applied_options and 'root_squash' in prev_options:
            effective_options.remove('root_squash')
            effective_options.append('no_root_squash')
        if 'fileid_32bit' in applied_options and 'no_fileid_32bit' in prev_options:
            effective_options.remove('no_fileid_32bit')
            effective_options.append('fileid_32bit')
        if 'no_fileid_32bit' in applied_options and 'fileid_32bit' in prev_options:
            effective_options.remove('fileid_32bit')
            effective_options.append('no_fileid_32bit')
        if 'all_squash' in applied_options and 'no_all_squash' in prev_options:
            effective_options.remove('no_all_squash')
            effective_options.append('all_squash')
        if 'no_all_squash' in applied_options and 'all_squash' in prev_options:
            effective_options.remove('all_squash')
            effective_options.append('no_all_squash')
        effective_options = ','.join(effective_options)
        return effective_options

    def return_rules(self):
        return self.rules_list
