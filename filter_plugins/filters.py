#!/usr/bin/python
import re
class FilterModule(object):
    def filters(self):
        return {'annex_iaas_inventory': self.annex_iaas_inventory}

    # the_data should be a read of the inventory file.
    # This appends NEW systems to the inventory file, does not handle pre-existing except sorting.
    def annex_iaas_inventory(self, the_data: dict, new_prefix: str, new_hosts: list):
        new_system = {new_prefix: {"hosts": {}}}
        for node in new_hosts:
            # Populate the new system dict with hosts
            new_system[new_prefix]["hosts"].update({node: None})
            # Update overall hosts dict
            the_data["all"]["hosts"].update({node: None})
            # Update internal_servers dict
            the_data["all"]["children"]["internal_servers"]["hosts"].update({node: None})
            # Update app dict if applicable
            if bool(re.search('.*ap[0-9]', node)):
                the_data["all"]["children"]["app"]["hosts"].update({node: None})
            # Update db dict if applicable
            if bool(re.search('.*db[0-9]', node)):
                the_data["all"]["children"]["db"]["hosts"].update({node: None})
            # Update db dict if we're dealing with a singleton, which should always be an app server
            elif len(new_hosts) == 1:
                the_data["all"]["children"]["db"]["hosts"].update({node: None})
        # Add the newly populated new_system dict to the children dict
        the_data["all"]["children"].update(new_system)

        # Sorting
        all_keys = list(the_data["all"]["hosts"].keys())
        all_keys.sort()
        sorted_all = {i: None for i in all_keys}

        app_keys = list(the_data["all"]["children"]["app"]["hosts"].keys())
        app_keys.sort()
        sorted_app = {i: the_data["all"]["children"]["app"]["hosts"][i] for i in app_keys}

        db_keys = list(the_data["all"]["children"]["db"]["hosts"].keys())
        db_keys.sort()
        sorted_db = {i: the_data["all"]["children"]["db"]["hosts"][i] for i in db_keys}

        ics_keys = list(the_data["all"]["children"]["internal_servers"]["hosts"].keys())
        ics_keys.sort()
        sorted_ics = {i: the_data["all"]["children"]["internal_servers"]["hosts"][i] for i in ics_keys}

        # .update() does not suffice. Replace values with their sorted counterparts.
        the_data["all"]["hosts"] = sorted_all
        the_data["all"]["children"]["app"]["hosts"] = sorted_app
        the_data["all"]["children"]["db"]["hosts"] = sorted_db
        the_data["all"]["children"]["internal_servers"]["hosts"] = sorted_ics

        # Children needs some extra work
        child_keys = list(the_data["all"]["children"].keys())
        child_keys.sort()
        # Be sure app, db, and internal_servers come first
        for i in ["internal_servers", "db", "app"]:
            child_keys.remove(i)
            child_keys.insert(0, i)
        sorted_children = {i: the_data["all"]["children"][i] for i in child_keys}

        the_data["all"]["children"] = sorted_children

        return the_data

# I don't think this filter is used in any of the examples in this git repo due to too much needed censoring, but I felt it was worth sharing.