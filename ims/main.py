import time
from ims.models.order import orders_menu
from ims.reports import reports_menu
from ims.utils import clear_screen, print_as_table
from pony import orm

from bcrypt import hashpw, gensalt, checkpw
import inquirer
from inquirer import errors

from ims.db import User

from ims.models.item import items_menu


current_user = None
DEBUG = False


class UserDTO:
		@staticmethod
		@orm.db_session
		def show():
				users = orm.select(user for user in User)[:]
				print_as_table(
						[
								{"ID": user.id, "Username": user.username, "Role": user.role}
								for user in users
						]
				)

		@staticmethod
		@orm.db_session
		def login():
				users = orm.select(user for user in User)
				if len(users) == 0:
						print("No users found. Please register a user first.")
						UserDTO.register(first_register=True)
						return
				saved_username = None

				while True:

						answers = inquirer.prompt(
								[
										inquirer.Text(
												"username",
												message="Enter your username",
												default=saved_username,
										),
										inquirer.Password("password", message="Enter your password"),
								]
						)
						if answers is None:
								exit(0)

						user = orm.select(
								user for user in User if user.username == answers["username"]
						).first()
						if user is None:
								checkpw(answers["password"].encode(), gensalt())
								print("Invalid username or password")
								saved_username = answers["username"]
								continue
						if not checkpw(answers["password"].encode(), user.hash.encode()):
								print("Invalid username or password")
								continue
						global current_user
						current_user = user
						print(f"Welcome {user.username}!")
						return True

		@staticmethod
		@orm.db_session
		def register(first_register=False):

				def validate_password(answers, password2):
						password = answers["password1"]
						if len(password) == 0:
								raise errors.ValidationError("", reason="You must enter a password")
						if password != password2:
								raise errors.ValidationError("", reason="Passwords do not match")
						return True

				answers = inquirer.prompt(
						[
								inquirer.Text("username", message="Enter your username"),
								inquirer.Password("password1", message="Enter your password"),
								inquirer.Password(
										"password2",
										message="Re-enter your password",
										validate=validate_password,
								),
								(
										inquirer.Checkbox(
												"role",
												message="Enter your role",
												choices=["admin", "staff"],
												default=["admin", "staff"],
												locked=["admin", "staff"],
										)
										if first_register
										else inquirer.Checkbox(
												"role",
												message="Enter your role",
												choices=["admin", "staff"],
												default=["staff"],
												locked=["staff"],
										)
								),
						]
				)

				if answers is None:
						return

				username = answers["username"]
				password = answers["password1"]
				if password != answers["password2"]:
						print("Passwords do not match!")
						UserDTO.register()
						return

				role = ",".join(answers["role"])
				salt = gensalt()
				hash = hashpw(password.encode(), salt).decode()
				User(username=username, hash=hash, role=role)
				orm.commit()
				print(f"User '{username}' created successfully!")
		
		@staticmethod
		@orm.db_session
		def edit():
				users = orm.select(user for user in User)[:]
				answers = inquirer.prompt(
						[
								inquirer.List(
										"user",
										message="Select a user to edit",
										choices=[user.username for user in users],
								),
						]
				)
				if answers is None:
						return
				user = orm.select(user for user in User if user.username == answers["user"]).first()

				def validate_password(answers, password2):
						password = answers["password"]
						if len(password) == 0:
								return True
						if password != password2:
								raise errors.ValidationError("", reason="Passwords do not match")
						return True

				answers = inquirer.prompt(
						[
								inquirer.Text(
										"username",
										message="Enter the new username",
										default=user.username,
								),
								inquirer.Password("password", message="Enter the new password (leave blank for same as old password)", default=""),
								inquirer.Password("password2", message="Re-enter the new password", default="", ignore=lambda answers: answers["password"] == "", validate=validate_password),
								inquirer.Checkbox(
										"role",
										message="Enter the new role",
										choices=["admin", "staff"],
										default=user.role.split(","),
								),
						]
				)
				if answers is None:
						return
				user.username = answers["username"]
				user.role = ",".join(answers["role"])
				if answers["password"] != "":
						salt = gensalt()
						hash = hashpw(answers["password"].encode(), salt).decode()
						user.hash = hash
				orm.commit()
				print(f"User '{answers['username']}' edited successfully")

		@staticmethod
		@orm.db_session
		def delete():
				users = orm.select(user for user in User)[:]
				answers = inquirer.prompt(
						[
								inquirer.List(
										"user",
										message="Select a user to delete",
										choices=[user.username for user in users],
								),
								inquirer.Confirm("confirm", message="Are you sure you want to delete this user?"),
						]
				)
				if answers is None:
						return
				if not answers["confirm"]:
						return
				user = orm.select(user for user in User if user.username == answers["user"]).first()
				user.delete()
				orm.commit()
				print(f"User '{answers['user']}' deleted successfully!")


def login_menu(first_login=False):
		global current_user

		menu = [
				inquirer.List(
						"option", message="Users", choices=["Login", "Register", "Edit", "Delete", "Back", "Exit"],
						hints={
								"Login": "Login to the system as another user",
								"Register": "Register a new user",
								"Edit": "Edit a user",
								"Delete": "Delete a user",
								"Back": "Go back to the main menu",
								"Exit": "Exit the program",
						}
				)
		]

		while True:
				pause = False
				clear_screen()
				if not current_user and first_login:
						UserDTO.login()
						return True
				if current_user and "admin" in current_user.role:
						print("Users")
						print("-----")
						UserDTO.show()
						print()
				if current_user:
						print(f"Logged in as {current_user.username} ({current_user.role})")
						print()
				ans = inquirer.prompt(menu)
				if ans is None:
						return
				choice = (ans["option"]).lower()
				if choice == "login":
						UserDTO.login()
				elif choice == "register":
						pause = True
						if current_user and "admin" not in current_user.role:
								print("You do not have permission to register new users")
						else:
								UserDTO.register()
				elif choice == "edit":
						pause = True
						if current_user and "admin" not in current_user.role:
								print("You do not have permission to edit users")
						else:
								UserDTO.edit()
				elif choice == "delete":
						pause = True
						if current_user and "admin" not in current_user.role:
								print("You do not have permission to delete users")
						else:
								UserDTO.delete()
				elif choice == "back":
						return
				elif choice == "exit":
						exit(0)

				if pause:
						input("Press Enter to continue...")


def main():
		menu = [
				{
						"text": "Items",
						"callback": items_menu,
				},
				{
						"text": "Users",
						"callback": login_menu,
				},
				{
						"text": "Orders",
						"callback": orders_menu,
				},
				{
						"text": "Reports",
						"callback": reports_menu,
				},
		]

		if current_user and "admin" not in current_user.role:
				menu.pop(1)

		while True:
				pause = False
				clear_screen()
				if not current_user:
						login_menu(first_login=True)
						time.sleep(1)
						continue

				answers = inquirer.prompt(
						[
								inquirer.List(
										"action",
										message="Inventory Management System",
										choices=[menu_item["text"] for menu_item in menu] + ["Exit"],
								)
						]
				)
				if answers is None:
						exit(0)

				elif answers["action"] == "Exit":
						exit(0)

				menu_item = next(
						menu_item for menu_item in menu if menu_item["text"] == answers["action"]
				)
				menu_item["callback"]()


if __name__ == "__main__":
		main()
