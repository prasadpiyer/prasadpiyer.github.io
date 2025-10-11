---
layout: archive
title: "Lab Members"
permalink: /lab-members/
author_profile: false
---

### Current Members

{% assign members = site.data.lab_members.current | default: [] %}
{% if members == empty %}
<p><em>Create <code>_data/lab_members.yml</code> with sections <code>current</code> and <code>alumni</code>.  Sample format:</em></p>

```yaml
current:
  - name: "Dr. Chris Arose"
    role: "Post-doctoral Researcher"
    img: "lab/members/jane_doe.jpg"
    bio: "Ultrafast spectroscopy and machine-learning optimization of metasurfaces."
  - name: "Aditya Choudhary"
    role:  "Post-doctoral Researcher"
    img: "lab/members/john_smith.jpg"
    bio: "Develops quantum-dot integrated metasurface emitters."
  - name: "Sanghyeok Park"
    role: "Post-doctoral Researcher"
    img: "lab/members/john_smith.jpg"
    bio: "Develops quantum-dot integrated metasurface emitters."
  - name: "Emmanuele Caddedu"
    role: "Graduate Student"
    img: "lab/members/john_smith.jpg"
    bio: "Develops quantum-dot integrated metasurface emitters."

alumni:
  - name: "Hyosim Yang"
    role: "Post Doctoral Appointee"
    now: "Optical Engineer at Acme Photonics"
    img: "lab/alumni/alice_brown.jpg"
  - name: "Tomas Santiago"
    role: "Post Doctoral Appointee"
    now: "Optical Engineer at Acme Photonics"
    img: "lab/alumni/alice_brown.jpg"
  - name: "Hyunseung Jung"
    role: "Post Doctoral Appointee"
    now: "Optical Engineer at Acme Photonics"
    img: "lab/alumni/alice_brown.jpg"
  - name: "Saaketh Desai"
    role: "Post Doctoral Appointee"
    now: "Optical Engineer at Acme Photonics"
    img: "lab/alumni/alice_brown.jpg"
  
```
{% endif %}

<div class="grid__wrapper" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 2rem; justify-items: start;">
{% for m in members %}
  <div class="grid__item" style="width:220px;text-align:center">
    {% if m.img %}<img src="{{ '/images/' | append: m.img }}" alt="{{ m.name }}" style="width:100%;height:220px;object-fit:cover;border-radius:50%" />{% endif %}
    <strong>{% if m.url and m.url != "" %}<a href="{{ m.url }}" target="_blank">{{ m.name }}</a>{% else %}{{ m.name }}{% endif %}</strong><br/>
    <em>{{ m.role }}</em>
    <p style="font-size:0.9em">{{ m.bio }}</p>
  </div>
{% endfor %}
</div>

---

### Users/Collaborators

{% assign users = site.data.lab_members.users | default: [] %}
<table style="margin: 0 auto; border-collapse: separate; border-spacing: 2rem;">
{% for m in users %}
  {% assign mod = forloop.index0 | modulo: 3 %}
  {% if mod == 0 %}<tr>{% endif %}
    <td style="width:220px;text-align:center;vertical-align:top">
      {% if m.img %}<img src="{{ '/images/' | append: m.img }}" alt="{{ m.name }}" style="width:100%;height:220px;object-fit:cover;border-radius:50%" />{% endif %}
      <strong>{% if m.url and m.url != "" %}<a href="{{ m.url }}" target="_blank">{{ m.name }}</a>{% else %}{{ m.name }}{% endif %}</strong><br/>
      <em>{{ m.role }}</em>
      <p style="font-size:0.9em">{{ m.bio }}</p>
    </td>
  {% if mod == 2 or forloop.last %}</tr>{% endif %}
{% endfor %}
</table>

---

### Industrial Collaborators

{% assign industrial = site.data.lab_members.industrial | default: [] %}
<div class="grid__wrapper" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 2rem; justify-items: start;">
{% for m in industrial %}
  <div class="grid__item" style="width:220px;text-align:center">
    {% if m.img %}{% if m.url and m.url != "" %}<a href="{{ m.url }}" target="_blank">{% endif %}<img src="{{ '/images/' | append: m.img }}" alt="{{ m.name }}" style="max-width:150px;height:80px;object-fit:contain;border-radius:10px" />{% if m.url and m.url != "" %}</a>{% endif %}{% endif %}
    <strong>{% if m.url and m.url != "" %}<a href="{{ m.url }}" target="_blank">{{ m.name }}</a>{% else %}{{ m.name }}{% endif %}</strong><br/>
    <p style="font-size:0.9em">{{ m.bio }}</p>
  </div>
{% endfor %}
</div>

---

### Alumni

{% assign alumni = site.data.lab_members.alumni | default: [] %}
<div class="grid__wrapper" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 2rem;">
{% for m in alumni %}
  <div class="grid__item" style="width:220px;text-align:center">
    {% if m.img %}<img src="{{ '/images/' | append: m.img }}" alt="{{ m.name }}" style="width:100%;height:220px;object-fit:cover;border-radius:50%" />{% endif %}
    <strong>{% if m.url and m.url != "" %}<a href="{{ m.url }}" target="_blank">{{ m.name }}</a>{% else %}{{ m.name }}{% endif %}</strong><br/>
    <em>{{ m.role }}</em><br/>
    <span style="font-size:0.9em">{{ m.now }}</span>
  </div>
{% endfor %}
</div> 