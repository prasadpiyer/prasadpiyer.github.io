---
title: "Patents"
permalink: /patents/
author_profile: true
---

## US Patents

{% assign sorted_patents = site.patents | sort: 'date' | reverse %}
{% assign pcount = sorted_patents | size %}
{% for post in sorted_patents %}
  {% include archive-single.html number=pcount-forloop.index0 %}
{% endfor %} 