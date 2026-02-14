from ..base import Base
import logging
import aiohttp
from typing import AsyncGenerator, Dict, Any, Optional, List
from .... import config
import asyncio

class GenerateStatus:
    WAITING = 1
    RUNNING = 2
    FINISHED = 3
    REJECTED = 4
    SUCCESS = 5
    FAILED = 6
    TIMEOUT = 7

class Base(Base):
    def __init__(
            self,
            timeout:int=150,
            interval:int=1,
            **kwargs):
        super().__init__(**kwargs)
        self.status_config = config.liblib.Status()
        self.timeout = timeout
        self.interval = interval

    async def generate(self, **kwargs) -> Optional[List[str]]:
        try:
            # 构建请求参数
            request_data = self._build_request_data(**kwargs)
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                url = self.config.url
                headers = {
                    "Content-Type": "application/json"
                }
                
                async with session.post(url, headers=headers, json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return await self._parse_response(result)
                    else:
                        error_text = await response.text()
                        logging.exception(f"API请求失败: {response.status}, {error_text}")
                        
        except Exception as e:
            logging.exception(f"生成图片失败: {e}")
    
    def _build_request_data(self, prompt: str, image_height:int, image_width:int, image_number:int=1) -> Dict[str, Any]:
        """
        构建请求数据
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
        
        Returns:
            Dict[str, Any]: 请求数据
        """
        # 获取参数，使用默认值
        template_uuid = self.config.model
        image_size = {
            "width": image_width,
            "height": image_height
        }
        img_count = image_number
        
        # 构建generateParams
        generate_params = {
            "prompt": prompt,
            "imgCount": img_count,
            "imageSize": image_size,
        }
        
        # 构建完整请求数据
        request_data = {
            "templateUuid": template_uuid,
            "generateParams": generate_params
        }
        
        return request_data
    
    async def _parse_response(self, response_data: Dict[str, Any]) -> Optional[List[str]]:
        """
        解析API响应
        
        Args:
            response_data: API响应数据
        
        Returns:
            str: 图片URL或base64数据
        """
        try:
            code = response_data['code']
            data = response_data['data']
            msg = response_data['msg']
            if code == 0:
                generateUuid = data['generateUuid']
                return await self.wait_generate(generateUuid)
            else:
                logging.exception(f"API请求失败: {response_data}")
                
        except Exception as e:
            logging.exception(f"解析响应失败: {e}")
        
    async def wait_generate(self, generateUuid: str) -> Optional[List[str]]:
        # 发送请求
        async with aiohttp.ClientSession() as session:
            url = self.status_config.url
            headers = {
                "Content-Type": "application/json"
            }
            
            request_data = {
                "generateUuid": generateUuid
            }
            
            t = self.timeout
            while t > 0:
                async with session.post(url, headers=headers, json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        try:
                            code = result['code']
                            data = result['data']
                            msg = result['msg']
                            if code == 0:
                                uuid = data['generateUuid']
                                status = data['generateStatus']
                                msg = data['generateMsg']
                                points_cost = data['pointsCost']
                                account_balance = data['accountBalance']
                                images = data['images']

                                if status in [GenerateStatus.FINISHED, GenerateStatus.SUCCESS]:
                                    images_url = [image['imageUrl'] for image in images]
                                    return images_url
                                elif status == GenerateStatus.RUNNING:
                                    pass
                                else:
                                    logging.error(f"图片生成状态异常: {status}")
                                    return
                            else:
                                logging.exception(f"图片生成失败: {result}")
                                return
                        except:
                            logging.exception(f"解析响应失败: {result}")
                            return
                    else:
                        error_text = await response.text()
                        logging.exception(f"API请求失败: {response.status}, {error_text}")
                        return

                t -= self.interval
                await asyncio.sleep(self.interval)

            logging.error(f"图片生成超时: {generateUuid}")

    
    async def run(self,**kwargs) -> AsyncGenerator[List[str], None]:
        rt = await self.generate(**kwargs)
        yield rt