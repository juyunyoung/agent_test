from google.oauth2 import service_account
from langchain.document_loaders import BigQueryLoader
from google.cloud import bigquery
from langchain.prompts import PromptTemplate
from langchain.schema import format_document
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
import pandas as pd

class DBSearchManager:
    load_dotenv()
    _loader = None  # 클래스 레벨 로더 인스턴스
    _instance = None  # 싱글톤 인스턴스

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 초기화 상태 확인
        if not hasattr(self, '_initialized'):
            self.credentials = service_account.Credentials.from_service_account_file(
                os.getenv("SERVICE_ACCOUNT_FILE")
            )
            self.llm = AzureChatOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY_4O"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_4O")
            )
            self.client = bigquery.Client(credentials=self.credentials)
            self._initialized = True

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = self._load_data()
        return self._data

    def _load_data(self):
        if DBSearchManager._loader is None:
            query = """
            SELECT table_name, ddl 
            FROM `corded-forge-433107-v9.PROJECTCONT.INFORMATION_SCHEMA.TABLES`
            """
            DBSearchManager._loader = BigQueryLoader(
                query=query,
                project="corded-forge-433107-v9",
                metadata_columns=["table_name"],
                page_content_columns=["ddl"],
                credentials=self.credentials
            )
        return DBSearchManager._loader.load()

    def get_search_result(self, question: str, markdown_converter: bool = True) -> str:
        # 기존 get_search_result 메서드 구현 유지
        chain = (
            {
                "content": lambda docs: "\n\n".join(
                    [format_document(doc, PromptTemplate.from_template("{page_content}")) for doc in docs]
                ),
            } 
            | PromptTemplate.from_template(question+"의 정보를 검색할 수 있는 쿼리를 작성해주세요. 쿼리 내용만 리턴해주세요:\n\n{content}")
            | self.llm
        )
        try:        
            result = chain.invoke(self.data)        
            print("result::", result)
#            search_query = result.content   #antropic return
            search_query = result.content.split('```')[1].strip('sql')   #openAI return
            print("search_query::", search_query)
            db_search_result = self.client.query(search_query).result().to_dataframe()
            print("db_search_result::", db_search_result)
            if markdown_converter:
                return db_search_result.to_markdown(index=False)
            else:
                return db_search_result
        except Exception as e:
            print(f"Exception Error: {e}")
            return "DB 검색 중 오류가 발생했습니다. 쿼리문을 다시 만들어 보세요"
