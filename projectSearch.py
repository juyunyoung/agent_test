
from langchain import PromptTemplate, LLMChain
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from dbSearch import DBSearchManager
from dotenv import load_dotenv
import os
import pandas as pd
import markdown
from langchain_anthropic import ChatAnthropic

class ProjectSearchTool:
    load_dotenv()
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProjectSearchTool, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        # self.llm = AzureChatOpenAI(
        #         api_key = os.getenv("AZURE_OPENAI_API_KEY_4O"),  
        #         api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
        #         azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4O")
        #     )
        self.llm = ChatOpenAI(model='gpt-4o')     
        #self.llm = ChatAnthropic(model='claude-3-opus-20240229')
    def get_project_search(self, input_text:str ) -> str:
        '''
        사용자가 입력한 질문에  대하여 프로젝트와 관련된 전체적인 정보를 검색 할수 있는 함수 
        :param question: 사용자가 입력한 질문내용
        '''
        db_search = DBSearchManager()        
        db_search_result = db_search.get_search_result(question= input_text)
        # Markdown을 HTML로 변환     
        return self._regenerate_answer(db_search_result)

    def _regenerate_answer(self,  markdown_table):
        html_content = markdown.markdown(markdown_table, extensions=["tables"])
        # PromptTemplate 정의
        prompt = PromptTemplate(
            input_variables=[ "markdown_table"],
            template="{markdown_table} 컬럼명을 한글로 변환해 주세요. 스키마에 없을 경우 한국 말로 적절하게 번역해 주세요. 변환한 markdown_table의 결과 값만 주세요 "
        )

        # LLMChain 생성
        answer_chain = LLMChain(
            llm=self.llm,
            prompt=prompt
        )
        answer_query = answer_chain.run(markdown_table=markdown_table)              

        return answer_query
    
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
    