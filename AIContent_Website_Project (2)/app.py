from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import json
import os
import uuid
import random
# Flask → tạo app web
# render_template → hiển thị file HTML (mở trang html đó ra)
# request → lấy dữ liệu người dùng nhập từ form
# redirect → chuyển sang trang khác
# session → lưu dữ liệu tạm (vd: đang đăng nhập)
# url_for() → gọi tên route để chuyển trang
# json → đọc/ghi file JSON

app = Flask(__name__)
app.secret_key = "supersecretkey"
# Tạo ứng dụng Flask
# secret_key → dùng để mã hóa session (bắt buộc khi dùng session)

# Hàm đọc user từ file JSON và trả về danh sách user
def load_users():
    with open("users.json", "r") as f:
        data = json.load(f)
        return data["users"]   # trả về list user

# Route cho trang chủ
@app.route("/")
def launch():
    return render_template("launch.html") # Mở trang launch.html

# Route cho trang đăng nhập (login)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST": # xử lý khi bấm nút login
        email = request.form.get("email") # Lấy dữ liệu từ form
        password = request.form.get("password")

        if not email or not password: # kiểm tra nếu có trường nào bỏ trống
            return render_template(
                "login.html",
                error="Please fill in all required fields."
            )

        users = load_users() # đọc danh sách user từ file JSON

        for user in users: # kiểm tra email và password
            if user["email"] == email and user["password"] == password:
                session["user"] = user.copy() # lưu thông tin user vào session (copy() để tránh thay đổi dữ liệu gốc)
                return redirect(url_for("home")) # chuyển đến trang home nếu đăng nhập thành công

        return render_template( # hiển thị lỗi nếu email hoặc password không đúng
            "login.html",
            error="Invalid email or password. Please try again!"
        )

    return render_template("login.html")

# Route cho trang home sau khi đăng nhập thành công
@app.route("/home")
def home():
    if "user" in session:
        success = request.args.get("success")
        return render_template(
            "home.html",
            name=session["user"]["name"],
            success=success,
            active_page="home"
        )
    return redirect(url_for("login"))

# Route cho trang đăng ký (register)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST": # xử lý khi bấm nút register
        name = request.form["name"] # Lấy dữ liệu từ form
        gender = request.form["gender"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]
        
        errors = []

        if not name:
            errors.append("name")
        if not email:
            errors.append("email")
        if not password:
            errors.append("password")
        if not confirm:
            errors.append("confirm_password")

        if errors:
            return render_template(
                "register.html",
                error="Please fill in all required fields.",
                error_fields=errors,
                form_data=request.form
            )

        users = load_users() # đọc danh sách user từ file JSON

        # kiểm tra email tồn tại chưa
        for user in users:
            if user["email"] == email:
                return render_template("register.html", error="Email already exists!") # Hiển thị lỗi nếu email đã tồn tại

        if len(password) < 6: # kiểm tra độ dài password
            return render_template("register.html", error="Password must be at least 6 characters!")

        if password != confirm: # kiểm tra password và confirm có giống nhau không
            return render_template("register.html", error="Passwords do not match!")

        # thêm user mới
        users.append({ 
            "name": name,
            "gender": gender,
            "email": email,
            "phone": phone,
            "password": password
        })

        with open("users.json", "w") as f: # ghi lại danh sách user vào file JSON
            json.dump({"users": users}, f, indent=4)

        return render_template("register.html", success=True) # Hiển thị thông báo đăng ký thành công

    return render_template("register.html")

# Route cho đăng xuất (logout)
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# Route cho trang quên mật khẩu
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        
        if not email: # kiểm tra nếu email bỏ trống
            return render_template(
                "forgot_email.html",
                error="Please fill in the required field."
            )
        
        users = load_users()

        #kiểm tra email có tồn tại không
        for user in users:
            if user["email"] == email:
                code = str(random.randint(100000, 999999)) # tạo mã code ngẫu nhiên 6 chữ số

                session["reset_email"] = email # lưu email vào session để dùng sau
                session["reset_code"] = code # lưu code vào session để dùng sau

                print("Reset code:", code)  # xem trong terminal để test

                return redirect(url_for("verify_code")) # chuyển đến trang verify_code nếu email tồn tại

        return render_template("forgot_email.html", error="Email not found. Please try again!") # Hiển thị lỗi nếu email không tồn tại

    return render_template("forgot_email.html")

# Route cho trang xác minh mã code
@app.route("/verify-code", methods=["GET", "POST"])
def verify_code():
    if "reset_code" not in session: # nếu không có mã code trong session thì chuyển về trang quên mật khẩu
        return redirect(url_for("forgot_password"))

    if request.method == "POST": # xử lý khi bấm nút verify
        input_code = request.form["code"]
        
        if not input_code: # kiểm tra nếu email bỏ trống
            return render_template(
                "verify_code.html",
                error="Please fill in the required field."
            )

        if input_code == session.get("reset_code"): # kiểm tra mã code
            return redirect(url_for("new_password")) # chuyển đến trang tạo mật khẩu mới nếu mã code đúng
        else:
            return render_template("verify_code.html", error="Incorrect code. Please try again!") # Hiển thị lỗi nếu mã code không đúng

    return render_template("verify_code.html")

# Route cho trang tạo mật khẩu mới
@app.route("/new-password", methods=["GET", "POST"])
def new_password():
    if "reset_email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST": # xử lý khi bấm nút submit
        password = request.form["password"] # Lấy password và confirm từ form
        confirm = request.form["confirm_password"] 
        
        if not password or not confirm: # kiểm tra nếu email bỏ trống
            return render_template(
                "new_password.html",
                error="Please fill in all required fields."
            )
        
        if len(password) < 6:
            return render_template("new_password.html", error="Password must be at least 6 characters!")

        if password != confirm:
            return render_template("new_password.html", error="Passwords do not match. Please try again!")

        email = session.get("reset_email") # Lấy email từ session
        
        users = load_users()

        # cập nhật password mới cho user vào JSON
        for user in users:
            if user["email"] == email:
                user["password"] = password
                break

        with open("users.json", "w") as f: # ghi lại danh sách user vào file JSON
            json.dump({"users": users}, f, indent=4)

        session.clear() # xóa session sau khi đổi mật khẩu thành công
        return render_template("new_password.html", success=True) # Hiển thị thông báo đổi mật khẩu thành công

    return render_template("new_password.html")

@app.route("/update-profile", methods=["POST"])
def update_profile():
    if "user" not in session:
        return redirect(url_for("login"))

    with open("users.json", "r") as f:
        users = json.load(f)

    email = session["user"]["email"]

    for user in users["users"]: # tìm user có email trùng với email trong session
            if user["email"] == email:
                user["name"] = request.form["name"]
                user["gender"] = request.form["gender"]
                user["phone"] = request.form["phone"]

                session["user"] = user.copy()  # cập nhật session 
                break

    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

    return redirect(url_for("home", success=1)) # chuyển về trang home và truyền tham số success=1 để hiển thị thông báo cập nhật thành công

@app.route("/ai-library")
def ai_library():
    if "user" not in session:
        return redirect(url_for("login"))

    with open(DATA_FILE, "r") as f:
        library = json.load(f)

    return render_template(
        "ai_library.html",
        name=session["user"]["name"],
        active_page="ai",
        blogs=library["blog"],
        posts=library["post"],
        emails=library["email"]
    )
DATA_FILE = "data/ai_library.json"

@app.route("/create-ai")
def create_ai():

    if "user" not in session:
        return redirect(url_for("login"))

    item_id = request.args.get("id")
    item_type = request.args.get("type")

    item = None

    if item_id and item_type:

        with open(DATA_FILE,"r") as f:
            db = json.load(f)

        for content in db[item_type]:
            if content["id"] == item_id:
                item = content
                break

    return render_template(
        "create_ai.html",
        name=session["user"]["name"],
        active_page="ai",
        item=item,
        item_type=item_type
    )

@app.route("/save_content", methods=["POST"])
def save_content():

    data = request.json

    with open(DATA_FILE, "r") as f:
        library = json.load(f)

    # EDIT MODE
    if data.get("id"):

        for item in library[data["type"]]:
            if item["id"] == data["id"]:
                item["title"] = data["title"]
                item["content"] = data["content"]
                item["date"] = data["date"]

    else:
        # CREATE MODE
        new_item = {
            "id": str(uuid.uuid4()),
            "title": data["title"],
            "content": data["content"],
            "date": data["date"]
        }

        library[data["type"]].append(new_item)

    with open(DATA_FILE, "w") as f:
        json.dump(library, f, indent=4)

    return jsonify({"status":"success"})

@app.route("/delete_content", methods=["POST"])
def delete_content():

    data = request.json
    id = data["id"]
    type = data["type"]

    with open(DATA_FILE,"r") as f:
        db = json.load(f)

    db[type] = [item for item in db[type] if str(item["id"]) != str(id)]

    with open(DATA_FILE,"w") as f:
        json.dump(db,f,indent=4)

    return jsonify({"success":True})

@app.route("/content/<type>/<id>")
def content_detail(type,id):

    if "user" not in session:
        return redirect(url_for("login"))

    with open(DATA_FILE,"r") as f:
        db = json.load(f)

    item = None

    for content in db[type]:
        if content["id"] == id:
            item = content
            break

    return render_template(
        "content_detail.html",
        item=item,
        type=type,
        name=session["user"]["name"],
        active_page="ai"
    )
    
@app.route("/template-brand")
def template_brand():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "template_brand.html",
        name=session["user"]["name"],
        active_page="template_brand"
    )

def load_seo_contents():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "seo_contents.json")

    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump({"items": []}, f, indent=4)

    with open(file_path, "r") as f:
        return json.load(f)

def save_seo_content(title, content, user_email):
    data = load_seo_contents()
    items = data.get("items", [])

    item = {
        "title": title,
        "content": content,
        "user_email": user_email
    }

    items.append(item)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "seo_contents.json")

    with open(file_path, "w") as f:
        json.dump({"items": items}, f, indent=4)

@app.route("/seo-optimizer", methods=["GET", "POST"])
def seo_optimizer():
    if "user" not in session:
        return redirect(url_for("login"))

    form_data = None
    result = None

    if request.method == "POST":
        title = request.form.get("article_title", "").strip()
        content = request.form.get("content", "").strip()

        form_data = {
            "article_title": title,
            "content": content
        }

        if title or content:
            save_seo_content(title, content, session["user"]["email"])

            word_count = len(content.split()) if content else 0
            status = "Looks good. Ready for deeper SEO analysis."

            result = {
                "title": title,
                "word_count": word_count,
                "status": status
            }

    return render_template(
        "seo_optimizer.html",
        name=session["user"]["name"],
        active_page="seo",
        form_data=form_data,
        result=result
    )

#THÊM ROUTE CHO TRANG COLLABORATION VÀ APPROVAL
@app.route("/collaboration")
def collaboration():

    if "user" not in session:
        return redirect(url_for("login"))

    import json

    with open("users.json", encoding="utf-8") as f:
        data = json.load(f)

    members = data["users"]
    activities = data["activities"]

    return render_template(
        "collaboration.html",
        name=session["user"]["name"],
        members=members,
        activities=activities
    )
    
@app.route("/invite-member", methods=["POST"])
def invite_member():

    if "user" not in session:
        return redirect(url_for("login"))

    email = request.form["email"]
    role = request.form["role"]

    with open("users.json", encoding="utf-8") as f:
        data = json.load(f)

    users = data["users"]

    # kiểm tra email tồn tại chưa
    for u in users:
        if u["email"] == email:
            return redirect(url_for("collaboration"))

    # tạo user mới
    new_user = {
        "name": email.split("@")[0],
        "email": email,
        "role": role,
        "contents": 0
    }

    users.append(new_user)

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return redirect(url_for("collaboration"))
    
@app.route("/approval")
def approval():

    if "user" not in session:
        return redirect(url_for("login"))

    with open("users.json", encoding="utf-8") as f:
        data = json.load(f)

    posts = data["posts"]

    # THỐNG KÊ TRẠNG THÁI
    pending = sum(1 for p in posts if p["status"] == "pending")
    approved = sum(1 for p in posts if p["status"] == "approved")
    rejected = sum(1 for p in posts if p["status"] == "rejected")

    return render_template(
        "approval.html",
        posts=posts,
        pending=pending,
        approved=approved,
        rejected=rejected,
        name=session["user"]["name"]
    )

# UPDATE STATUS KHI BẤM APPROVE / REJECT
@app.route("/update_status", methods=["POST"])
def update_status():

    index = int(request.form["index"])
    status = request.form["status"]

    with open("users.json", encoding="utf-8") as f:
        data = json.load(f)

    data["posts"][index]["status"] = status

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return redirect(url_for("approval"))
    
if __name__ == "__main__": # chạy ứng dụng Flask
    app.run(debug=True, port=5001) # debug=True → tự động tải lại khi code thay đổi và hiển thị lỗi chi tiết hơn