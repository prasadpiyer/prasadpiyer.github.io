---
layout: archive
title: "Lab Capabilities"
permalink: /lab-capabilities/
author_profile: false
---

Below is a snapshot of our experimental setups available in our lab. Click each image to enlarge.

<div style="background: #e6f3ff; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #4299e1;">
  <p style="margin: 0;"><strong>🔬 Looking for detailed instrument specifications?</strong> Visit our <a href="/lab-instruments/">Lab Instruments</a> page for a comprehensive list of available equipment and technical specifications.</p>
</div>

<!-- Lab Capabilities collection render -->
{% assign caps = site.lab_capabilities | sort: 'date' %}
<div class="lab-projects">
  <div class="lab-projects__grid">
    {% for cap in caps %}
      <article class="lab-project-card">
        <header class="lab-project-card__header">
          <h2 id="{{ cap.slug }}" class="lab-project-card__title">{{ cap.title }}</h2>
        </header>
        {% if cap.images %}
          {% include carousel.html id=cap.slug images=cap.images interval=5000 %}
        {% endif %}
        <div class="lab-project-card__body">
          {% if cap.summary %}
            <p class="lab-project-card__desc">{{ cap.summary }}</p>
          {% endif %}
          <p><a href="{{ cap.url }}" class="btn btn--primary">View Detailed Capabilities →</a></p>
        </div>
      </article>
    {% endfor %}
  </div>
</div>
