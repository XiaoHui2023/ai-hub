from fastapi import HTTPException

from .. import models
from ....configure import InputModels,BaseAI
from .... import core
import logging

class Chat:
    def __init__(self,config:InputModels,payload: models.Chat):
        self.config = config
        self.payload = payload
        
    @property
    def support(self) -> dict:
        data = {
            "aliyun": {
                'provider' : core.gpt.provider.chat.aliyun.Aliyun,
                'config' : {
                    "deepseek-v3": self.config.gpt.aliyun.deepseek_v3,
                    "deepseek-r1": self.config.gpt.aliyun.deepseek_r1,
                    "qwen-max" : self.config.gpt.aliyun.qwen_max,
                    'qwen-plus' : self.config.gpt.aliyun.qwen_plus,
                    "qwen-vl-plus" : self.config.gpt.aliyun.qwen_vl_plus,
                    'default' : self.config.gpt.aliyun.deepseek_v3,
                }
            },
            "grok": {
                'provider' : core.gpt.provider.chat.grok.Grok,
                'config' : {
                    "grok3": self.config.gpt.grok.grok3,
                    "grok2-image": self.config.gpt.grok.grok2_image,
                    "grok3-mini": self.config.gpt.grok.grok3_mini,
                    "grok4": self.config.gpt.grok.grok4,
                    "default": self.config.gpt.grok.grok3,
                }
            },
            "openai": {
                'provider' : core.gpt.provider.chat.openai.OpenAI,
                'config' : {
                    "gpt-5": self.config.gpt.openai.gpt5,
                    "default": self.config.gpt.openai.gpt5,
                }
            }
        }
        return data | {
            "default" : data['aliyun'],
        }

    async def run(self) -> str:
        provider = self.get_chat_provider(self.payload.provider, self.payload.model)

        # 聚合流式结果
        result = ""
        try:
            async for chunk in provider.run(
                user=self.payload.user,
                assistants=self.payload.assistants,
                system=self.payload.system,
                memory=self.payload.memory,
                name=self.payload.name,
            ):
                if chunk:
                    result += chunk
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"调用模型失败: {e}")

        return result


    def get_chat_provider(self,provider_name: str, model_name: str) -> core.gpt.provider.Base:
        support = self.support
        if provider_name not in support:
            raise HTTPException(status_code=400, detail=f"不支持的 provider: {provider_name},支持的 provider: {support.keys()}")
        
        provider_type: core.gpt.provider.Base = support[provider_name]['provider']
        configs: dict = support[provider_name]['config']
        if model_name not in configs:
            raise HTTPException(status_code=400, detail=f"不支持的 model: {model_name},支持的 model: {configs.keys()}")

        config: BaseAI = configs[model_name]
        api_key = config.get_api_key()
        base_url = config.base_url
        model = config.model
        proxy = config.proxy
        kwargs = {k:v for k,v in {
            "temperature": self.payload.temperature,
            "frequency_penalty": self.payload.frequency_penalty,
            "presence_penalty": self.payload.presence_penalty,
            "top_p": self.payload.top_p,
        }.items() if v is not None}
        provider = provider_type(
            api_key=api_key,
            base_url=base_url,
            model=model,
            proxy=proxy,
            **kwargs,
        )

        return provider
    
    

'''
# 默认使用
DefaultThinkProvider = provider.chat.aliyun.DeepSeekR1
DefaultSearchProvider = provider.search.bocha.WebSearch
DefaultVisionProvider = provider.vision.aliyun.QwenVlPlus
DefaultTextToImageProvider = provider.text_to_image.liblib.Star3
DefaultRagProvider = provider.rag.QAnything
'''