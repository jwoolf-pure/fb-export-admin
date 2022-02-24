from lib.export import *
from lib.exceptions import *


class ExportRules():

    def __init__(self, remote, logger):
        self.exports_list = []
        self.logger = logger
        self.remote = remote

    def add_export(self, name, initial_rules):
        self.exports_list.append(Exports(name, initial_rules, self.logger))

    def define_targets(self, targets, rules):

        try:
            targets = targets.split(',')
        except:
            targets = []
        for export in self.exports_list:
            export.define_targets(targets, rules)

    def delete_targets(self):
        for export in self.exports_list:
            export.remove_targets()

    def apply_rules_targets(self, force_target=False):

        for export in self.exports_list:
            try:
                export.rulesObj.insert_network_targets(force_target)
            except NetworkRangeConflict as e:
                self.logger.critical(e)
                self.logger.critical("For network share " + export.volume)
                sys.exit(1)

            except TargetNotInserted as e:
                self.logger.critical(e)
                self.logger.critical("Did not insert target into share " + export.volume)
                sys.exit(1)

            except TargetFoundNotForcingWarning as e:
                self.logger.warning(e)
                self.logger.warning('Not inserting target for volume ' + export.volume)

            except TargetFoundWarning as e:
                self.logger.warning(e)
                self.logger.warning('Not inserting target for volume ' + export.volume)

            try:
                export.rulesObj.insert_ip_targets(force_target)
            except TargetNetworkFoundForIPWarning as e:
                self.logger.warning(e)
                self.logger.warning("Not inserting IP address for share " + export.volume)

            except TargetFoundWarning as e:
                self.logger.warning(e)
                self.logger.warning('Not inserting target for volume ' + export.volume)

    def write_rules(self):
        retObj = []
        for export in self.exports_list:
            retObj.append({
                'name': export.volume,
                'rules': export.rulesObj.write_rules()
            })
            if len(export.rulesObj.write_rules()) > 4096:
                raise RuleExceedsMaxLength(export.volume)
        return retObj
