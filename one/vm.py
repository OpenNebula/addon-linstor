# -*- coding: utf-8 -*-
"""
OpenNebula Driver for Linstor
Copyright 2018 LINBIT USA LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import xml.etree.ElementTree as ET

from one import util


class Vm(object):

    """Docstring for vm. """

    def __init__(self, xml):
        self._root = ET.fromstring(xml)
        self._disks = {}
        for disk in self._root.find("TEMPLATE").findall("DISK"):
            self._disks[disk.find("DISK_ID").text] = disk

    @property
    def ID(self):
        """Returns name"""
        try:
            return self._root.find("ID").text
        except AttributeError:
            return ""

    @property
    def disk_IDs(self):
        """Returns IDs of all attached disks."""
        return list(self._disks)

    @property
    def has_context(self):
        return self._root.find("TEMPLATE").find("CONTEXT") is not None

    @property
    def context_ID(self):
        return self._root.find("TEMPLATE").find("CONTEXT").find("DISK_ID").text

    def disk(self, disk_ID):
        """Returns disk with the given ID"""
        try:
            return self._disks[disk_ID]
        except KeyError:
            util.error_message(
                "couldn't find disk {} on vm {}".format(disk_ID, self.ID)
            )
            raise

    def disk_image_ID(self, disk_ID):
        """Returns disk_image_ID"""
        try:
            return self.disk(disk_ID).find("IMAGE_ID").text
        except AttributeError:
            return ""

    def disk_type(self, disk_ID):
        """Returns disk_type"""
        try:
            return self.disk(disk_ID).find("TYPE").text
        except AttributeError:
            return ""

    def disk_save_as(self, disk_ID):
        """Returns disk_save_as"""
        try:
            return self.disk(disk_ID).find("SAVE_AS").text
        except AttributeError:
            return ""

    def disk_target(self, disk_ID):
        """Returns disk_target"""
        try:
            return self.disk(disk_ID).find("TARGET").text
        except AttributeError:
            return ""

    def disk_persistent(self, disk_ID):
        """Returns disk_persistent"""
        try:
            return self.disk(disk_ID).find("PERSISTENT").text
        except AttributeError:
            return ""

    def disk_is_clone(self, disk_ID):
        """Returns disk_persistent"""
        try:
            return self.disk(disk_ID).find("CLONE").text
        except AttributeError:
            return ""

    def disk_source(self, disk_ID):
        """Returns disk_source"""
        try:
            return self.disk(disk_ID).find("SOURCE").text
        except AttributeError:
            return ""

    def tm_mad(self, disk_ID):
        """Returns the tm driver identifier"""
        try:
            return self.disk(disk_ID).find("TM_MAD").text
        except AttributeError:
            return None
