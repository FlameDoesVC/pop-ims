from pprint import pprint
from pony.orm import *

from ims.db import Item
from ims.utils import (
    clear_screen,
    generate_menu,
    validate,
    print_as_table,
    validate_field,
)


import inquirer


class ItemDTO:
    @staticmethod
    @db_session
    def show():
        # select(item for item in Item)[:].show()
        items = select(item for item in Item)[:]
        print_as_table(
            [
                {
                    "ID": item.id,
                    "Category": item.category,
                    "Name": item.name,
                    "Serial": item.serial,
                    "Supplier": item.supplier,
                    "Price": item.price,
                    "Qty": item.quantity,
                    "Warranty": item.warranty,
                }
                for item in items
            ]
        )

    @staticmethod
    @db_session
    def create():
        suppliers = list(set(select(item.supplier for item in Item)))
        categories = list(set(select(item.category for item in Item)))

        answers = inquirer.prompt(
            [
                inquirer.Text("name", message="Enter the name of the item"),
                inquirer.List(
                    "category",
                    message="Enter the category of the item",
                    choices=categories,
                    carousel=True,
                    other=True,
                ),
                inquirer.Text(
                    "price",
                    message="Enter the price of the item",
                    validate=validate("float", "Price"),
                ),
                inquirer.List(
                    "supplier",
                    message="Enter the supplier of the item",
                    choices=suppliers,
                    carousel=True,
                    other=True,
                ),
                inquirer.Text("serial", message="Enter the serial number of the item"),
                inquirer.Text(
                    "quantity",
                    message="Enter the quantity of the item",
                    validate=validate("int", "Quantity"),
                ),
                inquirer.Text(
                    "warranty", message="Enter the warranty status of the item"
                ),
            ]
        )
        if answers is None:
            return

        item = Item(
            name=answers["name"],
            price=answers["price"],
            serial=answers["serial"],
            category=answers["category"],
            supplier=answers["supplier"],
            quantity=answers["quantity"],
            warranty=answers["warranty"],
        )
        commit()
        print(f"Item '{answers['name']}' created successfully!")

    @staticmethod
    @db_session
    def edit():
        id = inquirer.prompt(
            [
                inquirer.Text(
                    "id",
                    message="Enter the id of the item",
                    validate=validate_field(Item, "id"),
                )
            ]
        )
        if id is None:
            return
        id = id["id"]

        item = select(item for item in Item if item.id == id).first()
        if item is None:
            print(f"Item '{id}' not found!")
            return

        suppliers = list(set(select(item.supplier for item in Item)))
        categories = list(set(select(item.category for item in Item)))

        answers = inquirer.prompt(
            [
                inquirer.Text(
                    "name",
                    message=f"Enter the new name of the item ({item.name})",
                    default=item.name,
                ),
                inquirer.List(
                    "category",
                    message=f"Enter the new category of the item ({item.category})",
                    choices=categories,
                    default=item.category,
                    carousel=True,
                    other=True,
                ),
                inquirer.Text(
                    "price",
                    message=f"Enter the new price of the item ({item.price})",
                    default=item.price,
                    validate=validate("float", "Price"),
                ),
                inquirer.List(
                    "supplier",
                    message=f"Enter the new supplier of the item ({item.supplier})",
                    choices=suppliers,
                    default=item.supplier,
                    carousel=True,
                    other=True,
                ),
                inquirer.Text(
                    "serial",
                    message=f"Enter the new serial number of the item ({item.serial})",
                    default=item.serial,
                ),
                inquirer.Text(
                    "quantity",
                    message=f"Enter the quantity of the item ({item.quantity})",
                    validate=validate("int", "Quantity"),
                    default=item.quantity,
                ),
                inquirer.Text(
                    "warranty",
                    message=f"Enter the warranty status of the item ({item.warranty})",
                    default=item.warranty,
                ),
            ]
        )

        if answers is None:
            return

        item.name = answers["name"]
        item.price = answers["price"]
        item.category = answers["category"]
        item.supplier = answers["supplier"]
        item.serial = answers["serial"]
        item.quantity = answers["quantity"]
        item.warranty = answers["warranty"]
        commit()
        print(f"Item '{id}' updated successfully!")

    @staticmethod
    @db_session
    def delete():
        id = inquirer.prompt(
            [
                inquirer.Text(
                    "id",
                    message="Enter the id of the item",
                    validate=validate_field(Item, "id"),
                ),
                inquirer.Confirm(
                    "confirm",
                    message=lambda x: f"Are you sure you want to delete item id {x['id']}?",
                ),
            ]
        )
        if id is None:
            return
        if not id["confirm"]:
            return
        id = id["id"]
        item = select(item for item in Item if item.id == id).first()
        if item is None:
            print(f"Item '{id}' not found!")
            return
        item.delete()
        commit()
        print(f"Item '{id}' deleted successfully!")


def items_menu():
    generate_menu(
        [
            {"short": "Add", "text": "Add item", "action": ItemDTO.create},
            {"short": "Edit", "text": "Edit item", "action": ItemDTO.edit},
            {"short": "Delete", "text": "Delete item", "action": ItemDTO.delete},
        ],
        "items",
        ItemDTO,
    )()

    # while True:
    #     pause = True
    #     clear_screen()
    #     print("Items")
    #     print("-----")
    #     ItemDTO.show()
    #     print()

    #     ans = inquirer.prompt(menu)

    #     if ans is None:
    #         pause = False
    #         return

    #     choice = ans["option"].lower()
    #     if choice == "add":
    #         ItemDTO.create()
    #     elif choice == "edit":
    #         ItemDTO.edit()
    #     elif choice == "delete":
    #         ItemDTO.delete()
    #     elif choice == "back":
    #         pause = False
    #         return
    #     elif choice == "exit":
    #         pause = False
    #         exit(0)
    #     else:
    #         print("Invalid choice")
    #     if pause:
    #         input("\nPress Enter to continue...")
