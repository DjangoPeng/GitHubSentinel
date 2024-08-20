# LangChain AI 项目简报 - 2024-08-20

## 新增功能
1. **Ollama 模型支持工具调用** (#25555)
2. **添加 B(bugbear) ruff 规则** (#25520)
3. **添加 LangSmith 文档加载器** (#25493)
4. **添加 Union 提供者 - Agentic RAG 示例** (#25509)
5. **添加 LangChain Box 包和 DocumentLoader** (#25506)
6. **添加 ZhipuAIEmbeddings 文档** (#25467)
7. **添加 ColBERT 参考** (#25452)

## 主要改进
1. **Huridocs PDF 加载器增加更多功能** (#25543)
2. **改进浏览器自动化中“请求过大”问题的部分解决方案** (#25527)
3. **添加更多嵌入标准测试** (#25513)
4. **添加异步测试变体** (#25501)
5. **添加更多文档加载器索引** (#25500)
6. **添加 JSON 模式标准测试** (#25497)

## 修复问题
1. **create_tool_calling_agent 仅返回工具结果而不是直接答案** (#25568)
2. **修复 UnionType 类型变量替换** (#25566)
3. **修复 create_tool_calling_agent 对 AzureChatOpenAI 不工作的问题** (#25564)
4. **修复 ChatOpenAI http_client 无法指定的问题** (#25561)
5. **修复 VectorStoreRetriever._get_relevant_documents 错误** (#25530)
6. **修复 VectorStoreRetriever 无法正确处理来自 invoke() 的关键字参数** (#25528)
7. **修复 StructuredQueryOutputParser 在包含日期和时间时抛出错误** (#25526)
8. **修复 Chroma 搜索与文本搜索使用相同嵌入函数时结果不同的问题** (#25517)
9. **修复 Pydantic 解析器问题** (#25516)
10. **修复内容块提示模板** (#25514)
11. **修复 OpenAI 拒绝结构化输出未添加到 AIMessageChunk.additional_kwargs 的问题** (#25510)
12. **修复 AzureSearch 向量存储中使用文档 ID 作为键的问题** (#25486)
13. **修复 OpenAI LLM 集成笔记本中的拼写错误** (#25492)

## 文档更新
1. **添加 Azure Database for PostgreSQL 文档** (#25560)
2. **更新集成参考文档** (#25556, #25511)
3. **添加宪法 AI 参考** (#25553)
4. **更新 Ollama 文档** (#25549)
5. **更新 0.3 版本文档** (#25459)

## 社区贡献
1. **更改 Arcee LLM 和 Arcee 工具** (#25551)
2. **添加流和 astream 到 chatyandexgpt** (#25483)

## 其他
1. **修复回退上下文覆盖** (#25550)
2. **测试 Pydantic 2 和 LangChain 0.3** (#25503)