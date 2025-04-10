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
    int_to_weather = {
        "0": "맑음",
        "1": "비",
        "2": "비/눈",
        "3": "눈",
        "5": "빗방울",
        "6": "빗방울눈날림",
        "7": "눈날림"
    }    
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
    def get_weather_search(self, input_text: str) -> str:
        '''
        지역의 날씨를 검색하여 결과를 리턴하는 함수
        :param input_text: 사용자가 날씨 정보를 알기 원하는 입력한 질문
        '''
        db_search = DBSearchManager()
        user_question = f"{input_text}의 정보를 알기위해 해당 프로젝트의 주소를 검색해 주세요."
        db_search_result = db_search.get_search_result(question=user_question,markdown_converter=False)
        if len(db_search_result)<=0:
            return "해당 프로젝트의 주소를 찾을 수 없습니다."
        else:    
            address = db_search_result[0:1][['address']].to_string(index=False, header=False)
            print(f"address::{address}")                
            # 주소를 위성 x, y 좌표로 변환하는 로직을 구현합니다.
        return self._regenerate_answer( address)

    def _regenerate_answer(self, address):
        geo_key = os.getenv("GOOGLE_GEO_API_KEY")
        geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={geo_key}"

        response = requests.get(geo_url)
        data = response.json()
        print(f"location  data:::{data}")
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            lat = str(location["lat"])
            lng = str(location["lng"])

        WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

        params ={'serviceKey' : WEATHER_API_KEY,                 
                'numOfRows' : '10', 
                'dataType' : 'JSON', 
                'base_time' : '0500', 
                'base_date' : self._get_current_date(), 
                'nx' : lat[0:lat.index('.')] , 
                'ny' : lng[0:lng.index('.')]}


        return self._request_weather_info(params)


    def _get_current_date(self):        
        current_date = arrow.now('Asia/Seoul')        
        date_of_today = current_date.format("YYYYMMDD", locale="ko_kr")
        return date_of_today

    def _get_current_hour(self):
        now = datetime.now()
        return datetime.now().strftime("%H%M")



    def _request_weather_info(self, params):
        url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst' # 단기예보
        
        # 값 요청 (웹 브라우저 서버에서 요청 - url주소와 파라미터)
        response = requests.get(url, params=params)        
        data = response.json()
        items = data['response']['body']['items']['item']        
        PCP = list(filter(lambda x: x['category'] == 'PCP' , items))[0]['fcstValue']#강수확율
        SKY = list(filter(lambda x: x['category'] == 'SKY' , items))[0]['fcstValue']#하늘 상태
        TMP = list(filter(lambda x: x['category'] == 'TMP' , items))[0]['fcstValue']#온도
        
        return f"강수확율은  {PCP},  기온은 {TMP}, 하늘은 {self.int_to_weather[SKY]} 입니다. " 
                
        
        
        