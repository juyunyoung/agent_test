import streamlit as st
import agent as agent
st.set_page_config(page_title="Project Info Search", page_icon="🧞")
st.title("🧞 Project Information Assistant")
st.write("안녕하세요! 프로젝트 관련하여 궁금한 내용을 말씀해주시면, AI가 답변을 드리겠습니다.")
st.write("프로젝트 명은 지역명+프로젝트+4까지의 숫자 입니다. 정보는 영업, 계약, 프로덕트 담당자,주소, 프로젝트 금액, 계약 업체 등입니다.")
st.write("예) 강원도에서 진행중인 프로젝트의 시작일과 종료일을 가르쳐 주세요?")
st.write("&nbsp;" * 7 +"연도별로 도별로  프로젝트의 갯수를 표로 정리해서 주세요")
st.write("&nbsp;" * 7 +"강원도프로젝트1과 계약된 업체의 정보를 가르쳐 주세요 ")
st.write("&nbsp;" * 7 +"강원도프로젝트1 의 영업담당자 정보를 가르쳐 주세요")
st.write("&nbsp;" * 7 +"경상북도프로젝트2 날씨 정보를 가르쳐 주세요 / 날씨 기상청 연동")
st.write("&nbsp;" * 7 +"충청남도프로젝트1 와 관련된 뉴스기사 찾아주세요/web site 검색연동")
st.write("&nbsp;" * 7 +" 🛠️개발중..) /API연동")

if 'message_list' not in st.session_state:
    st.session_state.message_list=[]

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"]) 


if user_question := st.chat_input(placeholder="프로젝트 관련하여 궁금한 내용을 말씀해주세요 "):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role":"user","content":user_question})

    with st.spinner("답변을 생성하는 중입니다."):
        ai_response = agent.request_answer(question=user_question)
        if isinstance(ai_response, str):
            if ai_response.startswith("[이메일 보내기"):
                # 메일 링크인 경우, 클릭 가능한 링크로 표시
                st.markdown(ai_response, unsafe_allow_html=True)
                st.session_state.message_list.append({"role":"ai", "content":ai_response})
            else:    
                with st.chat_message("ai"):
                    st.write(ai_response)
                    st.session_state.message_list.append({"role":"ai", "content":ai_response})

        else:
            # Streamlit에서 HTML을 렌더링하기 위해 markdown 사용
            st.markdown(ai_response, unsafe_allow_html=True)
            st.session_state.message_list.append({"role":"ai", "content":ai_response})


