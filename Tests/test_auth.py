from UI.auth import register_user, login_user

print("=== 註冊測試 ===")
print(register_user("Webb", "webb@example.com", "123456"))

print("\n=== 登入測試 ===")
print(login_user("webb@example.com", "123456"))