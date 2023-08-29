import streamlit as st
import openai

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# プロンプトのセレクトボックスを作成
prompt = st.selectbox(
    "プロンプトを選んでください：",
    options=["真面目に500文字に要約", "ギャル口調に変換"]
)

if prompt == "真面目に500文字に要約":
    st.session_state["messages"].append({"role": "system", "content": st.secrets.AppSettings.chatbot_setting1})
elif prompt == "ギャル口調に変換":
    st.session_state["messages"].append({"role": "system", "content": st.secrets.AppSettings.chatbot_setting2})

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=1.1
    )  

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去


# ユーザーインターフェイスの構築
st.title("I'm ChatGPT!!!")
st.write("ChatGPT APIを使ったチャットボットです。")


user_input = st.text_input("できるだけ頑張ります。以下にテキストをどうそ。", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]

    for message in reversed(messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂"
        if message["role"]=="assistant":
            speaker="🤖"

        st.write(speaker + ": " + message["content"])
