# from peewee import SqliteDatabase, Model

# db = SqliteDatabase(
# 		"people.db",
# 		pragmas={
# 				"journal_mode": "wal",
# 				"cache_size": -1 * 64000,  # 64MB
# 				"foreign_keys": 1,
# 				"ignore_check_constraints": 0,
# 				"synchronous": 0,
# 		},
# )


# class BaseModel(Model):
# 		# id = AutoField()

# 		class Meta:
# 				database = db

import datetime
from pony.orm import *

db = Database()

db.bind(
    provider="sqlite",
    filename="../ims.db",
    create_db=True,
)


class User(db.Entity):
    username = Required(str)
    hash = Required(str)
    role = Required(str)


# class Box(db.Entity):
# 		name = Required(str)
# 		location = Required(str)
# 		items = Set("Item")


# class Supplier(db.Entity):
# 		name = Required(str)
# 		address = Required(str)
# 		phone = Required(str)
# 		email = Required(str)
# 		products = Set("Product")


# class Product(db.Entity):
# 		name = Required(str)
# 		price = Required(float)
# 		supplier = Required(Supplier)
# 		items = Set("Item")


class Item(db.Entity):
    name = Required(str)
    category = Required(str)
    price = Required(float)
    supplier = Required(str)
    serial = Required(str)
    quantity = Required(int)
    warranty = Required(str)
    orders = Set("OrderItem")


class Order(db.Entity):
    status = Required(str)
    created_at = Required(
        datetime.datetime, default=datetime.datetime.now(datetime.UTC)
    )
    items = Set("OrderItem")


class OrderItem(db.Entity):
    order = Required(Order)
    item = Required(Item)
    quantity = Required(int)


db.generate_mapping(create_tables=True)
