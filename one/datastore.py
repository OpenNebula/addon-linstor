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


class Datastore(object):

    """Docstring for Datastore. """

    def __init__(self, xml):
        root = ET.fromstring(xml)
        self._ID = root.find("ID").text
        self._name = root.find("NAME").text
        self._ds_mad = root.find("DS_MAD").text
        self._tm_mad = root.find("TM_MAD").text
        self._total_mb = root.find("TOTAL_MB").text
        self._free_mb = root.find("FREE_MB").text
        self._used_mb = root.find("USED_MB").text

    @property
    def ID(self):
        """Returns ID"""
        return self._ID

    @property
    def name(self):
        """Returns name"""
        return self._name

    @property
    def ds_mad(self):
        """Returns ds_mad"""
        return self._ds_mad

    @property
    def tm_mad(self):
        """Returns tm_mad"""
        return self._tm_mad

    @property
    def total_mb(self):
        """Returns total_mb"""
        return self._total_mb

    @property
    def free_mb(self):
        """Returns free_mb"""
        return self._free_mb

    @property
    def used_mb(self):
        """Returns used_mb"""
        return self._used_mb
