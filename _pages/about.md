---
permalink: /
title: "Autonomous&nbsp;Nanophotonics&nbsp;Lab&nbsp;@&nbsp;CINT"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
carousel_images:
  - banner/cint-buildings.jpg
  - Lab/liquid_crystal_steering.png
  - Lab/Photonic_Ising.png
  - Lab/Quantum_Dot.png
  - Lab/ultrafast_setups.png
  - Lab/self-driving_lab_2.png

carousel_durations:
  - 12000
  - 4000
  - 4000
  - 4000
  - 4000
  - 4000

carousel_titles:
  - "CINT Facility"
  - "Liquid Crystal Steering"
  - "Photonic Ising Machine"
  - "Quantum Dot Platform"
  - "Ultrafast Spectroscopy Setups"
  - "Self-Driving Lab"
---

{% include lab-news-scroll.html %}

{% include carousel.html id="lab-carousel" images=page.carousel_images durations=page.carousel_durations titles=page.carousel_titles interval=4000 %}

## The Future of Discovery is Autonomous

What if scientific experiments could design, execute, and interpret themselves—discovering physical principles faster than any human could imagine? At the **Autonomous Nanophotonics Lab**, we're making this vision a reality.

We're pioneering a radical new paradigm where **artificial intelligence becomes the experimentalist**, autonomously navigating vast parameter spaces to uncover hidden physics, optimize exotic materials, and design photonic systems that harness light in ways never before possible.

### Our Approach: Where AI Meets Light

Machine learning doesn't just assist our research—it **drives discovery**. Our self-driving laboratories integrate:

* **Autonomous experimentation** at femtosecond timescales, where AI orchestrates ultrafast spectroscopy, structured light patterns, and nanofabrication to reveal emergent light–matter interactions invisible to traditional methods
* **Interpretable discovery engines** that don't just optimize—they extract human-readable physical laws from high-dimensional experimental data, turning black-box results into actionable scientific insight  
* **Reconfigurable photonic hardware** spanning quantum emitters, liquid-crystal metasurfaces, and photonic Ising machines that compute at the speed of light with energy efficiencies orders of magnitude beyond electronics

### From Quantum Dots to Next-Gen Computing

Our discoveries are enabling transformative technologies:

* **Quantum information systems** with deterministic single-photon sources precisely controlled at the nanoscale
* **Ultrafast optical computing** performing complex optimization and AI inference entirely with photons
* **Intelligent LiDAR and imaging** using electrically reconfigurable metasurfaces for autonomous vehicles and AR/VR
* **Self-driving scientific instruments** openly available to the global research community through the *Center for Integrated Nanotechnologies (CINT)*

### Join the Revolution

Whether you're a **prospective student** seeking to shape the future of science, a **CINT user** looking to supercharge your research with autonomous tools, or an **industry partner** ready to translate breakthrough physics into transformative products—we invite you to collaborate with us.

**The age of human-limited discovery is transforming into the autonomous era.**

## Highlighted Publications

{% comment %} Assign highlighted papers {% endcomment %}
{% assign autoSci = site.publications | where: "title", "AutoSciLab: A Self-Driving Laboratory For Interpretable Scientific Discovery" | first %}
{% assign autoSciTalk = site.talks | where: "title", "AutoSciLab: A Self-Driving Laboratory For Interpretable Scientific Discovery" | first %}
{% assign beamSteer = site.publications | where: "title", "Sub-picosecond steering of ultrafast incoherent emission from semiconductor metasurfaces" | first %}
{% assign sdl = site.publications | where: "title", "Self-driving lab discovers principles for steering spontaneous emission" | first %}

<div class="publications-cards">
  <div class="publication-card">
    <h3><a href="{{ autoSciTalk.url | relative_url }}">{{ autoSciTalk.title }}</a></h3>
    <p class="archive__item-authors">{{ autoSciTalk.authors }}</p>
    <p><em>{{ autoSciTalk.venue }}</em>, {{ autoSciTalk.date | date: '%Y' }}</p>
  </div>

  <div class="publication-card">
    <h3><a href="{{ beamSteer.url | relative_url }}">{{ beamSteer.title }}</a></h3>
    <p class="archive__item-authors">{{ beamSteer.authors }}</p>
    <p><em>{{ beamSteer.venue }}</em>, {{ beamSteer.date | date: '%Y' }}</p>
  </div>

  <div class="publication-card">
    <h3><a href="{{ sdl.url | relative_url }}">{{ sdl.title }}</a></h3>
    <p class="archive__item-authors">{{ sdl.authors }}</p>
    <p><em>{{ sdl.venue }}</em>, {{ sdl.date | date: '%Y' }}</p>
  </div>
</div>
