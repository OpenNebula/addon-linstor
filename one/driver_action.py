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

from one import datastore, image


class DriverAction(object):

    """Docstring for vm. """

    def __init__(self, xml):
        root = ET.fromstring(xml)

        self._image = image.Image(ET.tostring(root.find("IMAGE")))
        self._datastore = datastore.Datastore(ET.tostring(root.find("DATASTORE")))

    @property
    def image(self):
        """Returns image"""
        return self._image

    @property
    def datastore(self):
        """Returns datastore"""
        return self._datastore
