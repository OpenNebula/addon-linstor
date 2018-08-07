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


class Image(object):

    """Docstring for vm. """

    def __init__(self, xml):
        self._root = ET.fromstring(xml)

    @property
    def ID(self):
        """Returns name"""
        try:
            return self._root.find("ID").text
        except AttributeError:
            return ""

    @property
    def size(self):
        """Returns name"""
        try:
            return self._root.find("SIZE").text
        except AttributeError:
            return ""

    @property
    def datastore_ID(self):
        """Returns name"""
        try:
            return self._root.find("DATASTORE_ID").text
        except AttributeError:
            return ""

    @property
    def FS_type(self):
        """Returns FS_type"""
        try:
            return self._root.find("FSTYPE").text
        except AttributeError:
            return ""

    @property
    def path(self):
        """Returns path"""
        try:
            return self._root.find("PATH").text
        except AttributeError:
            return ""

    @property
    def cloning_ID(self):
        """Returns cloning_ID"""
        try:
            return self._root.find("CLONING_ID").text
        except AttributeError:
            return ""

    @property
    def md5(self):
        """Returns md5"""
        try:
            return self._root.find("TEMPLATE").find("MD5").text
        except AttributeError:
            return '""'

    @property
    def sha1(self):
        """Returns sha1"""
        try:
            return self._root.find("TEMPLATE").find("SHA1").text
        except AttributeError:
            return '""'

    @property
    def no_decompress(self):
        """Returns no_decompress"""
        try:
            return self._root.find("TEMPLATE").find("NO_DECOMPRESS").text
        except AttributeError:
            return '""'

    @property
    def limit_transfer_bw(self):
        """Returns limit_transfer_bw"""
        try:
            return self._root.find("TEMPLATE").find("LIMIT_TRANSFER_BW").text
        except AttributeError:
            return '""'
