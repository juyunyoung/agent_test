from google.oauth2 import service_account
from langchain.document_loaders import BigQueryLoader
from google.cloud import bigquery
from langchain.prompts import PromptTemplate
from langchain.schema import format_document
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from dotenv import load_dotenv
import os
import pandas as pd

class DBSearchManager:
    load_dotenv()
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBSearchManager, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(os.getenv("SERVICE_ACCOUNT_FILE"))
        self.llm = AzureChatOpenAI(
                        api_key = os.getenv("AZURE_OPENAI_API_KEY_4O"),  
                        api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
                        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4O")
                    )
        # self.llm = ChatOpenAI(model='gpt-4o') 
        self.data = self._get_db_schema()
        self.client = bigquery.Client(credentials=self.credentials)

    def _get_db_schema(self):
        query = """ 
        SELECT table_name, ddl
        from `corded-forge-433107-v9.PROJECTCONT.INFORMATION_SCHEMA.TABLES`
        """

        loader = BigQueryLoader(
            query=query,
            project="corded-forge-433107-v9",
            metadata_columns=["table_name"],
            page_content_columns=["ddl"],
            credentials=self.credentials
        )
        return loader.load()
    
    
    def get_search_result(self, question:str, markdown_converter:bool = True ) -> str:
        chain = (
            {
                "content": lambda docs: "\n\n".join(
                    [format_document(doc, PromptTemplate.from_template("{page_content}")) for doc in docs]
                ),
                
            } | PromptTemplate.from_template(question+"의 정보를 검색할수 있는 쿼리를 작성해줘 query 의 내용만 리턴 해주세요. :\n\n{content} ")
            | self.llm
        )
        try:        
            result = chain.invoke(self.data)        
            search_query = result.content.split('```')[1].strip('sql')
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
