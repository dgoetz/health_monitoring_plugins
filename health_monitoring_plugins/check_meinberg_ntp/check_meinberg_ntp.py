#!/usr/bin/env python
# check_meinberg_ntp.py - Monitor the Meinberg NTP Server M300.

# Copyright (C) 2016-2018 rsmuc <rsmuc@mailbox.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with check_meinberg_ntp.py.  If not, see <http://www.gnu.org/licenses/>.

from pynag.Plugins import ok
import health_monitoring_plugins.meinberg

if __name__ == "__main__":
    # pylint: disable=C0103
    helper = health_monitoring_plugins.SnmpHelper()
    helper.parser.add_option('-m',
                             help="Version of the Firmware (v5 or NG) "
                                  "(NG = MBG-LANTIME-NG-MIB.mib used in Firmware 6 and newer)",
                             dest="mibversion")
    helper.parse_arguments()
    sess = health_monitoring_plugins.SnmpSession(**helper.get_snmp_args())

    # we need to increase the default timeout. the snmp session takes too long.
    helper.options.timeout = max(helper.options.timeout, 2000)

    # The default return value should be always OK
    helper.status(ok)

    meinberg = health_monitoring_plugins.meinberg.Meinberg(sess, helper.options.mibversion)

    # GPSPosition

    snmp_result = helper.get_snmp_value(sess, helper, meinberg.oids['oid_gps_position'])
    meinberg.check_gps_position(helper, snmp_result)

    # NTP Status
    snmp_result = helper.get_snmp_value(sess, helper, meinberg.oids['oid_ntp_current_state_int'])
    helper.update_status(helper, meinberg.check_ntp_status(snmp_result))

    # GPS Status
    snmp_result = helper.get_snmp_value(sess, helper, meinberg.oids['oid_gps_mode_int'])
    helper.update_status(helper, meinberg.check_gps_status(snmp_result))

    # Satellites
    snmp_result = helper.get_snmp_value(sess, helper, meinberg.oids['oid_gps_satellites_good'])
    meinberg.check_satellites(helper, snmp_result)

    # there is only the satellites metric, but we will check all available
    helper.check_all_metrics()

    # Print out plugin information and exit nagios-style
    helper.exit()
