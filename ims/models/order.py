from pony.orm import *
from ims.db import Order, OrderItem, Item

import inquirer

from ims.utils import generate_menu, validate, print_as_table, validate_field


class OrderItemDTO:
		def __init__(self, order):
				self.order = order

		@db_session
		def show(self):
				items = select(
						order_item for order_item in OrderItem if order_item.order == self.order
				)[:]
				if not items:
						print(f"No order items found for order '{self.order.id}'")
						return
				print_as_table(
						[
								{
										"ID": order_item.id,
										"Item": order_item.item.name,
										"Quantity": order_item.quantity,
										"Unit Price": order_item.item.price,
										"Total Price": order_item.item.price * order_item.quantity,
								}
								for order_item in items
						]
				)
				# print_as_table(items.to_list(), ['id', 'item', 'quantity'])

		@db_session
		def create(self):
				# items = list(set(select(order_item.item for order_item in OrderItem)))
				items = list(set(select(item for item in Item)))
				if not items or len(items) == 0:
						print("No items found. Please create an item first.")
						return

				def autocomplete_item(query, state):
						items = select(item for item in Item)[:]
						items = [item.name for item in items if query.lower() in item.name.lower()]
						return items[state % len(items)]

				def validate_item(_, item):
						if item not in [item.name for item in items]:
								raise inquirer.errors.ValidationError(
										"", reason=f"Item '{item}' not found!"
								)
						return True

				def validate_quantity(answers, quantity):
						validate("int", "Quantity")(answers, quantity)
						if int(quantity) < 1:
								raise inquirer.errors.ValidationError(
										"", reason="Quantity must be greater than 0!"
								)
						item = select(item for item in Item if item.name == answers["item"]).first()
						if item.quantity < int(quantity):
								raise inquirer.errors.ValidationError(
										"",
										reason=f"Quantity must be less than or equal to {item.quantity}!",
								)
						return True

				answers = inquirer.prompt(
						[
								inquirer.Text(
										"item",
										message="Enter the item of the order",
										autocomplete=autocomplete_item,
										validate=validate_item,
										# choices=items,
										# carousel=True,
								),
								inquirer.Text(
										"quantity",
										message="Enter the quantity of the item",
										validate=validate_quantity,
								),
						]
				)
				if answers is None:
						return

				order_item = select(
						order_item
						for order_item in OrderItem
						if order_item.order == self.order
						and order_item.item.name == answers["item"]
				).first()
				if order_item is not None:
						order_item.quantity += int(answers["quantity"])
						item = order_item.item
						item.quantity -= int(answers["quantity"])
				else:
						item = select(item for item in Item if item.name == answers["item"]).first()
						item.quantity -= int(answers["quantity"])
						order_item = OrderItem(
								order=self.order.id, item=item.id, quantity=answers["quantity"]
						)
				commit()
				print(f"Order item '{order_item.id}' created successfully!")

		@db_session
		def edit(self):
				id = inquirer.prompt(
						[
								inquirer.Text(
										"id",
										message="Enter the id of the order item",
										validate=validate_field(OrderItem, "id"),
								)
						]
				)
				if id is None:
						return
				id = id["id"]

				order_item = select(
						order_item for order_item in OrderItem if order_item.id == id
				).first()
				if order_item is None:
						print(f"Order item '{id}' not found!")
						return

				def validate_quantity(answers, quantity):
						validate("int", "Quantity")(answers, quantity)
						if int(quantity) < 1:
								raise inquirer.errors.ValidationError(
										"", reason="Quantity must be greater than 0!"
								)
						# item = select(item for item in Item if item.name == answers["item"]).first()
						item = order_item.item
						if (item.quantity + order_item.quantity) < int(quantity):
								raise inquirer.errors.ValidationError(
										"",
										reason=f"Quantity must be less than or equal to {item.quantity + order_item.quantity}!",
								)
						return True

				answers = inquirer.prompt(
						[
								inquirer.Text(
										"quantity",
										message=f"Enter the new quantity of the order item ({order_item.quantity})",
										validate=validate_quantity,
										default=order_item.quantity,
								),
						]
				)
				difference = int(answers["quantity"]) - order_item.quantity
				order_item.quantity = answers["quantity"]
				item = order_item.item
				item.quantity -= difference
				commit()
				print(f"Order item '{order_item.id}' updated successfully!")

		@db_session
		def delete(self):
				id = inquirer.prompt(
						[
								inquirer.Text(
										"id",
										message="Enter the id of the order item",
										validate=validate_field(OrderItem, "id"),
								),
								inquirer.Confirm("confirm", message=lambda answers: f"Are you sure you want to delete item id {answers["id"]}?", default=True),
						]
				)
				if id is None:
						return
				if not id["confirm"]:
						return
				id = id["id"]

				order_item = select(
						order_item for order_item in OrderItem if order_item.id == id
				).first()
				if order_item is None:
						print(f"Order item '{id}' not found!")
						return
				order_item.delete()
				commit()
				print(f"Order item '{id}' deleted successfully!")


def order_items_menu(order):
		dto = OrderItemDTO(order)
		generate_menu(
				[
						{
								"short": "Add",
								"text": "Add order item",
								"action": dto.create,
						},
						{
								"short": "Edit",
								"text": "Edit order item",
								"action": dto.edit,
								"pause": False,
						},
						{
								"short": "Remove",
								"text": "Remove order item",
								"action": dto.delete,
						},
				],
				"order items",
				dto,
		)()


class OrderDTO:
		@staticmethod
		@db_session
		def show():
				# select(order for order in Order)[:].show()
				orders = select(order for order in Order)[:]
				print_as_table(
						[
								{
										"ID": order.id,
										"Status": order.status,
										"Item Count": len(order.items),
										"Total Price": sum(
												[
														order_item.item.price * order_item.quantity
														for order_item in order.items
												]
										),
								}
								for order in orders
						]
				)

		@staticmethod
		@db_session
		def create():
				answers = inquirer.prompt(
						[
								inquirer.Text(
										"status", message="Enter the status of the order", default="Pending"
								),
						]
				)
				if answers is None:
						return

				order = Order(status=answers["status"])
				commit()
				print(f"Order '{order.id}' created successfully!")

				order_items_menu(order)

		@staticmethod
		@db_session
		def edit():
				id = inquirer.prompt(
						[
								inquirer.Text(
										"id",
										"Enter the id of the order",
										validate=validate_field(Order, "id"),
								),
								inquirer.Confirm(
										"edit_items", message="Edit order items?", default=True
								),
						]
				)
				if id is None:
						return
				edit_items = id["edit_items"]
				id = id["id"]

				if edit_items:
						order = select(order for order in Order if order.id == id).first()
						order_items_menu(order)
						return
				else:
						order = select(order for order in Order if order.id == id).first()
						if order is None:
								print(f"Order '{id}' not found!")
								return
						answers = inquirer.prompt(
								[
										inquirer.Text(
												"status",
												message=f"Enter the status of the order ({order.status})",
												default=order.status,
										),
								]
						)
						order.status = answers["status"]
						commit()
						print(f"Order '{order.id}' updated successfully!")

		@staticmethod
		@db_session
		def delete():
				id = inquirer.prompt(
						[
								inquirer.Text(
										"id",
										"Enter the id of the order",
										validate=validate_field(Order, "id"),
								),
								inquirer.Confirm(
										"confirm", message=lambda answers: f"Are you sure you want to delete order id {answers['id']}?", default=True
								),
						]
				)
				if id is None:
						return
				if not id["confirm"]:
						return
				id = id["id"]

				order = select(order for order in Order if order.id == id).first()
				if order is None:
						print(f"Order '{id}' not found!")
						return
				order.delete()
				commit()
				print(f"Order '{id}' deleted successfully!")


def orders_menu():
		generate_menu(
				[
						{
								"short": "Create",
								"text": "Create order",
								"action": OrderDTO.create,
						},
						{
								"short": "Edit",
								"text": "Edit order",
								"action": OrderDTO.edit,
						},
						{
								"short": "Delete",
								"text": "Delete order",
								"action": OrderDTO.delete,
						},
				],
				"orders",
				OrderDTO,
		)()
