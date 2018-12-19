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


class Datastore(object):

    """Docstring for Datastore. """

    def __init__(self, xml):
        self.xmlstr = xml  # type: str
        root = ET.fromstring(xml)
        self._ID = root.find("ID").text
        self._name = root.find("NAME").text
        self._ds_mad = root.find("DS_MAD").text
        self._tm_mad = root.find("TM_MAD").text
        self._total_mb = root.find("TOTAL_MB").text
        self._free_mb = root.find("FREE_MB").text
        self._used_mb = root.find("USED_MB").text

        self._base_path = root.find("BASE_PATH")
        self._auto_place = root.find("TEMPLATE").find("LINSTOR_AUTO_PLACE")
        self._deployment_nodes = root.find("TEMPLATE").find("LINSTOR_DEPLOYMENT_NODES")
        self._storage_pool = root.find("TEMPLATE").find("LINSTOR_STORAGE_POOL")
        self._linstor_controllers = root.find("TEMPLATE").find("LINSTOR_CONTROLLERS")
        self._linstor_clone_mode = root.find("TEMPLATE").find("LINSTOR_CLONE_MODE")
        self._restricted_dirs = root.find("TEMPLATE").find("RESTRICTED_DIRS")
        self._safe_dirs = root.find("TEMPLATE").find("SAFE_DIRS")
        self._staging_dirs = root.find("TEMPLATE").find("STAGING_DIR")

    def __str__(self):
        return self.xmlstr

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

    @property
    def base_path(self):
        """Returns base_path"""
        try:
            return self._base_path.text
        except AttributeError:
            return None

    @property
    def auto_place(self):
        """Returns auto_place"""
        try:
            return int(self._auto_place.text)
        except AttributeError:
            return None

    @property
    def deployment_nodes(self):
        """Returns deployment_nodes"""
        try:
            return self._deployment_nodes.text
        except AttributeError:
            return None

    @property
    def storage_pool(self):
        """Returns storage_pool"""
        try:
            return self._storage_pool.text
        except AttributeError:
            return None

    @property
    def linstor_controllers(self):
        """
        Returns string of defined linstor controllers

        :return: string with coma separated linstor hosts: 'host:2343,otherhost:3858' or 'localhost' if not set
        :rtype: str
        """
        try:
            return self._linstor_controllers.text
        except AttributeError:
            return "linstor://localhost"

    @property
    def linstor_clone_mode(self):
        """
        Returns the set linstor clone method
        :return: Set clone mode, if not set default "snapshot" is returned
        :rtype: str
        """
        try:
            clone_method = self._linstor_clone_mode.text
            if clone_method.lower() == "copy":
                return "copy"
            return "snapshot"
        except AttributeError:
            return "snapshot"

    @property
    def restricted_dirs(self):
        """Returns restricted_dirs"""
        try:
            return self._restricted_dirs.text
        except AttributeError:
            return None

    @property
    def safe_dirs(self):
        """Returns safe_dirs"""
        try:
            return self._safe_dirs.text
        except AttributeError:
            return None

    @property
    def staging_dirs(self):
        """Returns staging_dirs or /var/tmp"""
        try:
            return self._safe_dirs.text
        except AttributeError:
            return "/var/tmp"
