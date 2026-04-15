---
name: slides
description: Presentation design with McKinsey-style high-density slides. Create professional PPTX presentations with data visualization, clear messaging, and strategic storytelling.
---

# Slides Skill

## Core Principles

1. **Every slide must have a clear takeaway message** — The audience should immediately understand the point
2. **Use data visualization over bullet points** — Charts and graphs communicate faster than text
3. **Maintain consistent visual hierarchy** — Title, subtitle, content, notes follow strict layout rules
4. **Situation-Complication-Resolution framework** — Structure narratives for maximum impact

## Design Standards

### Slide Layouts
- **Title slide**: Large headline, subtitle, optional background image
- **Content slide**: Headline + 2-3 key points with visual support
- **Data slide**: Chart/graph with minimal supporting text
- **Divider slide**: Section headers with bold typography

### Color Schemes
- **Corporate**: Dark blue primary, white/gray secondary
- **Tech**: Dark background, accent colors (cyan, purple)
- **Minimalist**: Black/white with single accent

### Typography
- Headlines: 36-44pt, bold
- Body: 18-24pt, regular
- Captions: 14-16pt, light

## Tool Usage

Use `create_slides` tool with structured data:

```json
{
  "slides": [
    {"title": "Executive Summary", "content": "Key findings...", "notes": "Speaker notes here"},
    {"title": "Market Analysis", "content": "Data points...", "layout": "data"}
  ],
  "theme": "corporate",
  "output_path": "/mnt/workspace/output/presentation.pptx"
}
```

## Quality Checklist

- [ ] Every slide has a clear message
- [ ] Data is visualized, not listed
- [ ] Consistent fonts and colors
- [ ] Speaker notes added for detail
- [ ] Logical flow between slides
