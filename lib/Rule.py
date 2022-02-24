import re
import ipaddress

class NetEntity():
    def __init__(self, address, isnetwork, rule_position):
        self.address = address
        self.isnetwork = isnetwork
        self.rule_position = rule_position
        self.ipObj = ipaddress.ip_network(self.address)
        self.isnetwork = isnetwork

        if isnetwork:
            self.parse_network_addr()
        else:
            self.parse_ip_addr()

    def set_rule_position(self, position):
        self.rule_position = position

    def return_rule_position(self):
        return self.rule_position

    def parse_network_addr(self):
        tMatch = re.match(r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\/(\d{1,2})\b', self.address)
        self.a = int(tMatch.group(1))
        self.b = int(tMatch.group(2))
        self.c = int(tMatch.group(3))
        self.d = int(tMatch.group(4))
        self.mask = int(tMatch.group(5))

    def parse_ip_addr(self):
        tMatch = re.match(r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b', self.address)
        self.a = int(tMatch.group(1))
        self.b = int(tMatch.group(2))
        self.c = int(tMatch.group(3))
        self.d = int(tMatch.group(4))
        self.mask = 32

    def is_parent_to_ip(self, nObject):

        if self.address == '0.0.0.0/0':
            return True

        ret = False
        if self.mask < 16 and self.a == nObject.a and nObject.mask >= self.mask:

            nobject_ips = [nObject.address,]
            if self.isnetwork:
                object_ips = [str(each) for each in self.ipObj.hosts() ]
            else:
                object_ips = [self.address,]

            in_network = True
            for each in nobject_ips:
                if each not in object_ips:
                    in_network = False
            if in_network:
                ret = True

        if self.mask >= 16 and self.mask <= 24 and self.a == nObject.a and self.b == nObject.b and nObject.mask >= self.mask:

            nobject_ips = [nObject.address,]

            if self.isnetwork:
                object_ips = [str(each) for each in self.ipObj.hosts() ]
            else:
                object_ips = [self.address,]

            in_network = True
            for each in nobject_ips:
                if each not in object_ips:
                    in_network = False
            if in_network:
                ret = True

        if self.mask >= 24 and self.mask <= 32 and self.a == nObject.a and self.b == nObject.b and self.c == nObject.c \
                and nObject.mask >= self.mask:

            nobject_ips = [nObject.address,]

            if self.isnetwork:
                object_ips = [str(each) for each in self.ipObj.hosts() ]
            else:
                object_ips = [self.address,]

            in_network = True
            for each in nobject_ips:
                if each not in object_ips:
                    in_network = False
            if in_network:
                ret = True
        return ret



    def is_parent_to(self,nObject):

        ret = {'result_successful': False, 'rule_position': nObject.rule_position, 'orule_position': self.rule_position,
               'obj': self.address}

        if self.address == '0.0.0.0/0':
            ret = {'result_successful': True, 'rule_position': nObject.rule_position, 'orule_position': self.rule_position, 'obj': self.address}
            return ret

        if self.mask < 16 and self.a == nObject.a and nObject.mask >= self.mask:
            nobject_ips = nObject.ipObj.hosts()
            if self.isnetwork:
                object_ips = self.ipObj.hosts()
            else:
                object_ips = [self.address,]

            in_network = True
            for each in nobject_ips:
                if each not in object_ips:
                    in_network = False
            if in_network:
                ret = {
                    'result_successful': True,
                    'rule_position': nObject.rule_position,
                    'orule_position': self.rule_position,
                    "obj": self.address
                }

        if self.mask >= 16 and self.mask <= 24 and self.a == nObject.a and self.b == nObject.b and nObject.mask >= self.mask:
            nobject_ips = nObject.ipObj.hosts()
            if self.isnetwork:
                object_ips = self.ipObj.hosts()
            else:
                object_ips = [self.address,]

            in_network = True
            for each in nobject_ips:
                if each not in object_ips:
                    in_network = False
            if in_network:
                ret = {
                    'result_successful': True,
                    'rule_position': nObject.rule_position,
                    'orule_position': self.rule_position,
                    "obj": self.address
                }

        if self.mask >= 24 and self.mask <= 32 and self.a == nObject.a and self.b == nObject.b and self.c == nObject.c \
                and nObject.mask >= self.mask:

            nobject_ips = nObject.ipObj.hosts()
            if self.isnetwork:
                object_ips = self.ipObj.hosts()
            else:
                object_ips = [self.address,]

            in_network = True
            for each in nobject_ips:
                if each not in object_ips:
                    in_network = False
            if in_network:
                ret = {
                    'result_successful': True,
                    'rule_position': nObject.rule_position,
                    'orule_position': self.rule_position,
                    'obj': self.address
                }

        return ret


    def __str__(self):
        return "{} {} {}".format(self.address, str(self.isnetwork), str(self.rule_position))

    def __repr__(self):
        return "{} {} {}".format(self.address, str(self.isnetwork), str(self.rule_position))


class Rule():

    def __init__(self, applied_options, is_paren_rule):
        self.applied_options = applied_options
        self.net_objects = []
        self.is_paren_rule = is_paren_rule

    def is_ip_single_entry(self):
        if len(self.return_entities()) == 1 and not self.net_objects[0].isnetwork:
            return True
        return False

    def return_applied_options(self):
        return self.applied_options

    def set_applied_options(self, options):
        self.applied_options = options

    def min_rule_position(self):
        return self.net_objects[0].return_rule_position()

    def max_rule_position(self):
        return self.net_objects[-1].return_rule_position()

    def return_entities(self):
        return self.net_objects

    def add_net_entity(self, net_entity):
        self.net_objects.append(net_entity)

    def prepend_net_entity(self, net_entity):
        self.net_objects.insert(0, net_entity)

    def print_rule(self):
        self.print_options()
        for each in self.net_objects:
            print(each)

    def apply_effective_options(self, prev_options, options):
        self.previous_options = prev_options
        self.effective_options = options

    def return_effective_options(self):
        return self.effective_options

    def print_options(self):
        print("previous: " + self.previous_options)
        print("applied: " + self.applied_options)
        print("effective: " + self.effective_options)
        print()

    def __str__(self):
        return str(self.applied_options, self.effective_options)

    def __repr__(self):
        return self.applied_options

