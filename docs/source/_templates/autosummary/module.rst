{{ fullname  | escape | underline}}

.. currentmodule:: {{ fullname }}

.. automodule:: {{ fullname }}
   :members:
   :undoc-members:
   :special-members:

{% block modules %}
{% if modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
{% for item in modules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}