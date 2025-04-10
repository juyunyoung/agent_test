from langchain import PromptTemplate, LLMChain
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from dbSearch import DBSearchManager
from dotenv import load_dotenv
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_anthropic import ChatAnthropic
class WebSearchTool:
    load_dotenv()
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebSearchTool, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        # self.llm = AzureChatOpenAI(
        #         api_key = os.getenv("AZURE_OPENAI_API_KEY_4O"),  
        #         api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
        #         azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4O")
        #     )
        self.llm = ChatOpenAI(model='gpt-4o') 
        #self.llm = ChatAnthropic(model='claude-3-opus-20240229')

    
    def get_project_info_search(self, input_text: str):
        '''
        사용자의 질문에 대하여 프로젝트의 정보를 검색을 수행하는 함수
        :param input_text: 사용자가 날씨 정보를 알기 원하는 입력한 질문
        '''
        db_search = DBSearchManager()
        user_question = f"{input_text}의 corded-forge-433107-v9.PROJECTCONT.project_basic_info 테이블 에서 project_info를 검색해 주세요."
        db_search_result = db_search.get_search_result(question=user_question,markdown_converter=False)
        if len(db_search_result) <= 0:
             return "해당 프로젝트의 정보를 찾을 수 없습니다."
        else:             
                project_info = db_search_result[0:1]['project_info']
                print(f"project_info::{project_info}")                
                keyword = self.llm.invoke(f"{project_info}의 주요 키워드 4개를 선별하여 단어만 대답해주세요").content    
                return keyword
    
    def get_news_search(self, input_text: str):
        '''
        키워드 로 web 검색을 수행하는 함수. 
        :param input_text: 사용자가 날씨 정보를 알기 원하는 입력한 질문
        '''
        keyword = self.get_project_info_search(input_text)
        print("keyword::", keyword)
        search = TavilySearchResults(k=5)
        query = f"{keyword} 관련된 최신 뉴스를 검색해 주세요"
        print("query::", query)
        tavily_result = search.invoke(query)
        print(f"tavily_result::{tavily_result}")
        if tavily_result:
            result = []
            for item in tavily_result:
                
                result.append({
                    "title": item["title"],
                    "url": item["url"],
                    "content": item["content"]
                    
                })
            return f"사용자가 질문한 {input_text}와 과련된 최신뉴스에 사용되는 키워드는 {keyword} 입니다. ", result
        else:   
            return "인터넷 검색 결과가 없습니다."
        


        
        
        