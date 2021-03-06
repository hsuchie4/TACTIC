###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ["AccessRule", "AccessRuleInGroup", "AccessRuleBuilder"]

import types

from pyasm.common import *
from pyasm.search import *


# DEPRECATED

class AccessRuleException(Exception):
    pass

class AccessRule(SObject):
    '''Treat security rules as a separate handler'''
    SEARCH_TYPE = "sthpw/access_rule"

    def get_primary_key(my):
        return "code"

    def get_foreign_key(my):
        return "access_rule_code"

    def get_by_groups(groups):
        if not groups:
            return []

        access_rule_in_groups = AccessRuleInGroup.get_by_groups(groups)
        if not access_rule_in_groups:
            return []

        codes = [x.get_value("access_rule_code") for x in access_rule_in_groups]
        search = Search(AccessRule)
        search.add_filters("code", codes)

        return search.get_sobjects()

    get_by_groups = staticmethod(get_by_groups)



class AccessRuleInGroup(SObject):
    '''Treat access rules as a separate handler'''
    SEARCH_TYPE = "sthpw/access_rule_in_group"

    def get_by_groups(groups):
        if not groups:
            []

        search = Search(AccessRuleInGroup)

        group_names = [x.get_value("login_group") for x in groups]
        search.add_filters("login_group", group_names)

        return search.get_sobjects()

    get_by_groups = staticmethod(get_by_groups)





class AccessRuleBuilder(object):
    def __init__(my, xml=None):
        if not xml:
            my.xml = Xml()
            my.xml.create_doc("rules")
        else:
            if type(xml) in [types.StringType]:
                my.xml = Xml()
                my.xml.read_string(xml)
            else:
                my.xml = xml
        my.root_node = my.xml.get_root_node()


    def add_rule(my, group, key, access, unique=True):

        node = None
        if isinstance(key, dict):
            sub_paths = ["@%s='%s'"%(k,v) for k,v in key.items()]
            xpath = "rules/rule[@group='%s' and %s]" % (group, ' and '.join(sub_paths))
        else:
            xpath = "rules/rule[@group='%s' and @key='%s']" % (group,key)

            
        if unique:
            node = my.xml.get_node( xpath )
        if node is None:
            node = my.xml.create_element("rule")

        Xml.set_attribute(node, "group", group)
        if isinstance(key, dict):
            for k,v in key.items():
                Xml.set_attribute(node, k, v)
        else:
            Xml.set_attribute(node, "key", key)
        Xml.set_attribute(node, "access", access)

        #my.root_node.appendChild(node)
        Xml.append_child(my.root_node, node)

    def add_default_rule(my, group, access):
        '''add default rule'''
        node = None

        node = my.xml.get_node("rules/rule[@group='%s' and @default]" % group )
        if node == None:
            node = my.xml.create_element("rule")

        Xml.set_attribute(node, "group", group)
        Xml.set_attribute(node, "default", access)

        #my.root_node.appendChild(node)
        Xml.append_child(my.root_node, node)


    def remove_rule(my, group, key):

        node = None
        if isinstance(key, dict):
            sub_paths = ["@%s='%s'"%(k,v) for k,v in key.items()]
            xpath = "rules/rule[@group='%s' and %s]" % (group, ' and '.join(sub_paths))
        else:
            xpath = "rules/rule[@group='%s' and @key='%s']" % (group, key)

        # in case there are multiple manually inserted nodes
        nodes = my.xml.get_nodes(xpath)
        parent_node = my.xml.get_node("rules")
        for node in nodes:
            if node is not None:
                my.xml.remove_child(parent_node, node)

    def update_rule(my, xpath, update_dict):
        '''update the rule with the update_dict'''
        
        # in case there are multiple manually inserted nodes
        nodes = my.xml.get_nodes(xpath)
        parent_node = my.xml.get_node("rules")
        for node in nodes:
            if node is not None:
                for name, value in update_dict.items():
                    Xml.set_attribute(node, name, value)


    def get_default(my, group):
        '''get the default attribute'''
        node = my.xml.get_node("rules/rule[@default and @group='%s']" %group)
        if node is not None:
            return my.xml.get_attribute(node, 'default')
        else:
            return ''


    def to_string(my):
        return my.xml.to_string()


