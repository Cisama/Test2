"""EdgeFn.net 代理 provider (智谱 GLM / DeepSeek 等多模型聚合)

W4-41 (2026-06-30): 接入 edgefn.net 代理
- 支持 GLM-4.5V / GLM-5.2 (reasoning model, 原生 function call, 跟 deepseek-v4-flash 类似需要 reasoning_content 兜底)
- 也支持 deepseek 系列 (按 model 字段切)
- 一个 key 多模型, model 由调用方传

测试过的模型 (2026-06-30):
- GLM-4.5V: EdgeFn 控制台当前示例模型
- GLM-5.2: ✅ 200, reasoning_content, 原生 tool_calls
- deepseek-v4-pro: ❌ 403 ModelNotAllowed (key 没权限)
- deepseek-v4-flash: (待测, 之前走 deepseek.com 直连)

API: POST https://api.edgefn.net/v1/chat/completions
Auth: Bearer sk-...
格式: OpenAI 兼容

API Key 必须由调用方或 EDGEFN_API_KEY 环境变量提供，源码不保存凭据。
"""
import logging
from typing import Dict
from app.llm.openai_compatible import OpenAICompatibleLLM
from app.llm.base import LLMResponse
from app.llm.request_contract import ModelRequestOptions

logger = logging.getLogger(__name__)


class EdgeFnLLM(OpenAICompatibleLLM):
    """edgefn.net 通用 provider — 同一 key 走 GLM / DeepSeek 等多模型

    通过 DEFAULT_MODEL 切, 用户调用时传 model 参数覆盖:
        EdgeFnLLM(api_key="sk-...", model="GLM-4.5V")
        EdgeFnLLM(api_key="sk-...", model="GLM-5.2")
        EdgeFnLLM(api_key="sk-...", model="deepseek-v4-flash")
    """

    DEFAULT_API_BASE = "https://api.edgefn.net/v1"
    DEFAULT_MODEL = "GLM-4.5V"  # EdgeFn 当前控制台示例模型

    # 保留属性以兼容旧调用方，但不在源码中存放凭据。
    HARDCODED_API_KEY = None

    def __init__(self, api_key: str = None, model: str = None):
        # 凭据由调用方或配置层从环境变量注入。
        if not api_key:
            api_key = self.HARDCODED_API_KEY
        if not api_key:
            raise ValueError("EDGEFN_API_KEY 未配置")
        super().__init__(api_key, model)
        logger.info(f"EdgeFn LLM 初始化完成, model: {self.model}, api_base: {self.api_base}")

    async def chat(self, messages, tools=None, request_options: ModelRequestOptions = None, **kwargs):
        return await super().chat(messages, tools=tools, request_options=request_options, **kwargs)

    async def stream_chat(self, messages, request_options: ModelRequestOptions = None):
        async for chunk in super().stream_chat(messages, request_options=request_options):
            yield chunk

    def _parse_response(self, result: Dict) -> LLMResponse:
        """EdgeFn 走 thinking 解析 (跟 DeepSeek 一样是 reasoning model)

        GLM-5.2 实测响应格式:
        - content: "" (空)
        - reasoning_content: "思考过程" (有)
        - tool_calls: [{...}] (原生 function call, 结构化)
        - finish_reason: "tool_calls"
        """
        return self._parse_response_with_thinking(result)
