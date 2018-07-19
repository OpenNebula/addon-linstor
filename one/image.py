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
