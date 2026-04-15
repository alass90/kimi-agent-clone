---
name: data_analysis
description: Data analysis, visualization, and statistical modeling. Use Python with pandas, numpy, matplotlib, scipy for comprehensive data work.
---

# Data Analysis Skill

## Core Capabilities

1. **Data Loading & Cleaning** — Handle CSV, Excel, JSON, SQL sources
2. **Statistical Analysis** — Descriptive stats, hypothesis testing, correlations
3. **Visualization** — Charts, graphs, interactive plots
4. **Modeling** — Regression, classification, clustering

## Tool Usage

Use `ipython` tool for all data analysis work:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('/mnt/workspace/upload/data.csv')

# Analyze
print(df.describe())

# Visualize
plt.figure(figsize=(10, 6))
df['column'].hist()
plt.savefig('/mnt/workspace/output/chart.png')
```

## Common Patterns

### Exploratory Data Analysis
```python
# Quick overview
df.info()
df.isnull().sum()
df.describe()

# Distributions
df.hist(figsize=(12, 8))
```

### Correlation Analysis
```python
import seaborn as sns
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
```

### Time Series
```python
df['date'] = pd.to_datetime(df['date'])
df.set_index('date').plot()
```

## Output Standards

- Save all charts to `/mnt/workspace/output/`
- Use `plt.tight_layout()` before saving
- Set `dpi=150` for print quality
- Include titles, labels, legends
