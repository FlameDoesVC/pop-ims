import json
import os

from inquirer import errors
import inquirer

from pony.orm import *


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_as_table(data):
    if len(data) == 0:
        print("No entries found")
        return
    header = list(data[0].keys())
    rows = [list(x.values()) for x in data]
    column_widths = [max(len(str(row[i])) for row in rows) for i in range(len(header))]
    header_widths = [len(column) for column in header]
    column_widths = [
        max(header_widths[i], column_widths[i]) for i in range(len(header))
    ]
    for i, column in enumerate(header):
        print(f"{column:<{column_widths[i]}}", end=" | ")
    print()
    for i, column in enumerate(header):
        print(f"{'-' * column_widths[i]}", end="-+-")
    print()
    for row in rows:
        for i, column in enumerate(row):
            print(f"{column:<{column_widths[i]}}", end=" | ")
        print()


def validate(type, value_name):
    def validator(answers, value):
        if len(value) == 0:
            raise errors.ValidationError("", reason=f"{value_name} must not be empty")
        if type == "int":
            try:
                value = int(value)
            except Exception:
                raise errors.ValidationError(
                    "", reason=f"{value_name} must be a valid integer"
                )
        elif type == "float":
            try:
                value = float(value)
            except Exception:
                raise errors.ValidationError(
                    "", reason=f"{value_name} must be a valid float"
                )
        elif type == "str":
            if not isinstance(value, str):
                raise errors.ValidationError(
                    "", reason=f"{value_name} must be a valid string"
                )
            if len(value) == 0:
                raise errors.ValidationError(
                    "", reason=f"{value_name} must not be empty"
                )
        return True

    return validator


def titlecase(text):
    return " ".join([word.capitalize() for word in text.split()])


def generate_menu(menu, table_name, dto):
    def run_menu():
        while True:
            pause = True
            clear_screen()
            print(titlecase(table_name))
            print("-" * len(table_name))
            dto.show()
            print()

            hints = {}
            for menu_item in menu:
                hints[menu_item["short"]] = menu_item["text"]
            hints["Back"] = "Go back to the main menu"
            hints["Exit"] = "Exit the program"

            answers = inquirer.prompt(
                [
                    inquirer.List(
                        "action",
                        # message=f"Manage {table_name}",
                        message="Choose an option",
                        choices=[menu_item["short"] for menu_item in menu]
                        + ["Back", "Exit"],
                        hints=hints,
                        carousel=True,
                    )
                ]
            )
            if answers is None:
                pause = False
                return

            if answers["action"] == "Back":
                pause = False
                return
            elif answers["action"] == "Exit":
                pause = False
                exit(0)

            menu_item = next(
                menu_item
                for menu_item in menu
                if menu_item["short"] == answers["action"]
            )
            if "pause" in menu_item:
                pause = menu_item["pause"]
            menu_item["action"]()

            if pause:
                input("\nPress Enter to continue...")

    return run_menu


@db_session
def validate_field(obj, key):
    all_objs = select(obj for obj in obj)[:].to_list()

    def check_field(_, value):
        if value not in [str(x.to_dict()[key]) for x in all_objs]:
            raise errors.ValidationError("", reason=f"Invalid {key} : {value}")
        return True

    return check_field
