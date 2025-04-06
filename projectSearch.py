
from langchain import PromptTemplate, LLMChain
from langchain_openai import AzureChatOpenAI
from dbSearch import DBSearchManager
from dotenv import load_dotenv
import os
import pandas as pd
import markdown

class ProjectSearchTool:
    load_dotenv()
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProjectSearchTool, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
                api_key = os.getenv("AZURE_OPENAI_API_KEY_4O"),  
                api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4O")
            )
    
    def get_project_search(self, question:str ) -> str:
        '''
        사용자가 입력한 질문에  대하여 프로젝트와 관련된 전체적인 정보를 검색 할수 있는 함수 
        :param question: 사용자가 입력한 질문내용
        '''
        db_search = DBSearchManager()
        
        db_search_result = db_search.get_search_result(question= question)
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