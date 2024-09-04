from datetime import timedelta, datetime
from pony.orm import *

from ims.db import Item, Order
from ims.utils import generate_menu

import inquirer

threshold = 20

class ReportGenerator:
	@staticmethod
	@db_session
	def show():
		global threshold
		items = select(item for item in Item)[:]
		print("Low Inventory Report")
		print("-" * 20)
		if not items:
			print("No items are understocked at the moment :)")
			return
		for item in items:
			if item.quantity < threshold:
				print(f"{item.name} - {item.quantity} units available")

	@staticmethod
	@db_session
	def inventory_report():
		global threshold
		items = select(item for item in Item)[:]
		by_category = {}
		for item in items:
			if item.category not in by_category:
				by_category[item.category] = []
			by_category[item.category].append(item.to_dict())
		text = "Inventory Report"
		text += "\n" + "-" * len(text)
		# for item in items:
		# 	text += (f"{"LOW" if item.quantity < threshold else ""} {item.name} - {item.quantity} units available \n")
		for category, items in by_category.items():
			text += f"\n{category}"
			text += "\n" + "-" * len(category)
			for item in items:
				text += f"\n{"LOW - " if item['quantity'] < threshold else ""}{item['name']} - {item['quantity']} units available"
			text += "\n"

		print(text)
		markdown = inquirer.confirm("Do you want to save the report as a markdown file?")
		if not markdown:
			return
		
		md = "# Inventory Report"
		for category, items in by_category.items():
			md += f"\n\n## {category}"
			for item in items:
				md += f"\n\n- {'**LOW** - ' if item['quantity'] < threshold else ''}{item['name']} - `{item['quantity']}` units available"

		# file = inquirer.text(message="Enter the file name to save the report as", default="inventory_report.txt")
		file = inquirer.prompt(
			[
				inquirer.Text("file", message="Enter the file name to save the report as", default=f"inventory_report.md")
			]
		)
		if not file:
			return
		file = file["file"]
		with open(file, "w") as f:
			f.write(md)

		print(f"Report saved as {file}")

	@staticmethod
	@db_session
	def sales_report():
		orders = select(order for order in Order)[:]
		last_30_days = []
		for order in orders:
			if order.created_at > datetime.now() - timedelta(days=30):
				last_30_days.append(order)

		items_sold_last_30_days = []
		for order in last_30_days:
			for order_item in order.items:
				if order_item.item.category not in [item["category"] for item in items_sold_last_30_days]:
					items_sold_last_30_days.append({"category": order_item.item.category, "quantity": order_item.quantity})
				else:
					for item in items_sold_last_30_days:
						if item["category"] == order_item.item.category:
							item["quantity"] += order_item.quantity
							break
		
		last_year = []
		for order in orders:
			if order.created_at > datetime.now() - timedelta(days=365):
				last_year.append(order)
			
		items_sold_last_year = []
		for order in last_year:
			for order_item in order.items:
				if order_item.item.category not in [item["category"] for item in items_sold_last_year]:
					items_sold_last_year.append({"category": order_item.item.category, "quantity": order_item.quantity})
				else:
					for item in items_sold_last_year:
						if item["category"] == order_item.item.category:
							item["quantity"] += order_item.quantity
							break
		
		text = "Sales Report"
		text += "\n" + "-" * len(text)
		text += "\nLast 30 days"
		text += "\n" + "-" * len("Last 30 days")
		for item in items_sold_last_30_days:
			text += f"\n{item['category']} - {item['quantity']} units sold"
		text += "\n\nLast year"
		text += "\n" + "-" * len("Last year")
		for item in items_sold_last_year:
			text += f"\n{item['category']} - {item['quantity']} units sold"
		print(text)

		markdown = inquirer.confirm("Do you want to save the report as a markdown file?")
		if not markdown:
			return
		
		md = "# Sales Report"
		md += "\n\n## Last 30 days"
		for item in items_sold_last_30_days:
			md += f"\n\n- {item['category']} - `{item['quantity']}` units sold"
		md += "\n\n## Last year"
		for item in items_sold_last_year:
			md += f"\n\n- {item['category']} - `{item['quantity']}` units sold"

		# file = inquirer.text(message="Enter the file name to save the report as", default="inventory_report.txt")
		file = inquirer.prompt(
			[
				inquirer.Text("file", message="Enter the file name to save the report as", default=f"sales_report.md")
			]
		)
		if not file:
			return
		file = file["file"]
		with open(file, "w") as f:
			f.write(md)

		print(f"Report saved as {file}")
		
def reports_menu():
	menu = [
		{
			"short": "Inventory",
			"text": "Inventory Report",
			"action": ReportGenerator.inventory_report,
		},
		{
			"short": "Sales",
			"text": "Sales Report",
			"action": ReportGenerator.sales_report,
		},
	]
	generate_menu(menu, "reports", ReportGenerator)()
