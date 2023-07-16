import streamlit as st
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from streamlit_chat import message
import openai

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": st.secrets.AppSettings.chatbot_setting}
    ]

# 認証チェック関数
def authenticate():
    client_id = "st.secrets.AuthSettings.googleclientid"  # Google OAuth2.0のクライアントIDを指定してください
    st.write("認証中...")
    credentials, _ = google.auth.default()

    if credentials and credentials.valid:
        id_info = id_token.verify_oauth2_token(credentials.token, Request(), client_id)
        if id_info:
            st.write("認証に成功しました！")
            return True
    else:
        st.write("認証に失敗しました。再試行してください。")

    st.write("OAuth認証を開始します...")
    auth_url, _ = credentials.authorization_url("https://accounts.google.com/o/oauth2/auth", access_type="offline")

    if "code" not in st.session_state:
        st.write(f"[Googleで認証する]({auth_url})")
    else:
        try:
            credentials.fetch_token(
                "https://accounts.google.com/o/oauth2/token",
                authorization_response=st.session_state["code"],
                client_secret="st.secrets.AuthSettings.googleclientsecret"  # Google OAuth2.0のクライアントシークレットを指定してください
            )

            st.session_state.pop("code")  # クリア

            id_info = id_token.verify_oauth2_token(credentials.token, Request(), client_id)
            if id_info:
                st.write("認証に成功しました！")
                return True
        except Exception as e:
            st.write(f"認証エラー: {e}")

    return False


# チャットボットとやりとりする関数
def communicate():
    if not authenticate():
        return

    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=1.2
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去


# ユーザーインターフェイスの構築
st.title("I'm ChotGPT!!!")
st.write("ChatGPT APIを使ったチャットボットです。")

user_input = st.text_input("できるだけ頑張ります。以下にテキストをどうそ。", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]

    for message in reversed(messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂"
        if message["role"] == "assistant":
            speaker = "🤖"

        st.write(speaker + ": " + message["content"])
