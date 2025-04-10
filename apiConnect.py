from langchain import PromptTemplate, LLMChain
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from dbSearch import DBSearchManager
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import arrow
from langchain_anthropic import ChatAnthropic

class WeatherTool:
    load_dotenv()
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WeatherTool, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        # self.llm = AzureChatOpenAI(
        #         api_key = os.getenv("AZURE_OPENAI_API_KEY_4O"),  
        #         api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
        #         azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4O")
        #     )
        self.llm = ChatOpenAI(model='gpt-4o') 
        #self.llm = ChatAnthropic(model='claude-3-opus-20240229')
    def address_api_connect(self, input_text: str) -> str:
        '''
        사용자가 입력한 정보를 바탕드로 주소를 추가하는 API와 연동하는 함수 
        :param input_text: 사용자가 입력한 연동하려고 하는 사용자가 입력한 문장
        '''
        address_data = self.llm.invoke(f"{input_text}의 문장을 분석하여 json 형식인 'name': name, 'add': add, 'tel': tel, 'email': email 으로 만들어서 반환해 주세요 결과만 반환해주세요"  ).content.split('```')[1].strip('json')    
        return self._regenerate_answer( address_data)

    def _regenerate_answer(self, address_data):
        address_url = f"http://127.0.0.1:5000"
  
        
        # POST 요청 보내기
        response = requests.post(address_url, json=address_data)
        if response.status_code == 200:
            text ="POST request successful."
            result = response.text
        else:
            text ="POST request failed with status code:"+ response.status_code
            result = response.text

        return  f"{text}, result: {result} "
        
        

        return self._request_weather_info(params)



        
        
        