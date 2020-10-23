# -*- coding: utf-8 -*-
# @File  : utils.py

from pyzabbix import ZabbixAPI, ZabbixAPIException
import sys


class Zabbix(object):

    def __init__(self):
        ZABBIX_SERVER = 'http://10.1.1.110:8080'
        zapi = ZabbixAPI(ZABBIX_SERVER)
        zapi.login('Admin', 'zabbix')
        self.zapi = zapi

    def get_hosts(self, host):
        # 获取主机
        host_list = self.zapi.host.get(
            output=['hostid', 'name', 'host'],
            # search={'host': host}
        )
        return host_list

    def add_host(self, ip, group_ids, template_ids, port=10050, dns='', useip=1, main=1, type=1):
        # 添加主机监控
        interfaces = {
            "type": type,
            "main": main,
            "useip": useip,
            "ip": ip,
            "dns": dns,
            "port": port
        }
        if type == 2:
            interfaces['details'] = {
                'version': 2,
                'community': '{$SNMP_COMMUNITY}'
            }
        if not template_ids[0]['templateid']:
            template_ids = [{}]
        data = self.zapi.host.create(
            host=ip,
            interfaces=[interfaces],
            groups=group_ids,
            templates=template_ids
        )
        return data

    def get_hostgroups(self, name):
        # 获取主机群组
        hostgroups = self.zapi.hostgroup.get(
            output='extend',
            filter={
                'name': name
            }
        )
        return hostgroups

    def add_hostgroups(self, name):
        # 添加主机群组
        hostgroups = self.zapi.hostgroup.create(
            name=name
        )
        return hostgroups

    def get_templates(self, name):
        # 获取主机群组
        templates = self.zapi.template.get(
            output="extend",
            filter={
                "name": name
            }
        )
        return templates

    def add_item(self, host):
        # 添加监控项
        hosts = self.zapi.host.get(filter={"host": host}, selectInterfaces=["interfaceid"])
        if hosts:
            host_id = hosts[0]["hostid"]
            print("Found host id {0}".format(host_id))

            try:
                item = self.zapi.item.create(
                    hostid=host_id,
                    name='Used disk space on $1 in %',
                    key_='vfs.fs.size[/,pused]',
                    type=0,
                    value_type=3,
                    interfaceid=hosts[0]["interfaces"][0]["interfaceid"],
                    delay=30
                )
            except ZabbixAPIException as e:
                print(e)
                sys.exit()
            print("Added item with itemid {0} to host: ".format(item["itemids"][0]))
        else:
            print("No hosts found")

    def add_maintenance(self, name, active_since, active_till, groupids, hostids, timeperiods, description):
        # 创建维护期
        # timeperiod_type 时间周期类型
        # 0 - (default)one time only;
        # 2 - daily;
        # 3 - weekly;
        # 4 - monthly.
        # start_time 一天内维护模式开始的时刻
        # period 维护模式周期的时间（秒）
        # dayofweek 维护模式生效的周次
        # every 对于天或者周的周期every定义维护模式生效的天或者周间隔
        # active_since 维护模式生效的时刻
        # active_till 维护模式失效的时刻
        # name 维护模式的名称
        # groupids 要执行维护模式的主机组IDs
        # timeperiods 维护模式时间周期
        maintenance = self.zapi.maintenance.create(
            name=name,
            active_since=active_since,
            active_till=active_till,
            groupids=groupids,
            hostids=hostids,
            timeperiods=timeperiods,
            description=description
        )
        return maintenance

    def get_triggers(self, groupids=None, hostids=None):
        # 获取触发器标记
        params = {
            'output': ['triggerid', 'description']
        }
        if groupids:
            params['groupids'] = groupids.split(',')
        if hostids:
            params['hostids'] = hostids.split(',')
        result = self.zapi.trigger.get(**params)
        return result

    def update_triggers(self, triggerid, tag, value):

        # 更新触发器
        success_ids = []
        fail_ids = []

        try:
            self.zapi.trigger.update(
                triggerid=triggerid,
                tags=[
                    {
                        'tag': tag,
                        'value': value
                    }
                ]
            )
            success_ids.append(triggerid)
        except  Exception:
            fail_ids.append(triggerid)
        return success_ids, fail_ids


def time_to_stamp(date_time):
    # 时间转为时间戳
    import time
    a_time = time.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    return int(time.mktime(a_time))
if __name__ == '__main__':
    api = Zabbix()
    a = api.get_hosts("a")
    print(a)