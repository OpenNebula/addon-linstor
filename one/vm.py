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
    def id(self):
        """Returns name"""
        try:
            return self._root.find("ID").text
        except AttributeError:
            return ""

    @property
    def disk_ids(self):
        """Returns IDs of all attached disks."""
        return list(self._disks)

    @property
    def has_context(self):
        return self._root.find("TEMPLATE").find("CONTEXT") is not None

    @property
    def context_id(self):
        return self._root.find("TEMPLATE").find("CONTEXT").find("DISK_ID").text

    def disk(self, disk_id):
        """
        Returns disk with the given ID

        :param disk_id:
        :return:
        """
        try:
            return self._disks[disk_id]
        except KeyError:
            util.error_message(
                "couldn't find disk {} on vm {}".format(disk_id, self.id)
            )
            raise

    def disk_image_id(self, disk_id):
        """Returns disk_image_ID"""
        try:
            return self.disk(disk_id).find("IMAGE_ID").text
        except AttributeError:
            return ""

    def disk_type(self, disk_id):
        """Returns disk_type"""
        try:
            return self.disk(disk_id).find("TYPE").text
        except AttributeError:
            return ""

    def disk_datastore_id(self, disk_id):
        """
        Return the datastore id of the disk.

        :param disk_id: disk id to get the datastore id for
        :return:
        """
        try:
            return self.disk(disk_id).find("DATASTORE_ID").text
        except AttributeError:
            return None

    def disk_save_as(self, disk_id):
        """Returns disk_save_as"""
        try:
            return self.disk(disk_id).find("SAVE_AS").text
        except AttributeError:
            return ""

    def disk_target(self, disk_id):
        """Returns disk_target"""
        try:
            return self.disk(disk_id).find("TARGET").text
        except AttributeError:
            return ""

    def disk_persistent(self, disk_id):
        """Returns disk_persistent"""
        try:
            return self.disk(disk_id).find("PERSISTENT").text
        except AttributeError:
            return ""

    def disk_is_clone(self, disk_id):
        """Returns disk_persistent"""
        try:
            return self.disk(disk_id).find("CLONE").text
        except AttributeError:
            return ""

    def disk_source(self, disk_id):
        """Returns disk_source"""
        try:
            return self.disk(disk_id).find("SOURCE").text
        except AttributeError:
            return ""

    def disk_size(self, disk_id):
        """
        Return the disk size, of given disk id
        :param str disk_id: disk id as str
        :return: disk size in megabytes
        :rtype: int
        """
        try:
            return int(self.disk(disk_id).find("SIZE").text)
        except AttributeError:
            return None

    def tm_mad(self, disk_id):
        """Returns the tm driver identifier"""
        try:
            return self.disk(disk_id).find("TM_MAD").text
        except AttributeError:
            return None
