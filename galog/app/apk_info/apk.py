# Copyright 2021 Appknox <engineering@appknox.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import division
from __future__ import print_function

from builtins import str
from struct import unpack
from xml.dom import minidom

from .axmlprinter import AXMLPrinter
from .axmlparser import AXMLParser
from . import typeconstants as const


import io
from zlib import crc32
import os
import re
import zipfile
import logging
import hashlib
import binascii

import lxml.sax
from xml.dom.pulldom import SAX2DOM


import xml.etree.ElementTree as ET
from io import BytesIO, StringIO

# Used for reading Certificates
from asn1crypto import cms, x509, keys


NS_ANDROID_URI = 'http://schemas.android.com/apk/res/android'
NS_ANDROID = '{{{}}}'.format(NS_ANDROID_URI)  # Namespace as used by etree

log = logging.getLogger("pyaxmlparser.core")


class APK:
    def __init__(self, filename):
        self.xml = {}
        self.package = ""
        self.androidversion = {}
        self.permissions = []
        self.uses_permissions = []
        self.valid_apk = False
        self.filename = filename

        self._apk_analysis()

    def _ns(self, name):
        """
        return the name including the Android namespace
        """
        return NS_ANDROID + name

    def _apk_analysis(self):
        """
        Run analysis on the APK file.

        This method is usually called by __init__ except if skip_analysis is False.
        It will then parse the AndroidManifest.xml and set all fields in the APK class which can be
        extracted from the Manifest.
        """
        i = "AndroidManifest.xml"
        try:
            zip_file = zipfile.ZipFile(self.filename, mode="r")
            manifest_data = zip_file.read(i)

        except KeyError:
            log.warning("Missing AndroidManifest.xml. Is this an APK file?")

        except Exception as e:
            log.error(f"Failed to open target file. Reason - {e}")
            return

        try:
            ap = AXMLPrinter(manifest_data)
            self.xml[i] = ET.parse(BytesIO(ap.getBuff())).getroot()

        except Exception:
            log.error("Failed to decode AndroidManifest.xml")
            return

        if self.xml[i].tag != "manifest":
            log.error("AndroidManifest.xml does not start with a <manifest> tag! Is this a valid APK?")
            return

        self.package = self.get_attribute_value("manifest", "package")
        self.androidversion["Code"] = self.get_attribute_value("manifest", "versionCode")
        self.androidversion["Name"] = self.get_attribute_value("manifest", "versionName")
        permission = list(self.get_all_attribute_value("uses-permission", "name"))
        self.permissions = list(set(self.permissions + permission))

        for uses_permission in self.find_tags("uses-permission"):
            self.uses_permissions.append([
                self.get_value_from_tag(uses_permission, "name"),
                self._get_permission_maxsdk(uses_permission)
            ])

        self.valid_apk = True

    def _get_permission_maxsdk(self, item):
        maxSdkVersion = None
        try:
            maxSdkVersion = int(self.get_value_from_tag(item, "maxSdkVersion"))
        except ValueError:
            log.warning(self.get_max_sdk_version() + 'is not a valid value for <uses-permission> maxSdkVersion')
        except TypeError:
            pass
        return maxSdkVersion

    def is_valid_APK(self):
        """
        Return true if the APK is valid, false otherwise.
        An APK is seen as valid, if the AndroidManifest.xml could be successful parsed.
        This does not mean that the APK has a valid signature nor that the APK
        can be installed on an Android system.

        :rtype: boolean
        """
        return self.valid_apk

    def get_filename(self):
        """
        Return the filename of the APK

        :rtype: :class:`str`
        """
        return self.filename

    def get_package(self):
        """
        Return the name of the package

        This information is read from the AndroidManifest.xml

        :rtype: :class:`str`
        """
        return self.package

    def get_androidversion_code(self):
        """
        Return the android version code

        This information is read from the AndroidManifest.xml

        :rtype: :class:`str`
        """
        return self.androidversion["Code"]

    def get_androidversion_name(self):
        """
        Return the android version name

        This information is read from the AndroidManifest.xml

        :rtype: :class:`str`
        """
        return self.androidversion["Name"]

    def _format_value(self, value):
        """
        Format a value with packagename, if not already set

        :param value:
        :return:
        """
        if len(value) > 0:
            if value[0] == ".":
                value = self.package + value
            else:
                v_dot = value.find(".")
                if v_dot == 0:
                    value = self.package + "." + value
                elif v_dot == -1:
                    value = self.package + "." + value
        return value

    def get_all_attribute_value(
        self, tag_name, attribute, format_value=True, **attribute_filter
    ):
        """
        Return all the attribute values in xml files which match with the tag name and the specific attribute
        :param tag_name: specify the tag name
        :type tag_name: string
        :param attribute: specify the attribute
        :type attribute: string
        :param format_value: specify if the value needs to be formatted with packagename
        :type format_value: boolean
        """
        tags = self.find_tags(tag_name, **attribute_filter)
        for tag in tags:
            value = tag.get(attribute) or tag.get(self._ns(attribute))
            if value is not None:
                if format_value:
                    yield self._format_value(value)
                else:
                    yield value

    def get_attribute_value(
        self, tag_name, attribute, format_value=False, **attribute_filter
    ):
        """
        Return the attribute value in xml files which matches the tag name and the specific attribute
        :param tag_name: specify the tag name
        :type tag_name: string
        :param attribute: specify the attribute
        :type attribute: string
        :param format_value: specify if the value needs to be formatted with packagename
        :type format_value: boolean
        """

        for value in self.get_all_attribute_value(
                tag_name, attribute, format_value, **attribute_filter):
            if value is not None:
                return value

    def get_value_from_tag(self, tag, attribute):
        """
        Return the value of the android prefixed attribute in a specific tag.

        This function will always try to get the attribute with a android: prefix first,
        and will try to return the attribute without the prefix, if the attribute could not be found.
        This is useful for some broken AndroidManifest.xml, where no android namespace is set,
        but could also indicate malicious activity (i.e. wrongly repackaged files).
        A warning is printed if the attribute is found without a namespace prefix.

        If you require to get the exact result you need to query the tag directly:

        example::
            >>> from lxml.etree import Element
            >>> tag = Element('bar', nsmap={'android': 'http://schemas.android.com/apk/res/android'})
            >>> tag.set('{http://schemas.android.com/apk/res/android}foobar', 'barfoo')
            >>> tag.set('name', 'baz')
            # Assume that `a` is some APK object
            >>> a.get_value_from_tag(tag, 'name')
            'baz'
            >>> tag.get('name')
            'baz'
            >>> tag.get('foobar')
            None
            >>> a.get_value_from_tag(tag, 'foobar')
            'barfoo'

        :param lxml.etree.Element tag: specify the tag element
        :param str attribute: specify the attribute name
        :returns: the attribute's value, or None if the attribute is not present
        """

        # TODO: figure out if both android:name and name tag exist which one to give preference:
        # currently we give preference for the namespace one and fallback to the un-namespaced
        value = tag.get(self._ns(attribute))
        if value is None:
            value = tag.get(attribute)

            if value:
                # If value is still None, the attribute could not be found, thus is not present
                log.warning("Failed to get the attribute '{}' on tag '{}' with namespace. "
                            "But found the same attribute without namespace!".format(attribute, tag.tag))
        return value

    def find_tags(self, tag_name, **attribute_filter):
        """
        Return a list of all the matched tags in all available xml
        :param tag: specify the tag name
        :type tag: string
        """
        all_tags = [
            self.find_tags_from_xml(
                i, tag_name, **attribute_filter
            )
            for i in self.xml
        ]
        return [tag for tag_list in all_tags for tag in tag_list]

    def find_tags_from_xml(
        self, xml_name, tag_name, **attribute_filter
    ):
        """
        Return a list of all the matched tags in a specific xml
        :param xml_name: specify from which xml to pick the tag from
        :type xml_name: string
        :param tag_name: specify the tag name
        :type tag_name: string
        """
        xml = self.xml[xml_name]
        if xml is None:
            return []
        if xml.tag == tag_name:
            if self.is_tag_matched(
                xml.tag, **attribute_filter
            ):
                return [xml]
            return []
        tags = xml.findall(".//" + tag_name)
        return [
            tag for tag in tags if self.is_tag_matched(
                tag, **attribute_filter
            )
        ]

    def is_tag_matched(self, tag, **attribute_filter):
        """
        Return true if the attributes matches in attribute filter.

        An attribute filter is a dictionary containing: {attribute_name: value}.
        This function will return True if and only if all attributes have the same value.
        This function allows to set the dictionary via kwargs, thus you can filter like this:

        example::
            a.is_tag_matched(tag, name="foobar", other="barfoo")

        This function uses a fallback for attribute searching. It will by default use
        the namespace variant but fall back to the non-namespace variant.
        Thus specifiying :code:`{"name": "foobar"}` will match on :code:`<bla name="foobar" \>`
        as well as on :code:`<bla android:name="foobar" \>`.

        :param lxml.etree.Element tag: specify the tag element
        :param attribute_filter: specify the attribute filter as dictionary
        """
        if len(attribute_filter) <= 0:
            return True
        for attr, value in attribute_filter.items():
            _value = self.get_value_from_tag(tag, attr)
            if _value != value:
                return False
        return True

    def get_main_activities(self):
        """
        Return names of the main activities

        These values are read from the AndroidManifest.xml

        :rtype: a set of str
        """
        x = set()
        y = set()

        for i in self.xml:
            if self.xml[i] is None:
                continue
            activities_and_aliases = self.xml[i].findall(".//activity") + \
                self.xml[i].findall(".//activity-alias")

            for item in activities_and_aliases:
                # Some applications have more than one MAIN activity.
                # For example: paid and free content
                activityEnabled = item.get(self._ns("enabled"))
                if activityEnabled == "false":
                    continue

                for sitem in item.findall(".//action"):
                    val = sitem.get(self._ns("name"))
                    if val == "android.intent.action.MAIN":
                        activity = item.get(self._ns("name"))
                        if activity is not None:
                            x.add(item.get(self._ns("name")))
                        else:
                            log.warning('Main activity without name')

                for sitem in item.findall(".//category"):
                    val = sitem.get(self._ns("name"))
                    if val == "android.intent.category.LAUNCHER":
                        activity = item.get(self._ns("name"))
                        if activity is not None:
                            y.add(item.get(self._ns("name")))
                        else:
                            log.warning('Launcher activity without name')

        return x.intersection(y)

    def get_main_activity(self):
        """
        Return the name of the main activity

        This value is read from the AndroidManifest.xml

        :rtype: str
        """
        activities = self.get_main_activities()
        if len(activities) > 0:
            return self._format_value(activities.pop())
        return None

    def get_activities(self):
        """
        Return the android:name attribute of all activities

        :rtype: a list of str
        """
        return list(self.get_all_attribute_value("activity", "name"))

    def get_services(self):
        """
        Return the android:name attribute of all services

        :rtype: a list of str
        """
        return list(self.get_all_attribute_value("service", "name"))

    def get_receivers(self):
        """
        Return the android:name attribute of all receivers

        :rtype: a list of string
        """
        return list(self.get_all_attribute_value("receiver", "name"))

    def get_providers(self):
        """
        Return the android:name attribute of all providers

        :rtype: a list of string
        """
        return list(self.get_all_attribute_value("provider", "name"))

    def get_intent_filters(self, itemtype, name):
        """
        Find intent filters for a given item and name.

        Intent filter are attached to activities, services or receivers.
        You can search for the intent filters of such items and get a dictionary of all
        attached actions and intent categories.

        :param itemtype: the type of parent item to look for, e.g. `activity`,  `service` or `receiver`
        :param name: the `android:name` of the parent item, e.g. activity name
        :return: a dictionary with the keys `action` and `category` containing the `android:name` of those items
        """
        d = {"action": [], "category": []}

        for i in self.xml:
            # TODO: this can probably be solved using a single xpath
            for item in self.xml[i].findall(".//" + itemtype):
                if self._format_value(item.get(self._ns("name"))) == name:
                    for sitem in item.findall(".//intent-filter"):
                        for ssitem in sitem.findall("action"):
                            if ssitem.get(self._ns("name")) not in d["action"]:
                                d["action"].append(ssitem.get(self._ns("name")))
                        for ssitem in sitem.findall("category"):
                            if ssitem.get(self._ns("name")) not in d["category"]:
                                d["category"].append(ssitem.get(self._ns("name")))

        if not d["action"]:
            del d["action"]

        if not d["category"]:
            del d["category"]

        return d

    def get_permissions(self):
        """
        Return permissions names declared in the AndroidManifest.xml.

        It is possible that permissions are returned multiple times,
        as this function does not filter the permissions, i.e. it shows you
        exactly what was defined in the AndroidManifest.xml.

        Implied permissions, which are granted automatically, are not returned
        here. Use :meth:`get_uses_implied_permission_list` if you need a list
        of implied permissions.

        :returns: A list of permissions
        :rtype: list
        """
        return self.permissions

    def get_uses_implied_permission_list(self):
        """
            Return all permissions implied by the target SDK or other permissions.

            :rtype: list of string
        """
        target_sdk_version = self.get_effective_target_sdk_version()

        READ_CALL_LOG = 'android.permission.READ_CALL_LOG'
        READ_CONTACTS = 'android.permission.READ_CONTACTS'
        READ_EXTERNAL_STORAGE = 'android.permission.READ_EXTERNAL_STORAGE'
        READ_PHONE_STATE = 'android.permission.READ_PHONE_STATE'
        WRITE_CALL_LOG = 'android.permission.WRITE_CALL_LOG'
        WRITE_CONTACTS = 'android.permission.WRITE_CONTACTS'
        WRITE_EXTERNAL_STORAGE = 'android.permission.WRITE_EXTERNAL_STORAGE'

        implied = []

        implied_WRITE_EXTERNAL_STORAGE = False
        if target_sdk_version < 4:
            if WRITE_EXTERNAL_STORAGE not in self.permissions:
                implied.append([WRITE_EXTERNAL_STORAGE, None])
                implied_WRITE_EXTERNAL_STORAGE = True
            if READ_PHONE_STATE not in self.permissions:
                implied.append([READ_PHONE_STATE, None])

        if (WRITE_EXTERNAL_STORAGE in self.permissions or implied_WRITE_EXTERNAL_STORAGE) \
           and READ_EXTERNAL_STORAGE not in self.permissions:
            maxSdkVersion = None
            for name, version in self.uses_permissions:
                if name == WRITE_EXTERNAL_STORAGE:
                    maxSdkVersion = version
                    break
            implied.append([READ_EXTERNAL_STORAGE, maxSdkVersion])

        if target_sdk_version < 16:
            if READ_CONTACTS in self.permissions \
               and READ_CALL_LOG not in self.permissions:
                implied.append([READ_CALL_LOG, None])
            if WRITE_CONTACTS in self.permissions \
               and WRITE_CALL_LOG not in self.permissions:
                implied.append([WRITE_CALL_LOG, None])

        return implied

    def get_max_sdk_version(self):
        """
            Return the android:maxSdkVersion attribute

            :rtype: string
        """
        return self.get_attribute_value("uses-sdk", "maxSdkVersion")

    def get_min_sdk_version(self):
        """
            Return the android:minSdkVersion attribute

            :rtype: string
        """
        return self.get_attribute_value("uses-sdk", "minSdkVersion")

    def get_target_sdk_version(self):
        """
            Return the android:targetSdkVersion attribute

            :rtype: string
        """
        return self.get_attribute_value("uses-sdk", "targetSdkVersion")

    def get_effective_target_sdk_version(self):
        """
            Return the effective targetSdkVersion, always returns int > 0.

            If the targetSdkVersion is not set, it defaults to 1.  This is
            set based on defaults as defined in:
            https://developer.android.com/guide/topics/manifest/uses-sdk-element.html

            :rtype: int
        """
        target_sdk_version = self.get_target_sdk_version()
        if not target_sdk_version:
            target_sdk_version = self.get_min_sdk_version()
        try:
            return int(target_sdk_version)
        except (ValueError, TypeError):
            return 1

    def get_libraries(self):
        """
            Return the android:name attributes for libraries

            :rtype: list
        """
        return list(self.get_all_attribute_value("uses-library", "name"))

    def get_features(self):
        """
        Return a list of all android:names found for the tag uses-feature
        in the AndroidManifest.xml

        :return: list
        """
        return list(self.get_all_attribute_value("uses-feature", "name"))

    def is_wearable(self):
        """
        Checks if this application is build for wearables by
        checking if it uses the feature 'android.hardware.type.watch'
        See: https://developer.android.com/training/wearables/apps/creating.html for more information.

        Not every app is setting this feature (not even the example Google provides),
        so it might be wise to not 100% rely on this feature.

        :return: True if wearable, False otherwise
        """
        return 'android.hardware.type.watch' in self.get_features()

    def is_leanback(self):
        """
        Checks if this application is build for TV (Leanback support)
        by checkin if it uses the feature 'android.software.leanback'

        :return: True if leanback feature is used, false otherwise
        """
        return 'android.software.leanback' in self.get_features()

    def is_androidtv(self):
        """
        Checks if this application does not require a touchscreen,
        as this is the rule to get into the TV section of the Play Store
        See: https://developer.android.com/training/tv/start/start.html for more information.

        :return: True if 'android.hardware.touchscreen' is not required, False otherwise
        """
        return self.get_attribute_value(
            'uses-feature', 'name', required="false",
            name="android.hardware.touchscreen"
        ) == "android.hardware.touchscreen"

    def get_android_manifest_axml(self):
        """
            Return the :class:`AXMLPrinter` object which corresponds to the AndroidManifest.xml file

            :rtype: :class:`~androguard.core.bytecodes.axml.AXMLPrinter`
        """
        try:
            return self.axml["AndroidManifest.xml"]
        except KeyError:
            return None

    def get_android_manifest_xml(self):
        """
        Return the parsed xml object which corresponds to the AndroidManifest.xml file

        :rtype: :class:`~lxml.etree.Element`
        """
        try:
            return self.xml["AndroidManifest.xml"]
        except KeyError:
            return None

    def show(self):
        print("REQUESTED PERMISSIONS:")
        requested_permissions = self.get_permissions()
        for i in requested_permissions:
            print("\t", i)

        print("MAIN ACTIVITY: ", self.get_main_activity())

        print("ACTIVITIES: ")
        activities = self.get_activities()
        for i in activities:
            filters = self.get_intent_filters("activity", i)
            print("\t", i, filters or "")

        print("SERVICES: ")
        services = self.get_services()
        for i in services:
            filters = self.get_intent_filters("service", i)
            print("\t", i, filters or "")

        print("RECEIVERS: ")
        receivers = self.get_receivers()
        for i in receivers:
            filters = self.get_intent_filters("receiver", i)
            print("\t", i, filters or "")

        print("PROVIDERS: ", self.get_providers())

    @property
    def packagename(self):
        return self.get_package()

    @property
    def version_name(self):
        return self.get_androidversion_name()

    @property
    def version_code(self):
        return self.get_androidversion_code()