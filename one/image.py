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
        root = ET.fromstring(xml)
        self._ID = root.find("ID").text
        self._size = root.find("SIZE").text
        self._datastore_ID = root.find("DATASTORE_ID").text
        self._FS_type = root.find("FSTYPE").text
        self._path = root.find("PATH").text
        self._cloning_ID = root.find("CLONING_ID").text

        self._md5 = root.find("TEMPLATE").find("MD5")
        self._sha1 = root.find("TEMPLATE").find("SHA1")
        self._no_decompress = root.find("TEMPLATE").find("NO_DECOMPRESS")
        self._limit_transfer_bw = root.find("TEMPLATE").find("LIMIT_TRANSFER_BW")

    @property
    def ID(self):
        """Returns name"""
        return self._ID

    @property
    def size(self):
        """Returns name"""
        return self._size

    @property
    def datastore_ID(self):
        """Returns name"""
        return self._datastore_ID

    @property
    def FS_type(self):
        """Returns FS_type"""
        return self._FS_type

    @property
    def path(self):
        """Returns path"""
        return self._path

    @property
    def cloning_ID(self):
        """Returns cloning_ID"""
        return self._cloning_ID

    @property
    def md5(self):
        """Returns md5"""
        try:
            return self._md5.text
        except AttributeError:
            return '""'

    @property
    def sha1(self):
        """Returns sha1"""
        try:
            return self._sha1.text
        except AttributeError:
            return '""'

    @property
    def no_decompress(self):
        """Returns no_decompress"""
        try:
            return self._no_decompress.text
        except AttributeError:
            return '""'

    @property
    def limit_transfer_bw(self):
        """Returns limit_transfer_bw"""
        try:
            return self._limit_transfer_bw.text
        except AttributeError:
            return '""'
