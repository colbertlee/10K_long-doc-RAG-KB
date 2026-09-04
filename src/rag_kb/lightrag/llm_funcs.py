"""LLM functions for LightRAG - supports multiple providers."""

import asyncio
import os
import ollama
from rag_kb.config.core_config import settings


def get_llm_func():
    """Get LLM function based on provider configuration."""
    # Read current provider from config.yaml instead of cached settings
    import yaml
    from pathlib import Path
    
    config_path = Path("configs/config.yaml")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        llm_config = config_data.get('llm', {})
        provider = llm_config.get('provider', 'ollama').lower()
        
        # Debug logging
        print(f"DEBUG: get_llm_func() - provider from config.yaml: {provider}", flush=True)
        print(f"DEBUG: get_llm_func() - model from config.yaml: {llm_config.get('model', 'N/A')}", flush=True)
        print(f"DEBUG: get_llm_func() - has api_key: {bool(llm_config.get('api_key'))}", flush=True)
    else:
        provider = settings.llm_provider.lower()
        print(f"DEBUG: get_llm_func() - config.yaml not found, using settings: {provider}", flush=True)
    
    if provider == "minimax":
        print(f"DEBUG: get_llm_func() - returning minimax_llm", flush=True)
        return minimax_llm
    else:
        print(f"DEBUG: get_llm_func() - returning ollama_llm", flush=True)
        return ollama_llm


async def minimax_llm(prompt: str, **kwargs):
    """Generate LLM response using Minimax (async).
    
    Args:
        prompt: Input prompt for the LLM
        **kwargs: Additional parameters for generation
        
    Returns:
        Generated text response
    """
    try:
        from rag_kb.lightrag.minimax_adapter import MinimaxAdapter, MinimaxConfig
        import yaml
        from pathlib import Path
        
        # Load Minimax configuration from config.yaml
        config_path = Path("configs/config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            llm_config = config_data.get('llm', {})
            
            config = MinimaxConfig(
                api_key=llm_config.get('api_key', os.getenv("MINIMAX_API_KEY", "")),
                group_id=llm_config.get('group_id', os.getenv("MINIMAX_GROUP_ID", "")),
                base_url=llm_config.get('base_url', os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")),
                model=llm_config.get('model', os.getenv("MINIMAX_MODEL", "abab6.5s-chat")),
                temperature=float(llm_config.get('temperature', os.getenv("MINIMAX_TEMPERATURE", "0.3"))),
                top_p=float(llm_config.get('top_p', os.getenv("MINIMAX_TOP_P", "0.9"))),
                max_tokens=int(llm_config.get('max_tokens', os.getenv("MINIMAX_MAX_TOKENS", "2048"))),
                timeout=int(os.getenv("MINIMAX_TIMEOUT", "60"))
            )
        else:
            # Fallback to environment variables
            config = MinimaxConfig(
                api_key=os.getenv("MINIMAX_API_KEY", ""),
                group_id=os.getenv("MINIMAX_GROUP_ID", ""),
                base_url=os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1"),
                model=os.getenv("MINIMAX_MODEL", "abab6.5s-chat"),
                temperature=float(os.getenv("MINIMAX_TEMPERATURE", "0.3")),
                top_p=float(os.getenv("MINIMAX_TOP_P", "0.9")),
                max_tokens=int(os.getenv("MINIMAX_MAX_TOKENS", "2048")),
                timeout=int(os.getenv("MINIMAX_TIMEOUT", "60"))
            )
        
        # Validate API key
        if not config.api_key or config.api_key == "sk-test_api_key_12345":
            error_msg = "Minimax API key is not configured or is using test key. Please configure a valid API key in the system settings."
            print(f"Minimax LLM error: {error_msg}", flush=True)
            raise ValueError(error_msg)
        
        adapter = MinimaxAdapter(config)
        
        # Check if this is an entity extraction prompt
        is_entity_extraction = "Extract entities and relationships" in prompt or "missed or incorrectly formatted" in prompt

        # Use appropriate system prompt based on task type
        if is_entity_extraction:
            system_prompt = """你是一位顶尖的知识图谱架构师与信息抽取专家。你的任务是从给定的文本切片中提取出所有的核心实体（Entities）以及它们之间的结构化语义关系（Relationships），构建精准、拓扑清晰的知识图谱。

Steps:
1. 识别并提取文本中的所有关键实体：
   - entity_name: 实体的名称（统一使用最标准、规范的名词，避免代词如"它"、"该系统"）。
   - entity_type: 实体的类型（例如：System, Component, Protocol, Organization, Metric, Configuration, Fault, Concept 等）。
   - entity_description: 实体的综合描述，必须包含其在上下文中的核心功能、状态、属性或技术特征。

2. 识别并提取实体之间的显式与强逻辑关系：
   - src_id: 关系的源实体名称（必须与上述已抽取的 entity_name 完全一致）。
   - tgt_id: 关系的目标实体名称（必须与上述已抽取的 entity_name 完全一致）。
   - rel_type: 关系的动词或谓词短语（如：CONTAINS, DEPLOYS, CALLS, COMMUNICATES_WITH, CAUSES, DEPENDS_ON, SUPPORTS, CONFIGURES 等，尽量使用明确的大写动词/关系词）。
   - rel_description: 详细说明这两个实体为何产生该关联，以及关联发生时的具体上下文、条件或数据流向。
   - rel_strength: 关系的关联强度，打分范围为 1 到 10 的整数（10 为强直接依赖，1 为弱相关）。

Output Format:
请严格按照以下自定义分隔符的结构进行输出，切勿添加任何 Markdown 格式以外的废话或前缀：

-[Entities]
-("entity"<|>entity_name<|>entity_type<|>entity_description)
-##
-("entity"<|>entity_name<|>entity_type<|>entity_description)

-[Relationships]
-("relationship"<|>src_id<|>tgt_id<|>rel_type<|>rel_description<|>rel_strength)
-##
-("relationship"<|>src_id<|tgt_id<|>rel_type<|>rel_description<|>rel_strength)
-<|COMPLETE|>

Strict Constraints:
1. 保持实体名称的一致性（同一概念在不同段落出现必须使用同一个实体名称）。
2. 专业术语（如 CLI 命令、协议名称、网络端口、硬件型号等）严格保持原生拼写，不要随意直译。
3. 关系抽取必须有据可查，严禁凭空脑补不存在的因果关系。
4. 每个字段之间使用 <|> 分隔，每条记录之间使用 ## 分隔。"""
        else:
            system_prompt = """你是一个专业的知识库助手，专门基于提供的知识库内容回答用户问题。你的核心目标是：**基于真实检索文档，输出准确、严谨、可追溯且无幻觉的回答**。

## 核心原则

### 1. 真实性原则
- **严格基于检索文档**：所有回答必须严格基于提供的检索上下文
- **禁止外部知识**：不得使用训练数据中的外部知识或常识
- **事实验证**：每个事实都必须能在检索文档中找到对应依据
- **原文引用**：重要信息应直接引用检索文档中的原文

### 2. 准确性原则
- **精确表述**：使用检索文档中的精确表述，避免意译
- **数据准确**：所有数字、日期、名称必须与检索文档完全一致
- **逻辑准确**：推理过程必须基于检索文档的逻辑关系
- **范围准确**：明确说明回答的适用范围和限制

### 3. 严谨性原则
- **逻辑严密**：推理过程必须逻辑严密，无矛盾
- **表述严谨**：使用准确、专业的术语，避免模糊表达
- **结构严谨**：回答结构清晰，层次分明
- **结论严谨**：结论必须有充分的依据支持

### 4. 可追溯性原则
- **来源标注**：每个重要事实都必须标注信息来源
- **引用格式**：使用标准引用格式 [文档ID:段落] 或 [文档名称:章节]
- **追溯路径**：提供从问题到答案的完整追溯路径
- **原文对照**：重要观点应提供检索文档中的原文对照

## 操作规范

### 回答结构要求
每个回答必须包含以下结构：

1. **直接回答**：首先给出明确的答案
2. **依据说明**：说明答案的检索文档依据
3. **详细解释**：基于检索文档的详细解释
4. **引用标注**：在相关内容后标注来源
5. **限制说明**：明确说明回答的适用范围

### 引用标注规范
- **强制引用**：所有事实性陈述都必须引用
- **引用格式**：[文档ID:具体位置] 或 [文档名称:章节]
- **引用位置**：在相关事实后立即标注
- **引用验证**：确保引用的真实性和准确性

### 拒绝回答规范
当遇到以下情况时，必须拒绝回答：
- 检索文档中没有相关信息
- 检索文档信息不足以回答问题
- 问题超出检索文档覆盖范围
- 检索文档信息存在矛盾

### 无幻觉保障措施
- **严格依据**：只说检索文档中有的内容
- **避免推测**：不得推测或补充检索文档中没有的信息
- **拒绝猜测**：不得基于常识或训练数据猜测
- **明确边界**：明确说明检索文档的信息边界

## 质量检查清单

在生成每个回答前，必须自检：
- [ ] 所有信息都来自检索文档
- [ ] 没有使用外部知识或常识
- [ ] 所有事实都有引用标注
- [ ] 引用格式正确且可验证
- [ ] 没有推测或补充信息
- [ ] 逻辑严密，无矛盾
- [ ] 表述准确，无歧义
- [ ] 结构清晰，层次分明

## 错误处理

如果检索文档不足以回答问题：
1. 明确说明检索文档中的相关信息
2. 指出缺失的关键信息
3. 建议用户提供更具体的查询
4. 绝不编造或推测信息

记住：你的价值在于准确、严谨地呈现检索文档中的信息，而不是展示你的知识储备。"""

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        print(f"Minimax LLM Request: {prompt[:100]}...", flush=True)
        
        # Call Minimax API
        result = await adapter.chat_completion(messages)
        
        # Close adapter
        await adapter.close()
        
        if result["success"]:
            content = result["content"]
            print(f"Minimax LLM Response length: {len(content)}", flush=True)
            print(f"Minimax LLM Response preview: {content[:100]}...", flush=True)
            
            if not content or not content.strip():
                return "[]"
            
            return content
        else:
            print(f"Minimax LLM error: {result['error']}", flush=True)
            raise ConnectionError(f"Minimax API error: {result['error']}")
            
    except ValueError as e:
        print(f"Minimax LLM configuration error: {e}", flush=True)
        raise ConnectionError(f"Minimax配置错误: {str(e)}")
    except Exception as e:
        print(f"Minimax LLM error: {e}", flush=True)
        raise ConnectionError(f"Minimax LLM错误: {str(e)}")


# Global LLM cache for response caching
_llm_cache = {}
_llm_cache_enabled = True

def set_llm_cache_enabled(enabled: bool):
    """Enable or disable LLM response caching."""
    global _llm_cache_enabled
    _llm_cache_enabled = enabled

def clear_llm_cache():
    """Clear the LLM response cache."""
    global _llm_cache
    _llm_cache.clear()

async def ollama_llm(prompt: str, **kwargs):
    """Generate LLM response using Ollama (async) with caching support.
    
    Args:
        prompt: Input prompt for the LLM
        **kwargs: Additional parameters for generation
        
    Returns:
        Generated text response
    """
    global _llm_cache, _llm_cache_enabled
    
    try:
        # Check cache first if enabled (from config)
        cache_enabled = getattr(settings, 'llm_cache_enabled', True)
        if cache_enabled and _llm_cache_enabled:
            cache_key = hash(prompt + str(kwargs))
            if cache_key in _llm_cache:
                print(f"LLM cache hit for prompt: {prompt[:50]}...", flush=True)
                return _llm_cache[cache_key]
        
        # Run synchronous Ollama call in thread pool
        loop = asyncio.get_event_loop()
        client = ollama.Client(host=settings.llm_base_url)
        
        # Check if this is an entity extraction prompt
        is_entity_extraction = "Extract entities and relationships" in prompt or "missed or incorrectly formatted" in prompt

        # Use appropriate system prompt based on task type (optimized for qwen3.5:4b)
        if is_entity_extraction:
            system_prompt = """你是技术文档知识图谱专家。从文本中精确提取实体和关系：

实体提取规则：
- 识别技术概念、组件、API、配置项、错误码等
- 实体名称使用标准术语，避免代词
- 实体类型：concept/component/api/configuration/error/service/protocol等
- 实体描述要包含核心功能和上下文

关系提取规则：
- 识别包含、依赖、调用、配置、处理等技术关系
- 关系类型：contains/depends_on/calls/configures/handles/monitors等
- 关系描述要明确技术关联和业务逻辑

输出格式：
-[Entities]
-("entity"<|>name<|>type<|>description)
-##
-[Relationships]
-("relationship"<|>src<|>tgt<|>type<|>description<|>strength)
-<|COMPLETE|>

严格要求：
1. 实体名称必须一致，同一概念使用相同名称
2. 技术术语保持原样，如API路径、配置参数等
3. 关系必须有文本依据，不得凭空推断
4. 使用<|>分隔字段，##分隔记录"""
        else:
            system_prompt = """你是专业的技术文档知识库助手。基于提供的上下文准确回答技术问题：

核心原则：
1. 严格基于提供的上下文回答，不使用外部知识
2. 保持技术术语的准确性，不随意意译
3. 重要信息要标注来源文档位置
4. 回答结构清晰，逻辑严密
5. 如上下文不足，明确说明已知和缺失信息

回答格式：
- 直接回答：首先给出明确答案
- 详细说明：基于上下文的技术解释
- 引用来源：标注信息来源
- 相关建议：提供相关的技术要点（如有）
- 限制说明：明确回答的适用范围

质量要求：
- 所有技术信息必须来自上下文
- 配置参数、API路径等要保持原样
- 步骤类回答要完整且可操作
- 错误处理要包含具体错误码和解决方案"""

        def sync_chat():
            print(f"LLM Request: {prompt[:100]}...", flush=True)
            try:
                # Try HTTP API directly as fallback
                import requests
                import json
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                
                # qwen3.5:4b优化参数
                options = {
                    'temperature': settings.llm_temperature,
                    'top_p': settings.llm_top_p,
                    'num_predict': settings.llm_max_tokens,
                }
                
                # 添加qwen3.5:4b特定参数
                if hasattr(settings, 'llm_num_ctx'):
                    options['num_ctx'] = settings.llm_num_ctx
                if hasattr(settings, 'llm_num_batch'):
                    options['num_batch'] = settings.llm_num_batch
                
                # Try HTTP API first
                try:
                    payload = {
                        "model": settings.llm_model,
                        "messages": messages,
                        "options": options,
                        "stream": False
                    }
                    
                    response = requests.post(
                        f"{settings.llm_base_url}/api/chat",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json().get('message', {}).get('content', '')
                        print(f"HTTP API Response length: {len(result) if result else 0}", flush=True)
                        return result
                    else:
                        print(f"HTTP API failed with status {response.status_code}", flush=True)
                        raise ConnectionError(f"HTTP API error: {response.status_code}")
                        
                except Exception as http_error:
                    print(f"HTTP API failed: {http_error}, trying Python client", flush=True)
                    
                    # Fallback to Python client
                    try:
                        resp = client.chat(
                            model=settings.llm_model,
                            messages=messages,
                            options=options,
                            stream=False
                        )
                        result = resp['message']['content']
                        print(f"Python Client Response length: {len(result) if result else 0}", flush=True)
                        return result
                    except Exception as client_error:
                        print(f"Python Client also failed: {client_error}", flush=True)
                        raise ConnectionError(f"Ollama LLM调用失败: {str(client_error)}")
                
            except Exception as e:
                print(f"LLM call failed: {e}", flush=True)
                raise ConnectionError(f"Ollama连接失败: {str(e)}. 请确保Ollama服务正在运行 (ollama serve) 并且已下载模型 {settings.llm_model}")
        
        result = await loop.run_in_executor(None, sync_chat)
        
        if not result or not result.strip():
            print("LLM returned empty response, using fallback", flush=True)
            raise ConnectionError("Ollama返回空响应，请检查模型是否正确下载")
        
        # Cache the result if enabled
        cache_enabled = getattr(settings, 'llm_cache_enabled', True)
        if cache_enabled and _llm_cache_enabled:
            cache_key = hash(prompt + str(kwargs))
            _llm_cache[cache_key] = result
            # Limit cache size to prevent memory issues
            if len(_llm_cache) > 1000:
                # Remove oldest entries
                oldest_keys = list(_llm_cache.keys())[:100]
                for key in oldest_keys:
                    del _llm_cache[key]
            
        return result
    except ConnectionError as e:
        print(f"Ollama LLM connection error: {e}", flush=True)
        raise ConnectionError(f"Ollama连接错误: {str(e)}")
    except Exception as e:
        print(f"Ollama LLM error: {e}", flush=True)
        raise ConnectionError(f"Ollama LLM错误: {str(e)}")