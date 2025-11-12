import os

print("Select Mode:")
print("1. Web Version (Flask)")
print("2. Desktop Version (Tkinter)")

choice = input("Enter choice (1 or 2): ")

if choice == "1":
    os.system("python app.py")
elif choice == "2":
    os.system("python recovery_tool_desktop.py")
else:
    print("Invalid choice.")
