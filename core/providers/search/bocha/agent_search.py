from typing import Dict,Any,Callable,List
from .base import Base
import json
from dataclasses import dataclass

class AgentID():
    BOCHA_RESTAURANT_AGENT = "bocha-restaurant-agent"
    BOCHA_HOTEL_AGENT = "bocha-hotel-agent"
    BOCHA_ATTRACTION_AGENT = "bocha-attraction-agent"
    BOCHA_TRAIN_TICKET_AGENT = "bocha-train-ticket-agent"
    BOCHA_FLIGHT_TICKET_AGENT = "bocha-flight-ticket-agent"
    BOCHA_COMPANY_AGENT = "bocha-company-agent"
    BOCHA_SCHOLAR_AGENT = "bocha-scholar-agent"
    BOCHA_WENKU_AGENT = "bocha-wenku-agent"

class SearchType():
    NEAURAL = "neural"
    KEYWORD = "keyword"

@dataclass
class SearchAgent():
    agent_id: AgentID
    name: str
    description: str
    function: Callable
    example_queries: List[str]

class AgentSearch(Base):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            model="agent-search",
            **kwargs
        )
        self.bocha_restaurant_agent = SearchAgent(
            agent_id=AgentID.BOCHA_RESTAURANT_AGENT,
            name="餐厅",
            description="搜索各类餐厅信息，包括中餐、西餐、快餐、特色菜系等。可以查询餐厅位置、评分、价格、特色菜品、营业时间等信息。支持按地区、菜系、价格区间等条件筛选。",
            function=self.restaurant,
            example_queries=[
                "北京有哪些米其林餐厅？",
                "上海外滩附近有什么好吃的本帮菜？",
                "广州天河区人均100元以下的粤式茶餐厅",
                "成都春熙路附近有什么特色小吃？",
                "杭州西湖边有什么环境好的餐厅？",
                "深圳福田区有什么适合商务宴请的餐厅？",
                "南京夫子庙附近有什么老字号？",
                "武汉户部巷有什么特色小吃？",
                "西安回民街有什么必吃的美食？",
                "重庆解放碑附近有什么火锅店？"
            ]
        )
        self.bocha_hotel_agent = SearchAgent(
            agent_id=AgentID.BOCHA_HOTEL_AGENT,
            name="酒店",
            description="搜索各类酒店信息，包括星级酒店、商务酒店、度假酒店、民宿等。可以查询酒店位置、价格、设施、服务、评价等信息。支持按地区、星级、价格区间等条件筛选。",
            function=self.hotel,
            example_queries=[
                "北京王府井附近有什么五星级酒店？",
                "上海外滩有什么能看到江景的酒店？",
                "广州天河区有什么商务酒店？",
                "深圳湾附近有什么度假酒店？",
                "杭州西湖边有什么特色民宿？",
                "成都春熙路附近有什么性价比高的酒店？",
                "三亚亚龙湾有什么海景酒店？",
                "西安钟楼附近有什么酒店？",
                "重庆解放碑附近有什么酒店？",
                "厦门鼓浪屿附近有什么特色民宿？"
            ]
        )
        self.bocha_attraction_agent = SearchAgent(
            agent_id=AgentID.BOCHA_ATTRACTION_AGENT,
            name="景点",
            description="搜索各类旅游景点信息，包括自然景观、人文景点、主题公园、博物馆等。可以查询景点位置、门票、开放时间、特色、评价等信息。支持按地区、类型、价格等条件筛选。",
            function=self.attraction,
            example_queries=[
                "北京有什么必去的景点？",
                "上海有什么适合拍照的地方？",
                "广州有什么历史古迹？",
                "深圳有什么主题公园？",
                "杭州西湖有什么景点？",
                "成都有什么特色景点？",
                "西安有什么历史景点？",
                "重庆有什么网红打卡地？",
                "厦门有什么必去的景点？",
                "三亚有什么好玩的地方？"
            ]
        )
        self.bocha_train_ticket_agent = SearchAgent(
            agent_id=AgentID.BOCHA_TRAIN_TICKET_AGENT,
            name="火车票",
            description="搜索火车票信息，包括高铁、动车、普通列车等。可以查询车次、票价、座位类型、时刻表等信息。支持按出发地、目的地、日期等条件筛选。",
            function=self.train_ticket,
            example_queries=[
                "北京到上海的高铁票",
                "广州到深圳的动车票",
                "成都到重庆的火车票",
                "杭州到南京的高铁票",
                "武汉到长沙的火车票",
                "西安到郑州的高铁票",
                "南京到苏州的动车票",
                "深圳到广州的火车票",
                "重庆到成都的高铁票",
                "上海到杭州的动车票"
            ]
        )
        self.bocha_flight_ticket_agent = SearchAgent(
            agent_id=AgentID.BOCHA_FLIGHT_TICKET_AGENT,
            name="机票",
            description="搜索航班信息，包括国内航班、国际航班等。可以查询航班号、票价、舱位、时刻表等信息。支持按出发地、目的地、日期等条件筛选。",
            function=self.flight_ticket,
            example_queries=[
                "北京到上海的机票",
                "广州到深圳的航班",
                "成都到重庆的机票",
                "杭州到北京的航班",
                "武汉到上海的机票",
                "西安到广州的航班",
                "南京到深圳的机票",
                "深圳到北京的航班",
                "重庆到上海的机票",
                "上海到成都的航班"
            ]
        )
        self.bocha_company_agent = SearchAgent(
            agent_id=AgentID.BOCHA_COMPANY_AGENT,
            name="公司",
            description="搜索企业信息，包括公司简介、经营范围、注册资本、成立时间、联系方式等。支持按行业、地区、规模等条件筛选。",
            function=self.company,
            example_queries=[
                "阿里巴巴的公司信息",
                "腾讯的注册资本是多少？",
                "华为的成立时间",
                "小米的经营范围",
                "百度的发展历程",
                "京东的企业规模",
                "字节跳动的融资情况",
                "美团的公司简介",
                "拼多多的商业模式",
                "网易的企业文化"
            ]
        )
        self.bocha_scholar_agent = SearchAgent(
            agent_id=AgentID.BOCHA_SCHOLAR_AGENT,
            name="学术",
            description="搜索学术信息，包括论文、期刊、会议、专利等。可以查询作者、机构、发表时间、引用次数等信息。支持按学科、年份、机构等条件筛选。",
            function=self.scholar,
            example_queries=[
                "人工智能最新研究进展",
                "机器学习领域的重要论文",
                "自然语言处理的研究方向",
                "计算机视觉的经典算法",
                "深度学习在医疗领域的应用",
                "区块链技术的研究现状",
                "量子计算的最新突破",
                "生物信息学的研究热点",
                "材料科学的重要发现",
                "环境科学的研究成果"
            ]
        )
        self.bocha_wenku_agent = SearchAgent(
            agent_id=AgentID.BOCHA_WENKU_AGENT,
            name="文库",
            description="搜索文档资料，包括论文、报告、书籍、课件等。可以查询文档类型、作者、发布时间、下载量等信息。支持按学科、类型、年份等条件筛选。",
            function=self.wenku,
            example_queries=[
                "Python编程入门教程",
                "机器学习实战指南",
                "数据结构与算法分析",
                "高等数学教材",
                "英语四六级备考资料",
                "考研数学复习资料",
                "公务员考试真题",
                "教师资格证考试资料",
                "计算机二级考试题库",
                "英语专业八级备考资料"
            ]
        )

    @property
    def agent_list(self) -> List[SearchAgent]:
        return [
            self.bocha_restaurant_agent,
            self.bocha_hotel_agent,
            self.bocha_attraction_agent,
            self.bocha_train_ticket_agent,
            self.bocha_flight_ticket_agent,
            self.bocha_company_agent,
            self.bocha_scholar_agent,
            self.bocha_wenku_agent,
        ]
    
    async def run(self,agent_id:AgentID,query:str,answer:bool=False,stream:bool=False) -> Dict[str,Any]:
        '''
        网络搜索

        agent_id: 代理ID
        query: 搜索关键词
        answer: 是否回答
        stream: 是否流式
        '''
        data = {
            "agentId": agent_id,
            "query": query,
            "searchType": SearchType.NEAURAL,
            "answer": answer,
            "stream": stream
        }
        
        rt = await super().run(data)

        print(json.dumps(rt,indent=4))

        try:
            rt = rt["data"]["webPages"]["value"]

            rt = [{k:v for k,v in value.items() if k in ["name","snippet","summary","datePublished","dateLastCrawled"]} for value in rt]
        except:
            raise Exception(f'Failed to parse response: {rt}')

        return rt
    
    async def restaurant(self,*args,**kwargs):
        '''
        餐厅
        '''
        return await self.run(agent_id=AgentID.BOCHA_RESTAURANT_AGENT,*args,**kwargs)

    async def hotel(self,*args,**kwargs):
        '''
        酒店
        '''
        return await self.run(agent_id=AgentID.BOCHA_HOTEL_AGENT,*args,**kwargs)

    async def attraction(self,*args,**kwargs):
        '''
        景点
        '''
        return await self.run(agent_id=AgentID.BOCHA_ATTRACTION_AGENT,*args,**kwargs)

    async def train_ticket(self,*args,**kwargs):
        '''
        火车票
        '''
        return await self.run(agent_id=AgentID.BOCHA_TRAIN_TICKET_AGENT,*args,**kwargs)

    async def flight_ticket(self,*args,**kwargs):
        '''
        机票
        '''
        return await self.run(agent_id=AgentID.BOCHA_FLIGHT_TICKET_AGENT,*args,**kwargs)

    async def company(self,*args,**kwargs):
        '''
        公司
        '''
        return await self.run(agent_id=AgentID.BOCHA_COMPANY_AGENT,*args,**kwargs)

    async def scholar(self,*args,**kwargs):
        '''
        学术
        '''
        return await self.run(agent_id=AgentID.BOCHA_SCHOLAR_AGENT,*args,**kwargs)

    async def wenku(self,*args,**kwargs):
        '''
        文库
        '''
        return await self.run(agent_id=AgentID.BOCHA_WENKU_AGENT,*args,**kwargs)
