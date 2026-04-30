from UI.Login.auth import login_reader, register_reader


print("=== Register reader ===")
print(register_reader("Webb", "webb@example.com", "12345678"))

print("\n=== Login reader ===")
print(login_reader("webb@example.com", "12345678"))
