---
layout: archive
title: "Lab Capabilities"
permalink: /lab-capabilities/
author_profile: true
---

Below is a snapshot of the key experimental setups available in our lab.  Click each image to enlarge.

{% assign setups = site.data.lab_capabilities | default: [] %}
{% if setups == empty %}
<p><em>Upload your setup images to <code>images/lab/capabilities/</code> and describe them in <code>_data/lab_capabilities.yml</code>.  A sample entry is provided below.</em></p>

```yaml
# _data/lab_capabilities.yml
- title: "Ultrafast Pump–Probe Spectroscopy Station"
  img: "lab/capabilities/pump_probe.jpg"
  description: "Femtosecond Ti:Sapphire laser (35 fs, 1 kHz) with optical delay line for transient absorption and reflection measurements."
- title: "Fourier-Space Imaging Microscope"
  img: "lab/capabilities/fourier_imaging.jpg"
  description: "Custom microscope to measure angle-resolved emission and scattering from metasurfaces across 400–1700 nm."
```

Once the YAML file and images are in place this page will populate automatically.
{% endif %}

<div class="grid__wrapper">
{% for s in setups %}
  <div class="grid__item" style="max-width:320px;margin:1rem">
    <a href="{{ '/images/' | append: s.img }}" target="_blank">
      <img src="{{ '/images/' | append: s.img }}" alt="{{ s.title }}" style="width:100%" />
    </a>
    <h4 style="margin:0.5rem 0 0">{{ s.title }}</h4>
    <p>{{ s.description }}</p>
  </div>
{% endfor %}
</div> 