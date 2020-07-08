# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    templates.py

Jinja2 templates
'''

credits_template = '''
<table border=0>
  <tr>
    <td balign=right>
      <font point-size={{ title_text_size }}><b>{{ title }}</b></font><br />
      <font point-size={{ date_text_size }}>{{ today }}</font><br />
    </td>
  </tr>
</table>
'''

node_template = '''
<font point-size="10"><b>{{ node.name }}</b></font><br />
{{ node.get_ipaddr() }}<br />
{% if node.ios %}
    {{ node.ios }}<br />
{% endif %}
{% if node.stack.enabled %}
    {% if config.expand_stackwise and config.get_stack_members %}
        {% for member in node.stack.members %}
            Switch {{ member.stack.num }} of {{ member.stack.count }}<br />
            Platform {{ member.stack.plat }} Serial {{ member.stack.serial }}<br />
            Role {{ member.stack.role }}<br />
        {% endfor %}
    {% else %}
        {{ node.stack.serial }}<br />
    {% endif %}
{% elif node.vss.enabled %}
    {% if config.expand_vss %}
        VSS {{ node.vss.domain }}<br />
        VSS 0 - {{ node.vss.members[0].plat }} - {{ node.vss.members[0].serial }}<br />
        VSS 1 - {{ node.vss.members[1].plat }} - {{ node.vss.members[1].serial }}<br />
    {% else %}
        {{ node.vss.serial }}<br />
    {% endif %}
{% else %}
    {% if node.plat %}
        {{ node.plat }}<br />
    {% endif %}
    {% if node.serial %}
        {{ node.serial }}<br />
    {% endif %}
{% endif %}
{% if node.bgp_las %}
    BGP {{ node.bgp_las }}<br />
{% endif %}
{% if node.ospf_id %}
    OSPF {{ node.ospf_id }}<br />
{% endif %}
{% if node.hsrp_pri %}
    HSRP VIP {{ node.hsrp_vip }}<br />
    HSRP Pri {{ node.hsrp_pri }}<br />
{% endif %}
{% if node.lo %}
    {% for lo in node.loopbacks %}
        Loopback {{ lo.name }} - {{ lo.ip }}<br />
    {% endfor %}
{% endif %}
{% if node.svi %}
    {% for svi in node.svis %}
        VLAN {{ svi.vlan }} - {{ svi.ip }}<br />
    {% endfor %}
{% endif %}
'''

link_template = '''
{% if node.vpc_peerlink_if in [link.local_port, link.local_lag] %}
    VPC<br />
{% endif %}
{% if is_lag %}
    LAG<br />
    {{ lag_members }} Members<br />
{% else %}
    Local: {{ link.local_port }}<br />
    Remote: {{ link.remote_port }}<br />
{% endif %}
{% if is_lag %}
    {% if link.local_lag != 'UNKNOWN' %}
        LAG Member<br />
        {% if link.local_lag_ips and link.remote_lag_ips %}
            Local: {{ link.local_lag }} - {{ link.local_lag_ips[0] }}<br />
            Remote: {{ link.remote_lag }} - {{ link.remote_lag_ips[0] }}<br />
        {% else %}
            Local: {{ link.local_lag }} | Remote: {{ link.remote_lag }}<br />
        {% endif %}
    {% endif %}
    {% if link.local_if_ip and link.local_if_ip != 'UNKNOWN' %}
        Local: {{ link.local_if_ip }}<br />
    {% endif %}
    {% if link.remote_if_ip and link.remote_if_ip != 'UNKNOWN' %}
        Remote: {{ link.remote_if_ip }}<br />
    {% endif %}
{% else %}
    {% for lnk in node.links %}
        {% if lnk.local_lag == link.local_lag %}
            Local: {{ l.local_port }} | Remote: {{ l.remote_port }}"
        {% endif %}
    {% endfor %}
    {% if link.local_lag_ips and link.remote_lag_ips %}
        Local: {{ link.local_lag }} - {{ link.local_lag_ips[0] }}<br />
        Remote: {{ link.remote_lag }} - {{ link.remote_lag_ips[0] }}<br />
    {% else %}
        Local: {{ link.local_lag }} | Remote: {{ link.remote_lag }}<br />
    {% endif %}
{% endif %}
{% if link.link_type == '1' %}
    TRUNK<br />
    {% if link.local_native_vlan == link.remote_native_vlan %}
        Native Match: {{ link.local_native_vlan }}<br />
    {% elif not link.remote_native_vlan %}
        Native Local: {{ link.local_native_vlan }} Remote: None<br />
    {% else %}
        Native Local: {{ link.local_native_vlan }} Remote: {{ link.remote_native_vlan }}<br />
    {% endif %}
    {% if link.local_allowed_vlans == link.remote_allowed_vlans %}
        Allowed Match: {{ link.local_allowed_vlans }}<br />
    {% else %}
        Allowed Local: {{ link.local_allowed_vlans }}<br />
        {% if link.remote_allowed_vlans %}
            Allowed Remote: {{ link.remote_allowed_vlans }}<br />
        {% endif %}
    {% endif %}
{% elif not link.link_type %}
    ROUTED<br />
{% else %}
    SWITCHED<br />
    {% if link.vlan %}
        VLAN {{ link.vlan }}<br />
    {% endif %}
{% endif %}
'''
