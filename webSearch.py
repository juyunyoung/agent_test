from langchain import PromptTemplate, LLMChain
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from dbSearch import DBSearchManager
from dotenv import load_dotenv
import os
import requests

from langchain_community.tools.tavily_search import TavilySearchResults

class WebSearchTool:
    load_dotenv()
    int_to_weather = {
        "0": "맑음",
        "1": "비",
        "2": "비/눈",
        "3": "눈",
        "5": "빗방울",
        "6": "빗방울눈날림",
        "7": "눈날림"
    }    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebSearchTool, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
                api_key = os.getenv("AZURE_OPENAI_API_KEY_4O"),  
                api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4O")
            )
        #self.llm = ChatOpenAI(model='gpt-4o') 
    def get_weather_search(self, input_text: str) -> str:
        '''
        지역의 날씨를 검색하여 결과를 리턴하는 함수
        :param input_text: 사용자가 날씨 정보를 알기 원하는 입력한 질문
        '''
        db_search = DBSearchManager()
        user_question = f"{input_text}의 정보를 알기위해 해당 프로젝트의 정보를 검색해 주세요."
        db_search_result = db_search.get_search_result(question=user_question,markdown_converter=False)
        if len(db_search_result)<=0:
            return "해당 프로젝트의 주소를 찾을 수 없습니다."
        else:    
            project_info = db_search_result[0:1][['project_info']].to_string(index=False, header=False)
            print(f"project_info::{project_info}")                
            # 주소를 위성 x, y 좌표로 변환하는 로직을 구현합니다.
        return self._regenerate_answer( project_info)

    def _regenerate_answer(self, project_info):
        search = TavilySearchResults(k=5)
        

        return search.invoke("{project_info} 의 내용과 관련된 웹사이트를 검색해 주세요. 웹사이트의 제목과 링크를 리턴 해주세요.")


        
        
        