class ScanRules():

    def __init__(self, rules, tgt_options, insert_before, insert_after):
        self.rules = rules
        self.tgt_options = tgt_options
        self.insert_before = insert_before
        self.insert_after = insert_after
        self.insert_options = []
        self.found_equiv_rule = False

    def options_equiv(self, options):

        tgt_options = self.tgt_options.split(',')
        obj_options = options.split(',')

        for opt in tgt_options:
            if opt not in obj_options:
                if 'anon' not in opt:
                    return False
        return True

    def return_insert_options(self):
        return self.insert_options

    def scan(self):
        for i, rule in enumerate(self.rules):

            if rule.max_rule_position() >= self.insert_after and rule.min_rule_position() <= self.insert_before or \
                    rule.min_rule_position() == 1 and self.insert_before == 0:

                # Options Match{
                if self.options_equiv(rule.return_effective_options()):

                    # Find possible insertion points
                    # Count through rule targets where options are equiv

                    for j, netObj in enumerate(rule.net_objects):

                        if netObj.return_rule_position() >= self.insert_after and netObj.return_rule_position() <= self.insert_before:
                            pos = netObj.return_rule_position()
                            self.found_equiv_rule = True
                            self.insert_options.append({
                                'rule': i,
                                'rule_position': j,
                                'options_match': True,
                                'before': self.insert_before,
                                'after': self.insert_after,
                                'position': pos
                            })

                # Options don't match
                else:
                    for j, netObj in enumerate(rule.net_objects):
                        if netObj.return_rule_position() >= self.insert_after and netObj.return_rule_position() <= self.insert_before:
                            pos = netObj.return_rule_position()
                            self.insert_options.append({
                                'rule': i,
                                'rule_position': j,
                                'options_match': False,
                                'before': self.insert_before,
                                'after': self.insert_after,
                                'position': pos
                            })

        # if you find rules where options_match then, remove other rules.. if possible, we're only interested in options_match rules.
        if self.found_equiv_rule:
            for i, opts in enumerate(self.insert_options):
                if not opts['options_match']:
                    del self.insert_options[i]
