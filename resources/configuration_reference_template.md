# Configuration values reference


| Property | Type | Default value | Description |
| -------- | ---- | ------------- | ----------- |
{% for property in properties -%}
|{{ property.name }}|{{ property.type_ref }}|{{ property.default }}|{{ property.description }}|
{% endfor %}
