from langchain.agents import initialize_agent, Tool, AgentType
from langchain_openai import AzureChatOpenAI
from weather import WeatherTool
from projectSearch import ProjectSearchTool
from managerEmail import ManagerMailTool
import os
import pandas as pd
from dotenv import load_dotenv
from dbSearch import DBSearchManager


class AgentManager:
    load_dotenv()
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AgentManager, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
                api_key = os.getenv("AZURE_OPENAI_API_KEY_4O"),  
                api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4O")
            )
    #사용자가 입력한 질문에  대하여 프로젝트와 관련된 전체적인 정보를 검색 할수 있는 함수 
    def _get_project_search(self, input_text:str ) -> str:
        project_search = ProjectSearchTool()        
        print(f"input_text::{input_text}")
        db_search_result = project_search.get_project_search(question= input_text)        
        return  db_search_result

    #사용자가 입력한 질문을 바탕으로 메일을 작성한다."
    def _get_send_email(self, input_text:str ) -> str:
        mail_manager = ManagerMailTool()        
        db_search_result = mail_manager.get_send_email(input_text= input_text)        
        return  db_search_result
    
    #사용자가 입력한 질문을 바탕으로  존재하는 주소의 날씨 정보를 검색합니다.
    def _get_weather_search(self, input_text:str ) -> str:
        weatherTool = WeatherTool()        
        db_search_result = weatherTool.get_weather_search(input_text= input_text)        
        return  db_search_result

    def request_answer(self, question) -> str:
        weather_tool = Tool(
            name="Weather Search",
            func=self._get_weather_search,
            description="사용자가 입력한 프로젝트명이 존재하는 위치의 현재 날씨 정보를 검색합니다."
        )

        email_tool = Tool(
            name="Send Email",
            func=self._get_send_email,
            description="이메일 전송요으로 사용. 사용자가 입력한 질문을 param으로 사용. 사용자가 입력한 프로젝트명과 메니저 종류에 따라 메일 주소를 검색합니다."
        )

        project_search_tool = Tool(
            name="Project Information Search",
            func=self._get_project_search,
            description="사용자가 입력한 질문을 param으로 사용. 질문에 대하여 프로젝트 상세 정보를 검색 할수 있는 함수  "
        )

        # 에이전트 초기화
        agent = initialize_agent(
            tools=[weather_tool,    # 날씨 검색 도구 추가
                   email_tool,     # 이메일 전송 도구 추가
                   project_search_tool],# 프로젝트 검색 도구 추가  
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            prompt="agent 에서 제공하는 전체 답변을 가공하지 말고 대답해주세요. 대답은 한글로 해주세요. 답변을 요약하지 않아도 됩니다. ",                   
            verbose=True  # 상세 출력 활성화
        )

        result = agent.run(question)       
        print(f"result::{result}")
        return result