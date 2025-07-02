---
title: "Patents"
permalink: /patents/
author_profile: true
---

## US Patents

{% assign sorted_patents = site.patents | sort: 'date' %}
{% assign total = sorted_patents | size %}
{% for post in sorted_patents reversed %}
  {% assign num = total | minus: forloop.index0 %}
  {% include archive-single.html number=num %}
{% endfor %} 