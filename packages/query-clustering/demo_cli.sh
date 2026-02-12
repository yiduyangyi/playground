#!/bin/bash
# Query Clustering CLI Demo Script
# This script demonstrates various use cases of the query-clustering CLI tool

set -e

DATASET="packages/query-clustering/data/clustering_dataset.csv"
OUTPUT_DIR="demo_results"

echo "=================================="
echo "Query Clustering CLI - Demo"
echo "=================================="
echo ""

# Create demo directory
mkdir -p "$OUTPUT_DIR"

echo "📂 Dataset Info:"
echo "   Path: $DATASET"
echo "   Rows: $(tail -n +2 $DATASET | wc -l | xargs)"
echo ""

# Demo 1: Basic clustering
echo "📊 Demo 1: Basic Clustering (English queries, sample 300)"
echo "Command: query-clustering $DATASET --language 英文 --sample 300 -o $OUTPUT_DIR/demo1 -v"
uv run query-clustering "$DATASET" --language 英文 --sample 300 -o "$OUTPUT_DIR/demo1" -v
echo ""

# Demo 2: Category-based
echo "📊 Demo 2: Category-based Clustering (旅游出行 category)"
echo "Command: query-clustering $DATASET --category 旅游出行 -o $OUTPUT_DIR/demo2 -v"
uv run query-clustering "$DATASET" --category 旅游出行 -o "$OUTPUT_DIR/demo2" -v
echo ""

# Demo 3: Language + limit
echo "📊 Demo 3: Chinese Queries (first 800)"
echo "Command: query-clustering $DATASET --language 中文 --limit 800 -o $OUTPUT_DIR/demo3 -v"
uv run query-clustering "$DATASET" --language 中文 --limit 800 -o "$OUTPUT_DIR/demo3" -v
echo ""

echo "✅ All demos completed!"
echo ""
echo "📁 Generated Results:"
for i in 1 2 3; do
    echo ""
    echo "Demo $i:"
    echo "  Directory: $OUTPUT_DIR/demo$i/"
    ls -lh "$OUTPUT_DIR/demo$i/"
    echo ""
    echo "  Statistics:"
    cat "$OUTPUT_DIR/demo$i/statistics.csv" | column -t -s','
    echo ""
    echo "  Sample Results (first 5 queries):"
    tail -n +2 "$OUTPUT_DIR/demo$i/clustered_queries.csv" | head -5 | column -t -s','
done

echo ""
echo "=================================="
echo "📚 For more examples, see: CLI_GUIDE.md"
echo "📖 For API details, see: README.md"
echo "=================================="
