import re
from lib.exceptions import *
from lib.Rules import Rules
import sys


class Exports():

    def __init__(self, share, line, logger):

        self.rules_line = line
        self.logger = logger

        self.volume = share
        self.rules_text = line
        self.rules_text = re.sub(' +', ' ', self.rules_text)

        try:
            items = self.rules_text.split(' ')

        except:
            self.logger.critical("Can not split host/network list on spaces.")
            self.logger.critical("Network share: " + self.volume)
            sys.exit()

        try:
            self.rulesObj = Rules(self.rules_text, self.logger)
        except RuleParseException as e:
            self.logger.critical(e)
            self.logger.critical("Could not parse rule for " + self.volume)
            sys.exit(1)

    def remove_targets(self):
        for target in self.targets:
            self.rulesObj.remove_target(target)
        self.rulesObj.delete_empty_rules()
        self.rulesObj.refactor_rule_positions()
        self.rulesObj.factor_options()

    def define_targets(self, targets, options):

        if not isinstance(targets, list):
            self.logger.critical("define_targets function requires a list as an argument")
            sys.exit(1)
        self.targets = targets
        self.options = options
        self.rulesObj.factor_options()

        # deal with if a target is a wildcard for network
        tmplist = []
        for target in self.targets:
            if target == '*':
                target = '0.0.0.0/0'
            tmplist.append(target)
        self.targets = tmplist

        self.rulesObj.define_targets_options(targets, options)
