# Query Clustering CLI - User Guide

## Overview

The Query Clustering CLI is a command-line tool for batch processing CSV files containing queries and performing topic clustering analysis. It automatically generates multiple CSV output files with clustering results, topic information, and statistics.

## Installation

```bash
# Install query-clustering package
uv add query-clustering

# Or update if already installed
uv sync --package query-clustering
```

## Quick Start

### 1. Prepare Your CSV File

Create a CSV file with at least a `query` column. Optional columns include `category` and `language`.

**Example: queries.csv**
```csv
query,category,language
北京天气怎么样,旅游出行,中文
flights to paris,travel,英文
iPhone 15价格,电商购物,中文
how to learn Python,education,英文
```

### 2. Run Clustering

```bash
# Basic clustering
query-clustering queries.csv

# With output directory
query-clustering queries.csv --output-dir ./results

# Filter and verbose mode
query-clustering queries.csv --output-dir ./results --language 中文 -v
```

### 3. Check Results

The tool generates 4 CSV files in the output directory:

```
results/
├── clustered_queries.csv       # Main results with topic assignments
├── topic_info.csv              # Topic metadata
├── topic_summaries.csv         # Topic keywords and samples
└── statistics.csv              # Dataset statistics
```

## Command Line Options

### Basic Options

```bash
query-clustering INPUT_FILE [OPTIONS]
```

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output-dir` | `-o` | Output directory path | `./clustering_results` |
| `--verbose` | `-v` | Enable detailed output | Disabled |
| `--help` | `-h` | Show help message | - |

### Filtering Options

```bash
# Filter by language
query-clustering data.csv --language 中文

# Filter by category
query-clustering data.csv --category 旅游出行

# Random sample
query-clustering data.csv --sample 500

# Limit number of queries
query-clustering data.csv --limit 1000
```

### Clustering Options

```bash
# Use Ollama embedder (faster)
query-clustering data.csv --embedder-type ollama

# Minimum documents per topic
query-clustering data.csv --min-topic-size 5
```

## Common Usage Examples

### Example 1: Basic Clustering

```bash
query-clustering myqueries.csv --output-dir ./analysis
```

**When to use:** Quick clustering with default settings on all queries.

### Example 2: Language-Specific Analysis

```bash
# Cluster only Chinese queries
query-clustering myqueries.csv --language 中文 -o ./chinese_analysis

# Cluster only English queries
query-clustering myqueries.csv --language 英文 -o ./english_analysis
```

**When to use:** Analyze different language queries separately for better topic coherence.

### Example 3: Category-Focused Analysis

```bash
query-clustering sales_data.csv --category 旅游出行 -o ./travel_analysis
```

**When to use:** Focus on queries from specific business categories or domains.

### Example 4: Sampling Large Datasets

```bash
# Sample 1000 random queries for quick testing
query-clustering large_dataset.csv --sample 1000 -o ./sample_results -v

# Then process full dataset if satisfied
query-clustering large_dataset.csv -o ./full_results
```

**When to use:** Test parameters on a subset before processing large files.

### Example 5: Verbose Mode for Debugging

```bash
query-clustering data.csv -o ./results -v
```

Output includes:
- Loading progress
- Data filtering steps
- Clustering model initialization
- Topic discovery information
- File saving confirmation

### Example 6: Multiple Filters Combined

```bash
query-clustering data.csv \
  --language 中文 \
  --category 教育学习 \
  --sample 500 \
  --output-dir ./edu_results \
  -v
```

**When to use:** Complex analysis with multiple constraints.

## Output Files Explanation

### 1. clustered_queries.csv

**Main clustering results file.**

| Column | Description |
|--------|-------------|
| `query` | Original query string |
| `topic_id` | Assigned topic ID (-1 = noise/unclassified) |
| `topic_probability` | Confidence score (0.0-1.0) |

**Example:**
```
query,topic_id,topic_probability
北京天气怎么样,5,0.95
flights to paris,12,0.88
iPhone 15价格,-1,0.0
```

### 2. topic_info.csv

**Topic metadata and BERTopic information.**

Contains topic IDs, document counts, and BERTopic-generated topic names.

### 3. topic_summaries.csv

**Human-readable topic summaries.**

| Column | Description |
|--------|-------------|
| `topic_id` | Topic identifier |
| `keywords` | Top 10 keywords for the topic (comma-separated) |
| `document_count` | Number of queries assigned to this topic |
| `sample_documents` | 3 representative sample queries |

**Example:**
```
topic_id,keywords,document_count,sample_documents
5,"weather, forecast, temperature, beijing, today, tomorrow",124,"北京天气怎么样 | 北京明天下雨吗 | 北京温度预报"
```

### 4. statistics.csv

**Dataset statistics and summary metrics.**

| Metric | Description |
|--------|-------------|
| `Total Queries` | Total number of queries processed |
| `Unique Queries` | Number of unique queries (deduplication) |
| `Number of Topics` | Topics discovered (excluding noise) |
| `Queries with Topics` | Successfully classified queries |
| `Noise Queries` | Queries without clear topic (-1) |

## Tips for Better Results

### 1. Data Quality

- **Clean your data:** Remove duplicates, URLs, and special characters
- **Consistent format:** Ensure CSV is properly formatted with headers
- **Sufficient data:** At least 200-300 queries recommended for good results

### 2. Language Separation

```bash
# Better: Separate by language
query-clustering data.csv --language 中文 -o ./cn_results
query-clustering data.csv --language 英文 -o ./en_results

# Instead of: All languages mixed
query-clustering data.csv -o ./mixed_results
```

### 3. Category Analysis

```bash
# Better: Process by business category
query-clustering data.csv --category 电商购物 -o ./shopping
query-clustering data.csv --category 旅游出行 -o ./travel

# Instead of: All categories mixed
query-clustering data.csv -o ./all_categories
```

### 4. Embedder Selection

```bash
# For speed (if Ollama is available)
query-clustering data.csv --embedder-type ollama

# For accuracy (default)
query-clustering data.csv --embedder-type sentence-transformer
```

### 5. Topic Size Control

```bash
# More conservative clustering (fewer, larger topics)
query-clustering data.csv --min-topic-size 10

# More granular clustering (more, smaller topics)
query-clustering data.csv --min-topic-size 3
```

## Troubleshooting

### Error: "After pruning, no terms remain"

**Cause:** Too few queries or too much preprocessing.

**Solutions:**
```bash
# Use more queries
query-clustering data.csv --limit 1000

# Or increase sample size
query-clustering data.csv --sample 500
```

### Error: "File not found"

**Cause:** Incorrect file path.

**Solutions:**
```bash
# Use absolute path
query-clustering /full/path/to/queries.csv

# Or relative path from current directory
query-clustering ./data/queries.csv
```

### Error: "No queries available after filtering"

**Cause:** Filter criteria too restrictive.

**Solutions:**
```bash
# Check available values
# Remove --language filter
query-clustering data.csv --category 旅游出行

# Use --verbose to see filtering steps
query-clustering data.csv --language 中文 -v
```

### Slow Processing

**Solutions:**
```bash
# Use faster embedder
query-clustering data.csv --embedder-type ollama -o ./results

# Process subset first
query-clustering data.csv --sample 1000 -o ./results

# Reduce query limit
query-clustering data.csv --limit 2000 -o ./results
```

## Workflow Examples

### Marketing Analysis Workflow

```bash
# 1. Analyze customer search queries by category
query-clustering customer_queries.csv --category 电商购物 -o ./shopping_analysis -v

# 2. Review topic_summaries.csv to understand search intent
cat ./shopping_analysis/topic_summaries.csv

# 3. Use topic assignments for campaign targeting
cut -d',' -f1,2 ./shopping_analysis/clustered_queries.csv > topic_mapping.csv
```

### Product Development Workflow

```bash
# 1. Cluster feature requests by language
query-clustering feature_requests.csv --language 中文 -o ./cn_features -v
query-clustering feature_requests.csv --language 英文 -o ./en_features -v

# 2. Review topic summaries
head -20 ./cn_features/topic_summaries.csv

# 3. Identify feature themes
cat ./cn_features/statistics.csv
```

### Data Quality Workflow

```bash
# 1. Test on small sample
query-clustering data.csv --sample 100 -o ./test_results -v

# 2. Review quality
cat ./test_results/statistics.csv
head -50 ./test_results/clustered_queries.csv

# 3. Process full dataset if satisfied
query-clustering data.csv -o ./final_results -v
```

## Integration with Python

You can also use the clustering results in Python:

```python
import pandas as pd

# Load results
results = pd.read_csv('./results/clustered_queries.csv')
summaries = pd.read_csv('./results/topic_summaries.csv')
stats = pd.read_csv('./results/statistics.csv')

# Analyze
print(f"Topics found: {stats.loc[stats['Metric'] == 'Number of Topics', 'Value'].values[0]}")

# Filter by topic
topic_5 = results[results['topic_id'] == 5]
print(f"Queries in Topic 5: {len(topic_5)}")
```

## Support & Documentation

- **API Reference:** See main README.md
- **Python Examples:** Check `examples/` directory
- **Issues:** Report on GitHub repository

## Version

- Package Version: 0.1.0
- Last Updated: 2026-01-16
