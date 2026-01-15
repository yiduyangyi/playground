# Ollama Integration Guide

本指南说明如何在 query-clustering 中使用本地 Ollama 部署的 bge-m3 模型进行 embedding。

## 为什么使用 Ollama？

- **本地部署**：无需依赖云 API，完全本地化
- **隐私保护**：数据不上传到云端
- **成本低**：无需支付 API 费用
- **性能好**：bge-m3 是高质量的中文 embedding 模型
- **灵活性**：支持多种模型切换

## 安装步骤

### 1. 安装 Ollama

访问 [https://ollama.ai](https://ollama.ai) 下载并安装 Ollama。

### 2. 拉取 bge-m3 模型

```bash
ollama pull bge-m3
```

### 3. 启动 Ollama 服务

```bash
ollama serve
```

Ollama 服务将在 `http://localhost:11434` 上运行。

### 4. 安装 Python 依赖

```bash
# 安装带 ollama 支持的 query-clustering
pip install query-clustering[ollama]

# 或者单独安装 ollama Python 包
pip install ollama
```

## 使用方法

### 基本用法

```python
from query_clustering import ChineseQueryClustering

# 使用 Ollama 的 bge-m3 模型（默认）
clustering = ChineseQueryClustering(embedder_type='ollama')

documents = [
    "北京的天气怎么样",
    "今天北京天气如何",
    "北京明天会下雨吗",
    "上海的天气预报",
]

clustering.fit(documents)
print(clustering.get_topic_info())
```

### 使用远程 Ollama 服务器

```python
clustering = ChineseQueryClustering(
    embedder_type='ollama',
    base_url='http://192.168.1.100:11434'  # 你的 Ollama 服务器地址
)
```

### 使用其他 Ollama 模型

```python
clustering = ChineseQueryClustering(
    embedder_type='ollama',
    model_name='other-model-name'
)
```

### 自定义 Embedder

```python
from query_clustering import OllamaEmbedder

custom_embedder = OllamaEmbedder(
    model_name='bge-m3',
    base_url='http://localhost:11434',
    normalize=True
)

clustering = ChineseQueryClustering(embedder=custom_embedder)
```

## 对比不同 Embedding 方案

| 方案 | 优点 | 缺点 | 使用场景 |
|------|------|------|---------|
| SentenceTransformer | 简单易用、无需服务器 | 需要下载模型、占用内存多 | 快速原型、单机运行 |
| Ollama bge-m3 | 本地化、隐私好、性能好 | 需要部署 Ollama | 生产环境、隐私敏感 |

## 常见问题

### Q: 如何检查 Ollama 是否正常运行？

```bash
curl http://localhost:11434/api/tags
```

### Q: bge-m3 模型占用多少存储空间？

约 3-4GB（GGUF 格式）

### Q: 如何切换回 SentenceTransformer？

```python
clustering = ChineseQueryClustering(
    embedder_type='sentence-transformer',
    embedding_model='paraphrase-multilingual-MiniLM-L12-v2'
)
```

### Q: 支持哪些 Ollama 模型？

任何 Ollama 支持的 embedding 模型，如：
- `bge-m3` - 推荐用于中文
- `nomic-embed-text`
- `all-minilm`

## 性能参数

### bge-m3 模型信息

- **类型**：多语言 embedding 模型
- **维度**：1024
- **最大输入长度**：8192 token
- **特点**：支持 100+ 语言，包括中文

### 优化建议

1. **批处理**：使用 `show_progress_bar=True` 查看进度
2. **规范化**：OllamaEmbedder 默认启用 L2 规范化
3. **模型选择**：对于中文，bge-m3 > 通用多语言模型

## 故障排查

### 连接错误

```
ConnectionError: Failed to connect to Ollama server
```

**解决方案**：
1. 确保 Ollama 服务正在运行：`ollama serve`
2. 检查服务地址是否正确
3. 检查防火墙设置

### 模型未找到

```
Error: model 'bge-m3' not found
```

**解决方案**：
1. 拉取模型：`ollama pull bge-m3`
2. 检查模型名称是否正确

### 内存不足

**解决方案**：
1. 减少批处理大小
2. 减少并发请求数
3. 增加系统内存或使用更小的模型

## 更多资源

- [Ollama 官网](https://ollama.ai)
- [BGE-M3 模型](https://huggingface.co/BAAI/bge-m3)
- [BERTopic 文档](https://maartengr.github.io/BERTopic/)
