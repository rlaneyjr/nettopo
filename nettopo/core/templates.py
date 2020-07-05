# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    templates.py

Jinja2 templates
'''

node_template = '''
<font point-size="10"><b>{{ node.name }}</b></font><br />
{{ node.ip }}<br />
{% if node.ios %}
    {{ node.ios }}<br />
{% endif %}
{% if node.plat %}
    {{ node.plat }}<br />
{% endif %}
{% if node.stack.enabled %}
    {% if config.diagram.expand_stackwise %}
        Switch {{ node.stack.num }} of {{ node.stack.count }}<br />
        Platform {{ node.stack.plat }} Serial {{ node.stack.serial }}<br />
        Role {{ node.stack.role }}<br />
    {% else %}
        {{ node.stack.serial }}<br />
    {% endif %}
{% elif node.vss.enabled %}
    {% if config.diagram.expand_vss %}
        VSS {{ node.vss.domain }}<br />
        VSS 0 - {{ node.vss.members[0].plat }} - {{ node.vss.members[0].serial }}<br />
        VSS 1 - {{ node.vss.members[1].plat }} - {{ node.vss.members[1].serial }}<br />
    {% else %}
        {{ node.vss.serial }}<br />
    {% endif %}
{% else %}
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
    Loopback {{ node.lo.name }} - {{ node.lo.ip }}<br />
{% endif %}
{% if node.svi %}
    VLAN {{ node.svi.vlan }} - {{ node.svi.ip }}<br />
{% endif %}
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
