# log in/out logic
# Webb's responsibility
import bcrypt # encrypt
from DB_Stuff.db_connect import get_connection

# 1、密碼轉換: 將使用者原始密碼轉換為雜湊後的密碼
def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw( 
        password.encode("utf-8"), # bcrypt 吃的是 bytes，不是一般 Python 字串 str
        bcrypt.gensalt() # 產生salt，讓想同密碼每次hash可能不同
    )
    return hashed_bytes.decode("utf-8") # 轉回 str 

# 2、比對密碼: checkpw() 專門驗證密碼
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw( 
        password.encode("utf-8"), # str 轉成 byte
        password_hash.encode("utf-8") # str 轉成 byte
    )

# 3、註冊: 將新註冊資料放入資料庫
def register_user(name: str, email: str, password: str):
    # # The bcrypt algorithm only handles passwords up to 72 characters
    # if len(password) > 72:

    # 為放入資料庫，優先連線
    connection = get_connection() # 呼叫 connect 資料夾的函式
    if connection is None:
        return False, "資料庫連線失敗"

    # cursor是游標，對資料庫下指令的工具
    cursor = connection.cursor(dictionary=True) # 採用字典取值方便，如:users[email]=webb@...

    # (1) 先檢查 email 是否已存在
    # execute() 執行 sql 指令
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,)) # (email,)是真正的email值，單一元素這樣寫
    existing_user = cursor.fetchone() # fetchone(): 抓查詢結果的第一筆資料
    
    # 重複
    if existing_user: 
        cursor.close()
        connection.close()
        return False, "此電子信箱已被註冊"
    
    # 未重複
    # (2) 密碼做 hash
    # 寫入 users table
    password_hash = hash_password(password)

    cursor.execute(
        """
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
        """,
        (name, email, password_hash)
    )
    connection.commit() # 將記錄正式存入資料庫

    cursor.close()
    connection.close()
    return True, "註冊成功"

# 4、登入: 確認使用者輸入 email、pw 是否正確
def login_user(email: str, password: str):
    # 需要抓 DB 的資料比對，故須先連線
    connection = get_connection()
    if connection is None:
        return False, "資料庫連線失敗"

    cursor = connection.cursor(dictionary=True)
    
    # (1) 先比對帳號(email)
    cursor.execute(
        """
        SELECT id, name, email, password_hash
        FROM users
        WHERE email = %s
        """,
        (email,)
    )
    user = cursor.fetchone()

    cursor.close()
    connection.close()
    
    # 帳號不存在
    if not user: # user["email"] 預設 null
        return False, "查無此帳號"
    
    # 帳號存在
    # (2) 再比較密碼
    if verify_password(password, user["password_hash"]): # user["password_hash"] 取 DB 的 pw_hash
        return True, "歡迎", user["name"]

    return False, "密碼錯誤"