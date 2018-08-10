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


class Vm(object):

    """Docstring for vm. """

    def __init__(self, xml, disk_ID):
        self._root = ET.fromstring(xml)
        for disk in self._root.find("TEMPLATE").findall("DISK"):
            if disk.find("DISK_ID").text == disk_ID:
                self._disk = disk
                break

    @property
    def ID(self):
        """Returns name"""
        try:
            return self._root.find("ID").text
        except AttributeError:
            return ""

    @property
    def disk_ID(self):
        """Returns disk_ID"""
        try:
            return self._disk.find("DISK_ID").text
        except AttributeError:
            return ""

    @property
    def disk_image_ID(self):
        """Returns disk_image_ID"""
        try:
            return self._disk.find("IMAGE_ID").text
        except AttributeError:
            return ""

    @property
    def disk_type(self):
        """Returns disk_type"""
        try:
            return self._disk.find("TYPE").text
        except AttributeError:
            return ""

    @property
    def disk_save_as(self):
        """Returns disk_save_as"""
        try:
            return self._disk.find("SAVE_AS").text
        except AttributeError:
            return ""

    @property
    def disk_target(self):
        """Returns disk_target"""
        try:
            return self._disk.find("TARGET").text
        except AttributeError:
            return ""

    @property
    def disk_persistent(self):
        """Returns disk_persistent"""
        try:
            return self._disk.find("PERSISTENT").text
        except AttributeError:
            return ""
