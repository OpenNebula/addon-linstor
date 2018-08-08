# -*- coding: utf-8 -*-
"""
Linstor addon for OpenNebula
Copyright © 2018 LINBIT USA, LLC

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
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
