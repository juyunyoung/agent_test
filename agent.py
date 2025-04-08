from langchain.agents import initialize_agent, Tool, AgentType
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from weather import WeatherTool
from projectSearch import ProjectSearchTool
from managerEmail import ManagerMailTool
from webSearch import WebSearchTool
import os
import pandas as pd
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()
    
llm = AzureChatOpenAI(
    api_key = os.getenv("AZURE_OPENAI_API_KEY_4O"),  
    api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4O")
)
#llm = ChatOpenAI(model='gpt-4o') 
#사용자가 입력한 질문에  대하여 프로젝트와 관련된 전체적인 정보를 검색 할수 있는 함수 
def get_project_search( input_text:str ) -> str:
    """
    사용자가 입력한 질문에  대하여 프로젝트와 관련된 전체적인 정보를 검색 할수 있는 함수 
    :param question: 사용자가 입력한 질문내용
    """       
    project_search = ProjectSearchTool()        
    print(f"input_text::{input_text}")
    db_search_result = project_search.get_project_search(question= input_text)        
    return  db_search_result

#사용자가 입력한 질문을 바탕으로 메일을 작성한다."
def get_web_search( input_text:str ) -> str:
    """
    사용자의 질문에 대하여 프로젝트의 정보를 바탕으로 web 검색을 수행하는 함수
    :param input_text:  사용자가 입력한 질문내용

    """
    web_search_manager = WebSearchTool()        
    db_search_result = web_search_manager.get_web_search(input_text= input_text)        
    return  db_search_result

#사용자가 입력한 질문을 바탕으로  존재하는 주소의 날씨 정보를 검색합니다.
def get_weather_search( input_text:str ) -> str:
    """
    지역의 날씨를 검색하여 결과를 리턴하는 함수
    :param input_text: 사용자가 날씨 정보를 알기 원하는 입력한 질문
    """
    weatherTool = WeatherTool()        
    db_search_result = weatherTool.get_weather_search(input_text= input_text)        
    return  db_search_result

def request_answer( question) -> str:
    weather_tool = Tool(
        name="get_weather_search",
        title="Weather Search",
        func=get_weather_search,
        description="사용자가 입력한 프로젝트명이 존재하는 위치의 현재 날씨 정보를 검색합니다."
    )
    project_search_tool = Tool(
        name="get_project_search",
        title="Project Information Search",
        func=get_project_search,
        description="사용자가 입력한 질문을 param으로 사용. 질문에 대하여 db를 검색하여 프로젝트 정보를 검색 할수 있는 툴"
    )
    web_search_tool = Tool(
        name="get_web_search",
        title="WEB search base on Project Information",
        func=get_web_search,
        description="사용자가 입력한 질문을 param으로 사용. 질문에 대하여 프로젝트 정보를 바탕으로 web에서 검색. 프로젝트 리턴값은  타이틀, URL 링크, 요약 정보를 제공한다."
    )


    tools=[weather_tool,    # 날씨 검색 도구 추가     
           web_search_tool,    # 날씨 검색 도구 추가
           project_search_tool, # 프로젝트 검색 도구 추가  
           ]
    #에이전트 초기화
    # agent = initialize_agent(
    #     tools=[weather_tool,    # 날씨 검색 도구 추가                   
    #            project_search_tool],# 프로젝트 검색 도구 추가  
    #     llm=llm,
    #     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    #     handle_parsing_errors=True,        
    #     verbose=True  # 상세 출력 활성화
    # )
    # tools=[get_weather_search,    # 날씨 검색 도구 추가               
    #        get_project_search],# 프로젝트 검색 도구 추
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. "
                "agent 에서 제공하는 가능한한 많은 정보를 보여주세요. 대답은 반드시 한국어로만 해주세요. 답변을 요약하지 않아도 됩니다. 너무 오래 생각하지 마세요. 다음 액션이 생각나지 않으면 에이전트가 제공한 답변을 주세요. web_search_tool은 결과를 사용자 질문과 관련이 없는 내용이 검색 될수 있으니 결과가 검색되면 꼭 답변을 작성해주세요.",
            ),                
            ("human", "{input}"),               
            ("placeholder", "{agent_scratchpad}"),
        ]
    )        
    agent = create_tool_calling_agent(llm, tools, prompt)
    # AgentExecutor 생성
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        #max_iterations=30,
        #max_execution_time=20,
        handle_parsing_errors=True,
    )


    #result = agent.run(question)       
    result = agent_executor.invoke({"input": question})
    print(f"result::{result}")
#    return result
    return result['output'] if isinstance(result, dict) else result