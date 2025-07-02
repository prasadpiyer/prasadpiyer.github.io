---
layout: archive
title: "Lab Members"
permalink: /lab-members/
author_profile: true
---

### Current Members

{% assign members = site.data.lab_members.current | default: [] %}
{% if members == empty %}
<p><em>Create <code>_data/lab_members.yml</code> with sections <code>current</code> and <code>alumni</code>.  Sample format:</em></p>

```yaml
current:
  - name: "Dr. Jane Doe"
    role: "Post-doctoral Researcher"
    img: "lab/members/jane_doe.jpg"
    bio: "Ultrafast spectroscopy and machine-learning optimization of metasurfaces."
  - name: "John Smith"
    role: "Graduate Student"
    img: "lab/members/john_smith.jpg"
    bio: "Develops quantum-dot integrated metasurface emitters."

alumni:
  - name: "Alice Brown"
    role: "PhD 2023"
    now: "Optical Engineer at Acme Photonics"
    img: "lab/alumni/alice_brown.jpg"
```
{% endif %}

<div class="grid__wrapper">
{% for m in members %}
  <div class="grid__item" style="max-width:220px;margin:1rem;text-align:center">
    {% if m.img %}<img src="{{ '/images/' | append: m.img }}" alt="{{ m.name }}" style="width:100%;border-radius:50%" />{% endif %}
    <strong>{{ m.name }}</strong><br/>
    <em>{{ m.role }}</em>
    <p style="font-size:0.9em">{{ m.bio }}</p>
  </div>
{% endfor %}
</div>

---

### Alumni

{% assign alumni = site.data.lab_members.alumni | default: [] %}
<div class="grid__wrapper">
{% for m in alumni %}
  <div class="grid__item" style="max-width:220px;margin:1rem;text-align:center">
    {% if m.img %}<img src="{{ '/images/' | append: m.img }}" alt="{{ m.name }}" style="width:100%;border-radius:50%" />{% endif %}
    <strong>{{ m.name }}</strong><br/>
    <em>{{ m.role }}</em><br/>
    <span style="font-size:0.9em">{{ m.now }}</span>
  </div>
{% endfor %}
</div> 