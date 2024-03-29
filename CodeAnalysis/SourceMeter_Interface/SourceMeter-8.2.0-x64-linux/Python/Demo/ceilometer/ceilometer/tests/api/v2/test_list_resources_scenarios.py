#
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
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
"""Test listing resources.
"""

import datetime
import json

from oslo.utils import timeutils
import six

from ceilometer.publisher import utils
from ceilometer import sample
from ceilometer.tests.api import v2
from ceilometer.tests import db as tests_db


class TestListResources(v2.FunctionalTest,
                        tests_db.MixinTestsWithBackendScenarios):

    def test_empty(self):
        data = self.get_json('/resources')
        self.assertEqual([], data)

    @staticmethod
    def _isotime(timestamp):
        # drop TZ specifier
        return six.text_type(timeutils.isotime(timestamp))[:-1]

    def _verify_sample_timestamps(self, res, first, last):
        self.assertTrue('first_sample_timestamp' in res)
        self.assertEqual(self._isotime(first), res['first_sample_timestamp'])
        self.assertTrue('last_sample_timestamp' in res)
        self.assertEqual(self._isotime(last), res['last_sample_timestamp'])

    def test_instance_no_metadata(self):
        timestamp = datetime.datetime(2012, 7, 2, 10, 40)
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id',
            timestamp=timestamp,
            resource_metadata=None,
            source='test',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        data = self.get_json('/resources')
        self.assertEqual(1, len(data))
        self._verify_sample_timestamps(data[0], timestamp, timestamp)

    def test_instances(self):
        timestamps = {
            'resource-id': datetime.datetime(2012, 7, 2, 10, 40),
            'resource-id-alternate': datetime.datetime(2012, 7, 2, 10, 41),
        }
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id',
            timestamp=timestamps['resource-id'],
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample',
                               },
            source='test',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        sample2 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id-alternate',
            timestamp=timestamps['resource-id-alternate'],
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample2',
                               },
            source='test',
        )
        msg2 = utils.meter_message_from_counter(
            sample2,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg2)

        data = self.get_json('/resources')
        self.assertEqual(2, len(data))
        for res in data:
            timestamp = timestamps.get(res['resource_id'])
            self._verify_sample_timestamps(res, timestamp, timestamp)

    def test_instance_multiple_samples(self):
        timestamps = [
            datetime.datetime(2012, 7, 2, 10, 41),
            datetime.datetime(2012, 7, 2, 10, 42),
            datetime.datetime(2012, 7, 2, 10, 40),
        ]
        for timestamp in timestamps:
            datapoint = sample.Sample(
                'instance',
                'cumulative',
                '',
                1,
                'user-id',
                'project-id',
                'resource-id',
                timestamp=timestamp,
                resource_metadata={'display_name': 'test-server',
                                   'tag': 'self.sample-%s' % timestamp,
                                   },
                source='test',
            )
            msg = utils.meter_message_from_counter(
                datapoint,
                self.CONF.publisher.metering_secret,
            )
            self.conn.record_metering_data(msg)

        data = self.get_json('/resources')
        self.assertEqual(1, len(data))
        self._verify_sample_timestamps(data[0], timestamps[-1], timestamps[1])

    def test_instances_one(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id',
            timestamp=datetime.datetime(2012, 7, 2, 10, 40),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample',
                               },
            source='test',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        sample2 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id-alternate',
            timestamp=datetime.datetime(2012, 7, 2, 10, 41),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample2',
                               },
            source='test',
        )
        msg2 = utils.meter_message_from_counter(
            sample2,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg2)

        data = self.get_json('/resources/resource-id')
        self.assertEqual('resource-id', data['resource_id'])

    def test_with_source(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id',
            timestamp=datetime.datetime(2012, 7, 2, 10, 40),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample',
                               },
            source='test_list_resources',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        sample2 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id2',
            'project-id',
            'resource-id-alternate',
            timestamp=datetime.datetime(2012, 7, 2, 10, 41),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample2',
                               },
            source='not-test',
        )
        msg2 = utils.meter_message_from_counter(
            sample2,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg2)

        data = self.get_json('/resources', q=[{'field': 'source',
                                               'value': 'test_list_resources',
                                               }])
        ids = [r['resource_id'] for r in data]
        self.assertEqual(['resource-id'], ids)
        sources = [r['source'] for r in data]
        self.assertEqual(['test_list_resources'], sources)

    def test_with_invalid_resource_id(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id-1',
            timestamp=datetime.datetime(2012, 7, 2, 10, 40),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample',
                               },
            source='test_list_resources',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        sample2 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id2',
            'project-id',
            'resource-id-2',
            timestamp=datetime.datetime(2012, 7, 2, 10, 41),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample2',
                               },
            source='test_list_resources',
        )
        msg2 = utils.meter_message_from_counter(
            sample2,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg2)

        resp1 = self.get_json('/resources/resource-id-1')
        self.assertEqual("resource-id-1", resp1["resource_id"])

        resp2 = self.get_json('/resources/resource-id-2')
        self.assertEqual("resource-id-2", resp2["resource_id"])

        resp3 = self.get_json('/resources/resource-id-3', expect_errors=True)
        self.assertEqual(404, resp3.status_code)
        self.assertEqual("Resource resource-id-3 Not Found",
                         json.loads(resp3.body)['error_message']
                         ['faultstring'])

    def test_with_user(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id',
            timestamp=datetime.datetime(2012, 7, 2, 10, 40),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample',
                               },
            source='test_list_resources',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        sample2 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id2',
            'project-id',
            'resource-id-alternate',
            timestamp=datetime.datetime(2012, 7, 2, 10, 41),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample2',
                               },
            source='not-test',
        )
        msg2 = utils.meter_message_from_counter(
            sample2,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg2)

        data = self.get_json('/resources', q=[{'field': 'user_id',
                                               'value': 'user-id',
                                               }])
        ids = [r['resource_id'] for r in data]
        self.assertEqual(['resource-id'], ids)

    def test_with_project(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id',
            timestamp=datetime.datetime(2012, 7, 2, 10, 40),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample',
                               },
            source='test_list_resources',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        sample2 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id2',
            'project-id2',
            'resource-id-alternate',
            timestamp=datetime.datetime(2012, 7, 2, 10, 41),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample2',
                               },
            source='not-test',
        )
        msg2 = utils.meter_message_from_counter(
            sample2,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg2)

        data = self.get_json('/resources', q=[{'field': 'project_id',
                                               'value': 'project-id',
                                               }])
        ids = [r['resource_id'] for r in data]
        self.assertEqual(['resource-id'], ids)

    def test_with_user_non_admin(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id2',
            'project-id2',
            'resource-id-alternate',
            timestamp=datetime.datetime(2012, 7, 2, 10, 41),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample1',
                               },
            source='not-test',
        )
        msg2 = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg2)

        data = self.get_json('/resources',
                             headers={"X-Roles": "Member",
                                      "X-Project-Id": "project-id2"})
        ids = set(r['resource_id'] for r in data)
        self.assertEqual(set(['resource-id-alternate']), ids)

    def test_with_user_wrong_tenant(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id2',
            'project-id2',
            'resource-id-alternate',
            timestamp=datetime.datetime(2012, 7, 2, 10, 41),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample1',
                               },
            source='not-test',
        )
        msg2 = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg2)

        data = self.get_json('/resources',
                             headers={"X-Roles": "Member",
                                      "X-Project-Id": "project-wrong"})
        ids = set(r['resource_id'] for r in data)
        self.assertEqual(set(), ids)

    def test_metadata(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id',
            timestamp=datetime.datetime(2012, 7, 2, 10, 40),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample',
                               'dict_properties': {'key': 'value'},
                               'not_ignored_list': ['returned'],
                               },
            source='test',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        data = self.get_json('/resources')
        metadata = data[0]['metadata']
        self.assertEqual([(u'dict_properties.key', u'value'),
                          (u'display_name', u'test-server'),
                          (u'not_ignored_list', u"['returned']"),
                          (u'tag', u'self.sample')],
                         list(sorted(six.iteritems(metadata))))

    def test_resource_meter_links(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id',
            timestamp=datetime.datetime(2012, 7, 2, 10, 40),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample',
                               },
            source='test_list_resources',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        data = self.get_json('/resources')
        links = data[0]['links']
        self.assertEqual(2, len(links))
        self.assertEqual('self', links[0]['rel'])
        self.assertTrue((self.PATH_PREFIX + '/resources/resource-id')
                        in links[0]['href'])
        self.assertEqual('instance', links[1]['rel'])
        self.assertTrue((self.PATH_PREFIX + '/meters/instance?'
                         'q.field=resource_id&q.value=resource-id')
                        in links[1]['href'])

    def test_resource_skip_meter_links(self):
        sample1 = sample.Sample(
            'instance',
            'cumulative',
            '',
            1,
            'user-id',
            'project-id',
            'resource-id',
            timestamp=datetime.datetime(2012, 7, 2, 10, 40),
            resource_metadata={'display_name': 'test-server',
                               'tag': 'self.sample',
                               },
            source='test_list_resources',
        )
        msg = utils.meter_message_from_counter(
            sample1,
            self.CONF.publisher.metering_secret,
        )
        self.conn.record_metering_data(msg)

        data = self.get_json('/resources?meter_links=0')
        links = data[0]['links']
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['rel'], 'self')
        self.assertTrue((self.PATH_PREFIX + '/resources/resource-id')
                        in links[0]['href'])
