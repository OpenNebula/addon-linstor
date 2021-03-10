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


class Image(object):

    """Docstring for vm. """

    def __init__(self, xml):
        self.xmlstr = xml  # type: str
        self._root = ET.fromstring(xml)

    def __str__(self):
        return self.xmlstr

    @property
    def id(self):
        """Returns name"""
        try:
            return self._root.find("ID").text or ""
        except AttributeError:
            return ""

    @property
    def size(self):
        """Returns name"""
        try:
            return self._root.find("SIZE").text or ""
        except AttributeError:
            return ""

    @property
    def source(self):
        """Returns source"""
        try:
            return self._root.find("SOURCE").text or ""
        except AttributeError:
            return '""'

    @property
    def target_snap(self):
        """Returns target_snap"""
        try:
            return self._root.find("TARGET_SNAPSHOT").text or ""
        except AttributeError:
            return '""'

    @property
    def datastore_id(self):
        """Returns name"""
        try:
            return self._root.find("DATASTORE_ID").text or ""
        except AttributeError:
            return ""

    @property
    def fs_type(self):
        """Returns FS_type"""
        try:
            return self._root.find("FSTYPE").text or ""
        except AttributeError:
            return ""

    @property
    def fs(self):
        """Returns filesystem"""
        try:
            return self._root.find("FS").text or ""
        except AttributeError:
            return ""

    @property
    def path(self):
        """Returns path"""
        try:
            return self._root.find("PATH").text or ""
        except AttributeError:
            return ""

    @property
    def cloning_id(self):
        """Returns cloning_ID"""
        try:
            return self._root.find("CLONING_ID").text or ""
        except AttributeError:
            return ""

    @property
    def md5(self):
        """Returns md5"""
        try:
            return self._root.find("TEMPLATE").find("MD5").text or ""
        except AttributeError:
            return '""'

    @property
    def sha1(self):
        """Returns sha1"""
        try:
            return self._root.find("TEMPLATE").find("SHA1").text or ""
        except AttributeError:
            return '""'

    @property
    def no_decompress(self):
        """Returns no_decompress"""
        try:
            return self._root.find("TEMPLATE").find("NO_DECOMPRESS").text or ""
        except AttributeError:
            return '""'

    @property
    def limit_transfer_bw(self):
        """Returns limit_transfer_bw"""
        try:
            return self._root.find("TEMPLATE").find("LIMIT_TRANSFER_BW").text or ""
        except AttributeError:
            return '""'

    @property
    def format(self):
        """
        Format of the image
        :return: Image format info string, e.g. raw, qcow2
        :rtype: str
        """
        try:
            return self._root.find("FORMAT").text or ""
        except AttributeError:
            return ''

    @property
    def template_format(self):
        """
        Format of the image
        :return: Image format info string, e.g. raw, qcow2
        :rtype: str
        """
        try:
            return self._root.find("TEMPLATE").find("FORMAT").text or ""
        except AttributeError:
            return ''

    @property
    def template_driver(self):
        """
        Driver of the image
        :return: Image driver info string, e.g. raw, qcow2
        :rtype: str
        """
        try:
            return self._root.find("TEMPLATE").find("DRIVER").text or ""
        except AttributeError:
            return ''
