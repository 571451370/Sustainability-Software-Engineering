#
# Copyright 2014 ZHAW SoE
#
# Authors: Lucas Graf <graflu0@students.zhaw.ch>
#          Toni Zehnder <zehndton@students.zhaw.ch>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Inspector abstraction for read-only access to hardware components"""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Inspector(object):
    @abc.abstractmethod
    def inspect_generic(self, host, identifier, cache):
        """A generic inspect function.

        :param host: the target host
        :param identifier: the identifier of the metric
        :param cache: cache passed from the pollster
        :return: an iterator of (value, metadata, extra)
        :return value: the sample value
        :return metadata: dict to construct sample's metadata
        :return extra: dict of extra info to help constructing sample
        """