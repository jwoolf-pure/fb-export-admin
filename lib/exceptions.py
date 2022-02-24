class NetworkRangeConflict(Exception):

    def __init__(self, target):
        self.target = target
        self.message = "Can not insert network rule for " + self.target + " Network address conflict."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.target}'


class RuleParseException(Exception):

    def __init__(self, rule_line, message):
        self.rule_line = rule_line
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.rule_line}'


class DefineTargetException(Exception):

    def __init__(self, target):
        self.target = target
        self.message = "Can not scan defined target for " + self.target + " Regex exception."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.target}'


class TargetNotInserted(Exception):

    def __init__(self, target):
        self.target = target
        self.message = "Did not insert target " + self.target + " Insert failed."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.target}'


class TargetFoundNotForcingWarning(Exception):

    def __init__(self, target):
        self.target = target
        self.message = "Did not insert target " + self.target + \
                       " Found network range in scope of target. Did not add.  Use --force_target to force add."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.target}'


class TargetNetworkFoundForIPWarning(Exception):

    def __init__(self, target):
        self.target = target
        self.message = "Did not insert target IP " + self.target + \
                       " Found network range in scope of target. Did not add.  Use --force_target to force add."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.target}'


class NoSessionException(Exception):

    def __init__(self, remotes):
        self.remotes = remotes
        self.message = "Did not find remote(s) for " + str(self.remotes) + \
                       " in sessions directory.  Do you need ot add the Flashblade?"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.remotes}'


class SharesNotDefined(Exception):

    def __init__(self):
        self.message = "Did not find any shares defined by --file_shares or --load_from_file. Can not continue."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class SessionExistsError(Exception):

    def __init__(self, session_dir):
        self.session_dir = session_dir
        self.message = "Found session " + session_dir + " already exists."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class FilesystemGetException(Exception):

    def __init__(self, error):
        self.error = error
        self.message = "Did not get filesystem(s)."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.error}'


class ApplyRulesException(Exception):

    def __init__(self, error):
        self.error = error
        self.message = "Rule not applied."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.error}'


class FBInitException(Exception):

    def __init__(self, error):
        self.error = error
        self.message = "Did not initiate session with FlashBlade."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.error}'


class YamlReadException(Exception):

    def __init__(self, group):
        self.group = group
        self.message = "Could not read settings.yaml file for group."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.group}'


class SettingsGroupException(Exception):

    def __init__(self, group):
        self.group = group
        self.message = "Could not get file group for group."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.group}'


class RuleExceedsMaxLength(Exception):

    def __init__(self, share):
        self.share = share
        self.message = "Rule exceeds limit of 4096 chars."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.share}'


class TargetFoundWarning(Exception):

    def __init__(self, target):
        self.target = target
        self.message = "Did not insert target " + self.target + \
                       " Found target. Did not add.  Use --force_target to force add."
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.target}'
