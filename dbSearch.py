from google.oauth2 import service_account
from langchain.document_loaders import BigQueryLoader
from google.cloud import bigquery
from langchain.prompts import PromptTemplate
from langchain.schema import format_document
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from sql_examples import sql_examples
import os
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, FewShotChatMessagePromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
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
        print("DBSearchManager.__init__")
        if not hasattr(self, '_initialized'):
            self.credentials = service_account.Credentials.from_service_account_file(os.getenv("SERVICE_ACCOUNT_FILE"))
            # self.llm = AzureChatOpenAI(
            #     api_key=os.getenv("AZURE_OPENAI_API_KEY_4O"),
            #     api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_4O")
            # )
            #self.llm = ChatOpenAI(model='gpt-4o') 
            self.llm = ChatAnthropic(model='claude-3-opus-20240229')

            self.client = bigquery.Client(credentials=self.credentials)
            self._initialized = True    
    

    @property
    def data(self):
        print("DBSearchManager.data")
        if not hasattr(self, '_data'):
            load_data = self._load_data()
            
            content = lambda load_data: "\n\n".join(
                    [format_document(doc, PromptTemplate.from_template("{page_content}")) for doc in load_data]
                )            
            self._data = content(load_data)
            
        return self._data

    def _load_data(self):
        print("DBSearchManager._load_data")
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
    
    
    def get_search_result(self, question:str, markdown_converter:bool = True ):
        print("DBSearchManager.get_search_result")
        
        # chain = (
        #     {
        #         "content": lambda docs: "\n\n".join(
        #             [format_document(doc, PromptTemplate.from_template("{page_content}")) for doc in docs]
        #         ),
                
        #     } | PromptTemplate.from_template(question+"의 정보를 검색할수 있는 쿼리를 작성해줘 query 의 내용만 리턴 해주세요. :\n\n{content} ")
        #     | self.llm
        # )     
        
        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{answer}"),
            ]
        )
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=sql_examples,
        )
        print("system_prompt_text")
        system_prompt = SystemMessagePromptTemplate.from_template(
            f"""당신은 SQL 쿼리문을 작성하는 전문가입니다
            아래의 Table schema를 바탕으로 사용자의 질문에 대한 SQL 쿼리문을 작성해 주세요            
            정보가 충분하지 않을 경우 작성할수 없음 이라고 답변해 주세요 
            쿼리만 리턴 해 주세요            
            \n\n:
            {self.data}"""
        )
        

        #print(system_prompt_str)
        qa_prompt = ChatPromptTemplate.from_messages(
            [
               system_prompt,
               few_shot_prompt,
               ("human", "{input}"),
            ]
        )
        #qa_prompt = qa_prompt.format(question=question)
        #chain = create_stuff_documents_chain(llm=self.llm, prompt=qa_prompt)
        #chain = qa_prompt.format_messages({"input":question, "context":self.data})|self.llm
        print("create_stuff_documents_chain")
        chain = qa_prompt|self.llm
        
        try:        
            #result = chain.invoke(self.data)                    
            print("question::",question)
            result = chain.invoke({"input": question})
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
