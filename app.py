# ====================
# Streamlit home page
# ====================
import streamlit as st
import book_request
from auth import login_user, register_user # 這兩個是登入、註冊的functions

# ===================
# user 手動輸入 isbn??? 改名成import_book_by_isbn()如何??
# ===================   
def update_isbn():
    isbn = st.session_state.user_input
    st.session_state.book_data = book_request.request_book_data_with_returning_value(isbn)


# ====================
# session state 初始化 => 為了之後紀錄狀態(似建立空箱放入值)
# ====================
# 初始狀態都不會在
if 'book_data' not in st.session_state:
    st.session_state.counter = ''

st.header("type in the isbn and the system will find the book from open library!")
st.text_input(label="ISBN", key='user_input', placeholder="Enter ISBN")
st.button(label="Submit",on_click=update_isbn)
st.text_area(label="Book data", key='book_data', placeholder="Will show book data here", height=2000)

if "user_id" not in st.session_state:
    st.session.user_id = None # 登入成功會將id存入
if "loged_in" not in st.session_state:
    st.session.loged_in = False # 尚未登入
if "user_email" not in st.session_state:
    st.session.user_email = "" # 登入成功會將email放入
if "user_name" not in st.session_state:
    st.session.user_name = "" # 登入成功會將名字放入

# ====================
# 側邊選單
# ===================
# 先叫做選單
menu = st.sidebar.selectbox("選單", ["註冊", "登入", "尋找書籍"]) # 單選
# 若尋找不到，會需要 user 用 isbn 新增

# =================
# 註冊頁 
# =================
if menu == "註冊":
    # 選擇註冊就到「註冊頁面」

    st.header("註冊帳號")
    # 顯示頁面大標題「註冊帳號」

    name = st.text_input("姓名")
    # 建立一個文字輸入框，標籤是「姓名」

    email = st.text_input("電子信箱")
    # 建立另一個文字輸入框，標籤是「電子信箱」

    password = st.text_input("密碼", type="password")
    # 建立密碼輸入框
    # type="password" 代表輸入內容會以隱藏形式顯示（例如 ****）
    
    if st.button("註冊"):
        # 建立一顆按鈕，顯示文字是「註冊」(按下就執行)

        # 註冊邏輯判斷(任一欄不得為空)
        if not name or not email or not password:
            # 如果 name、email、password 任一欄為空
            # not 代表空字串會被視為 False

            st.warning("請完整填寫所有欄位")
            # 顯示警告訊息，提醒使用者要把欄位填完整

        else:
            # 反之，三個欄位都有值

            success, message = register_user(name, email, password)
            # 呼叫 auth.py 裡的 register_user()
            # 它會回傳兩個東西：
            # success：True/False，代表註冊成功或失敗
            # message：要顯示給使用者看的訊息(成功/失敗)

            if success:
                st.success(message) # 顯示成功訊息
            else:
                st.error(message) # 顯示錯誤訊息，例如 email 已被註冊

# ==========
# 登入頁
# ==========
elif menu == "登入":
    # 如果側邊欄選的是「登入」
    # 就顯示登入頁面

    st.header("登入系統")
    # 顯示頁面標題「登入系統」

    email = st.text_input("電子信箱")
    # 建立 email 輸入框
    # 使用者輸入的 email 會存進變數 email

    password = st.text_input("密碼", type="password")
    # 建立密碼輸入框
    # type="password" 會把內容隱藏起來(如: ****)
    # 使用者輸入的密碼存進變數 password

    if st.button("登入"):
        # 建立「登入」按鈕
        # 如果按下，就執行以下內容

        if not email or not password:
            # 如果 email 或 password 有任一欄是空的

            st.warning("請輸入電子信箱與密碼")
            # 顯示警告訊息

        else:
            # 如果 email 和 password 都有填

            success, result = login_user(email, password)
            # 呼叫 auth.py 裡的 login_user()
            # 傳入 email 和 password
            # 它會回傳：
            # success：True/False
            # result：若成功，回傳歡迎某某使用者；若失敗，回傳對應的失敗原因

            if success:
                # 如果 success 是 True，表示登入成功

                st.session_state.logged_in = True
                # 把登入狀態記成 True
                # 之後系統就知道這個使用者目前是已登入狀態

                st.session_state.user_name = result["name"]
                # 把登入者姓名存進 session_state

                st.session_state.user_email = result["email"]
                # 把登入者 email 存進 session_state

                st.session_state.user_id = result["id"]
                # 把登入者 id 存進 session_state

                st.success(f"登入成功，歡迎 {result['name']}！")
                # 顯示登入成功訊息，並歡迎使用者

            else:
                # 如果 success 是 False，表示登入失敗

                st.error(result)
                # 顯示錯誤訊息
                # 例如「查無此帳號」或「密碼錯誤」            

# ==========
# 尋找書籍
# ==========

# Front end to be edited