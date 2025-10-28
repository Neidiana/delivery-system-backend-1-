from fastapi import FastAPI, HTTPException
from models.user_model import UserCreate, UserUpdate, UserResponse
from models.produc_model import ProductResponse, ProductCreate
from models.order_model import OrderCreate, OrderUpdate, OrderResponse, OrderItemCreate, OrderItemResponse
from config import get_connection
from typing import List

app = FastAPI(title="Delivery System API", version="1.0")

# -------------------
# CREATE USER
# -------------------
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (user.name, user.email, user.password, user.role)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return UserResponse(id=new_id, name=user.name, email=user.email, role=user.role)

# -------------------
# READ ALL USERS
# -------------------
@app.get("/users", response_model=List[UserResponse])
def get_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

# -------------------
# READ USER BY ID
# -------------------
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

# -------------------
# UPDATE USER
# -------------------
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    updated_name = user.name if user.name else existing["name"]
    updated_email = user.email if user.email else existing["email"]
    updated_password = user.password if user.password else existing["password"]
    updated_role = user.role if user.role else existing["role"]

    cursor.execute(
        "UPDATE users SET name=%s, email=%s, password=%s, role=%s WHERE id=%s",
        (updated_name, updated_email, updated_password, updated_role, user_id)
    )
    conn.commit()
    conn.close()

    return UserResponse(id=user_id, name=updated_name, email=updated_email, role=updated_role)

# -------------------
# DELETE USER
# -------------------
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()

    return {"message": f"Usuário {user_id} deletado com sucesso"}

# -------------------
# CREATE PRODUCT
# -------------------
@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM products WHERE name = %s", (product.name,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Produto já cadastrado")

    cursor.execute(
        "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
        (product.name, product.price, product.quantity)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return ProductResponse(id=new_id, name=product.name, price=product.price, quantity=product.quantity)

# -------------------
# READ ALL PRODUCTS
# -------------------
@app.get("/products", response_model=List[ProductResponse])
def get_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, price, quantity FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

# -------------------
# READ PRODUCT BY ID
# -------------------
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, price, quantity FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

# -------------------
# UPDATE PRODUCT
# -------------------
@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    updated_name = product.name if product.name else existing["name"]
    updated_price = product.price if product.price else existing["price"]
    updated_quantity = product.quantity if product.quantity else existing["quantity"]

    cursor.execute(
        "UPDATE products SET name=%s, price=%s, quantity=%s WHERE id=%s",
        (updated_name, updated_price, updated_quantity, product_id)
    )
    conn.commit()
    conn.close()

    return ProductResponse(id=product_id, name=updated_name, price=updated_price, quantity=updated_quantity)

# -------------------
# DELETE PRODUCT
# -------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM products WHERE id = %s", (product_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    conn.close()

    return {"message": f"Produto {product_id} deletado com sucesso"}

from models.order_model import OrderCreate, OrderUpdate, OrderResponse, OrderItemCreate, OrderItemResponse
from fastapi import FastAPI, HTTPException
from typing import List
from config import get_connection

# -------------------
# CREATE ORDER
# -------------------
@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verifica se o usuário existe
    cursor.execute("SELECT id FROM users WHERE id = %s", (order.user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Cria o pedido
    cursor.execute(
        "INSERT INTO orders (user_id, status) VALUES (%s, %s)",
        (order.user_id, order.status.value)
    )
    conn.commit()
    order_id = cursor.lastrowid

    # Adiciona itens do pedido
    for item in order.items:
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, item.product_id, item.quantity, item.price)
        )
    conn.commit()

    # Busca itens criados
    cursor.execute("SELECT id, product_id, quantity, price FROM order_items WHERE order_id = %s", (order_id,))
    items_db = cursor.fetchall()

    conn.close()

    items_response = [OrderItemResponse(**i) for i in items_db]
    return OrderResponse(
        id=order_id,
        user_id=order.user_id,
        status=order.status,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        items=items_response
    )

# -------------------
# READ ALL ORDERS
# -------------------
@app.get("/orders", response_model=List[OrderResponse])
def get_orders():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM orders")
    orders_db = cursor.fetchall()

    orders_response = []
    for o in orders_db:
        cursor.execute("SELECT id, product_id, quantity, price FROM order_items WHERE order_id = %s", (o["id"],))
        items_db = cursor.fetchall()
        items_response = [OrderItemResponse(**i) for i in items_db]

        orders_response.append(OrderResponse(
            id=o["id"],
            user_id=o["user_id"],
            status=o["status"],
            created_at=o["created_at"],
            updated_at=o["updated_at"],
            items=items_response
        ))

    conn.close()
    return orders_response

# -------------------
# READ ORDER BY ID
# -------------------
@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order_db = cursor.fetchone()
    if not order_db:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    cursor.execute("SELECT id, product_id, quantity, price FROM order_items WHERE order_id = %s", (order_id,))
    items_db = cursor.fetchall()
    items_response = [OrderItemResponse(**i) for i in items_db]

    conn.close()
    return OrderResponse(
        id=order_db["id"],
        user_id=order_db["user_id"],
        status=order_db["status"],
        created_at=order_db["created_at"],
        updated_at=order_db["updated_at"],
        items=items_response
    )

# -------------------
# UPDATE ORDER
# -------------------
@app.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order: OrderUpdate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    existing_order = cursor.fetchone()
    if not existing_order:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    new_status = order.status.value if order.status else existing_order["status"]

    cursor.execute(
        "UPDATE orders SET status=%s WHERE id=%s",
        (new_status, order_id)
    )
    conn.commit()

    cursor.execute("SELECT id, product_id, quantity, price FROM order_items WHERE order_id = %s", (order_id,))
    items_db = cursor.fetchall()
    items_response = [OrderItemResponse(**i) for i in items_db]

    conn.close()
    return OrderResponse(
        id=order_id,
        user_id=existing_order["user_id"],
        status=new_status,
        created_at=existing_order["created_at"],
        updated_at=datetime.now(),
        items=items_response
    )

# -------------------
# DELETE ORDER
# -------------------
@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Deleta os itens primeiro
    cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
    cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()
    conn.close()

    return {"message": f"Pedido {order_id} deletado com sucesso"}
