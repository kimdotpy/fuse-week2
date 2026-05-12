"""
models/models.py — SQLAlchemy ORM models.

Each class maps 1-to-1 with a table in the seed.sql schema.
Column names use the exact quoted identifiers from the DDL so SQLAlchemy
generates the right SQL (PostgreSQL is case-sensitive for quoted names).
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    LargeBinary,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# ─────────────────────────────────────────────────────────────────────────────
# ProductLine
# ─────────────────────────────────────────────────────────────────────────────
class ProductLine(Base):
    __tablename__ = "productlines"

    productLine: Mapped[str] = mapped_column(
        "productLine", String(50), primary_key=True
    )
    textDescription: Mapped[str | None] = mapped_column(
        "textDescription", String(4000), nullable=True
    )
    htmlDescription: Mapped[str | None] = mapped_column(
        "htmlDescription", Text, nullable=True
    )
    image: Mapped[bytes | None] = mapped_column(
        "image", LargeBinary, nullable=True
    )

    # relationships
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="product_line"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Product
# ─────────────────────────────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    productCode: Mapped[str] = mapped_column(
        "productCode", String(15), primary_key=True
    )
    productName: Mapped[str] = mapped_column(
        "productName", String(70), nullable=False
    )
    productLine: Mapped[str] = mapped_column(
        "productLine",
        String(50),
        ForeignKey("productlines.productLine"),
        nullable=False,
    )
    productScale: Mapped[str] = mapped_column(
        "productScale", String(10), nullable=False
    )
    productVendor: Mapped[str] = mapped_column(
        "productVendor", String(50), nullable=False
    )
    productDescription: Mapped[str] = mapped_column(
        "productDescription", Text, nullable=False
    )
    quantityInStock: Mapped[int] = mapped_column(
        "quantityInStock", Integer, nullable=False
    )
    buyPrice: Mapped[Decimal] = mapped_column(
        "buyPrice", Numeric(10, 2), nullable=False
    )
    MSRP: Mapped[Decimal] = mapped_column(
        "MSRP", Numeric(10, 2), nullable=False
    )

    # relationships
    product_line: Mapped["ProductLine"] = relationship(
        "ProductLine", back_populates="products"
    )
    order_details: Mapped[list["OrderDetail"]] = relationship(
        "OrderDetail", back_populates="product"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Office
# ─────────────────────────────────────────────────────────────────────────────
class Office(Base):
    __tablename__ = "offices"

    officeCode: Mapped[str] = mapped_column(
        "officeCode", String(10), primary_key=True
    )
    city: Mapped[str] = mapped_column("city", String(50), nullable=False)
    phone: Mapped[str] = mapped_column("phone", String(50), nullable=False)
    addressLine1: Mapped[str] = mapped_column(
        "addressLine1", String(50), nullable=False
    )
    addressLine2: Mapped[str | None] = mapped_column(
        "addressLine2", String(50), nullable=True
    )
    state: Mapped[str | None] = mapped_column(
        "state", String(50), nullable=True
    )
    country: Mapped[str] = mapped_column("country", String(50), nullable=False)
    postalCode: Mapped[str] = mapped_column(
        "postalCode", String(15), nullable=False
    )
    territory: Mapped[str] = mapped_column(
        "territory", String(10), nullable=False
    )

    # relationships
    employees: Mapped[list["Employee"]] = relationship(
        "Employee", back_populates="office"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Employee
# ─────────────────────────────────────────────────────────────────────────────
class Employee(Base):
    __tablename__ = "employees"

    employeeNumber: Mapped[int] = mapped_column(
        "employeeNumber", Integer, primary_key=True
    )
    lastName: Mapped[str] = mapped_column("lastName", String(50), nullable=False)
    firstName: Mapped[str] = mapped_column(
        "firstName", String(50), nullable=False
    )
    extension: Mapped[str] = mapped_column(
        "extension", String(10), nullable=False
    )
    email: Mapped[str] = mapped_column("email", String(100), nullable=False)
    officeCode: Mapped[str] = mapped_column(
        "officeCode",
        String(10),
        ForeignKey("offices.officeCode"),
        nullable=False,
    )
    reportsTo: Mapped[int | None] = mapped_column(
        "reportsTo",
        Integer,
        ForeignKey("employees.employeeNumber"),
        nullable=True,
    )
    jobTitle: Mapped[str] = mapped_column(
        "jobTitle", String(50), nullable=False
    )

    # relationships
    office: Mapped["Office"] = relationship("Office", back_populates="employees")
    manager: Mapped["Employee | None"] = relationship(
        "Employee", remote_side="Employee.employeeNumber", back_populates="reports"
    )
    reports: Mapped[list["Employee"]] = relationship(
        "Employee", back_populates="manager"
    )
    customers: Mapped[list["Customer"]] = relationship(
        "Customer", back_populates="sales_rep"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Customer
# ─────────────────────────────────────────────────────────────────────────────
class Customer(Base):
    __tablename__ = "customers"

    customerNumber: Mapped[int] = mapped_column(
        "customerNumber", Integer, primary_key=True
    )
    customerName: Mapped[str] = mapped_column(
        "customerName", String(50), nullable=False
    )
    contactLastName: Mapped[str] = mapped_column(
        "contactLastName", String(50), nullable=False
    )
    contactFirstName: Mapped[str] = mapped_column(
        "contactFirstName", String(50), nullable=False
    )
    phone: Mapped[str] = mapped_column("phone", String(50), nullable=False)
    addressLine1: Mapped[str] = mapped_column(
        "addressLine1", String(50), nullable=False
    )
    addressLine2: Mapped[str | None] = mapped_column(
        "addressLine2", String(50), nullable=True
    )
    city: Mapped[str] = mapped_column("city", String(50), nullable=False)
    state: Mapped[str | None] = mapped_column(
        "state", String(50), nullable=True
    )
    postalCode: Mapped[str | None] = mapped_column(
        "postalCode", String(15), nullable=True
    )
    country: Mapped[str] = mapped_column("country", String(50), nullable=False)
    salesRepEmployeeNumber: Mapped[int | None] = mapped_column(
        "salesRepEmployeeNumber",
        Integer,
        ForeignKey("employees.employeeNumber"),
        nullable=True,
    )
    creditLimit: Mapped[Decimal | None] = mapped_column(
        "creditLimit", Numeric(10, 2), nullable=True
    )

    # relationships
    sales_rep: Mapped["Employee | None"] = relationship(
        "Employee", back_populates="customers"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="customer"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="customer"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Payment
# ─────────────────────────────────────────────────────────────────────────────
class Payment(Base):
    __tablename__ = "payments"

    customerNumber: Mapped[int] = mapped_column(
        "customerNumber",
        Integer,
        ForeignKey("customers.customerNumber"),
        primary_key=True,
    )
    checkNumber: Mapped[str] = mapped_column(
        "checkNumber", String(50), primary_key=True
    )
    paymentDate: Mapped[date] = mapped_column(
        "paymentDate", Date, nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        "amount", Numeric(10, 2), nullable=False
    )

    # relationships
    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="payments"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    orderNumber: Mapped[int] = mapped_column(
        "orderNumber", Integer, primary_key=True
    )
    orderDate: Mapped[date] = mapped_column("orderDate", Date, nullable=False)
    requiredDate: Mapped[date] = mapped_column(
        "requiredDate", Date, nullable=False
    )
    shippedDate: Mapped[date | None] = mapped_column(
        "shippedDate", Date, nullable=True
    )
    status: Mapped[str] = mapped_column("status", String(15), nullable=False)
    comments: Mapped[str | None] = mapped_column(
        "comments", Text, nullable=True
    )
    customerNumber: Mapped[int] = mapped_column(
        "customerNumber",
        Integer,
        ForeignKey("customers.customerNumber"),
        nullable=False,
    )

    # relationships
    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="orders"
    )
    order_details: Mapped[list["OrderDetail"]] = relationship(
        "OrderDetail", back_populates="order"
    )


# ─────────────────────────────────────────────────────────────────────────────
# OrderDetail
# ─────────────────────────────────────────────────────────────────────────────
class OrderDetail(Base):
    __tablename__ = "orderdetails"

    orderNumber: Mapped[int] = mapped_column(
        "orderNumber",
        Integer,
        ForeignKey("orders.orderNumber"),
        primary_key=True,
    )
    productCode: Mapped[str] = mapped_column(
        "productCode",
        String(15),
        ForeignKey("products.productCode"),
        primary_key=True,
    )
    quantityOrdered: Mapped[int] = mapped_column(
        "quantityOrdered", Integer, nullable=False
    )
    priceEach: Mapped[Decimal] = mapped_column(
        "priceEach", Numeric(10, 2), nullable=False
    )
    orderLineNumber: Mapped[int] = mapped_column(
        "orderLineNumber", SmallInteger, nullable=False
    )

    # relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_details")
    product: Mapped["Product"] = relationship(
        "Product", back_populates="order_details"
    )
