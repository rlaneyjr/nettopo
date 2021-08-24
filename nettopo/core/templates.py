# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
    templates.py

Jinja2 templates
"""
from jinja2 import BaseLoader, TemplateNotFound
from jinja2.environment import Template
from jinja2.nativetypes import NativeEnvironment
from typing import Optional, Any

credits_template = """
<table border=0>
  <tr>
    <td balign=right>
      <font point-size={{ title_text_size }}><b>{{ title }}</b></font><br />
      <font point-size={{ date_text_size }}>{{ today }}</font><br />
    </td>
  </tr>
</table>
"""

node_template = """
<font point-size="10"><b>{{ node.name }}</b></font><br />
{{ node.ip }}<br />
{% if node.ios %}
    {{ node.ios }}<br />
{% endif %}
{% if node.stack %}
    {% if config.expand_stackwise and config.get_stack_members %}
        {% for member in node.stack.members %}
            Switch {{ member.stack.num }} of {{ member.stack.count }}<br />
            Platform {{ member.stack.plat }} Serial {{ member.stack.serial }}<br />
            Role {{ member.stack.role }}<br />
        {% endfor %}
    {% else %}
        {{ node.stack.serial }}<br />
    {% endif %}
{% elif node.vss %}
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
"""

link_template = """
{% if node.vpc and node.vpc.ifname == link.local_port %}
    VPC<br />
{% endif %}
{% if link.local_port %}
    Local Port: {{ link.local_port }}<br />
{% endif %}
{% if link.remote_port %}
    Remote Port: {{ link.remote_port }}<br />
{% endif %}
{% if link.local_if_ip %}
    Local IP: {{ link.local_if_ip }}<br />
{% endif %}
{% if link.remote_if_ip %}
    Remote IP: {{ link.remote_if_ip }}<br />
{% endif %}
"""

template_mapper = {
    'credits': credits_template,
    'node': node_template,
    'link': link_template,
}

class MyTemplateLoader(BaseLoader):
    def __init__(self) -> None:
        self.template_mapper = template_mapper

    def get_source(self, environment, template):
        source = self.template_mapper.get(template)
        if not source:
            raise TemplateNotFound(f"Template {template} not found")
        return source, None, False


def load_template(kind: str, template: str) -> Any:
    # Create a new instancve of our MyTemplateLoader class
    temp_loader = MyTemplateLoader()
    env = NativeEnvironment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=temp_loader,
    )
    return env.get_template(template)
