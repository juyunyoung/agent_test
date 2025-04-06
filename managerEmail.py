from langchain_openai import AzureChatOpenAI
from dbSearch import DBSearchManager
from dotenv import load_dotenv
import os
import pandas as pd

class ManagerMailTool:
    load_dotenv()
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ManagerMailTool, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
                api_key = os.getenv("AZURE_OPENAI_API_KEY_4O"),  
                api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4O")
            )

    def get_send_email(self, input_text: str) -> str:
        '''
        프로젝트의 메니저 이메일 주소를 검색하여 결과를 리턴하는 함수
        :param input_text: 사용자가 메일을 보내고자 하는 프로젝트명
    
        '''
        db_search = DBSearchManager()
        user_question = f"{input_text}의 내용을 찾을수 있는 프로젝트명,이메일 주소 , 이름은 뭐야?"
        db_search_result = db_search.get_search_result(question=user_question,markdown_converter=False)
        if len(db_search_result) <= 0:
            return "해당 프로젝트의 메니저 주소를 찾을 수 없습니다."
        elif len(db_search_result) > 2:
            db_search_result = db_search_result[0:1]
            return "해당 프로젝의 담당자 메일이 여러개 검색되었습니다. 프토젝트명, 담당 종류를 명확히 입력해 주세요.."
        else:    
            address = db_search_result[0:1][['email']].to_string(index=False, header=False)
            manager_name = db_search_result[0:1][['name']].to_string(index=False, header=False)
            project_name = db_search_result[0:1][['project_name']].to_string(index=False, header=False)
            print(f"address::{address}, manager_name::{manager_name}")                
            subject = f"{manager_name}담당자님 {project_name} 프로젝트  관련 문의 사항입니다."
            body = f"안녕하세요 {manager_name}님,\n\n{project_name} 프로젝트에 대한 문의 사항이 있습니다.\n\n감사합니다."
            
            mailto_link=f"[이메일 보내기 📧 ](mailto:{address}?subject={subject}&body={body})"
            return mailto_link


