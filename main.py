from flask import Flask, render_template, request, redirect
import pandas as pd
import os

app = Flask(__name__)
CSV_FILE = "member.csv"

if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["name", "add", "tel", "email"]).to_csv(CSV_FILE, index=False)

@app.route("/")
def display_table():
    # CSV 파일 읽기
    data = pd.read_csv(CSV_FILE)
    # HTML로 변환하여 렌더링에 전달
    return render_template("table.html", tables=[data.to_html(classes='data', header="true")], titles=data.columns.values)

# 새로운 데이터를 CSV에 추가하는 함수
@app.route("/add", methods=["POST"])
def add_member():
    # 폼 데이터 가져오기
    name = request.form.get("name")
    add = request.form.get("add")
    tel = request.form.get("tel")
    email = request.form.get("email")

    # writeCSV 함수 호출 (데이터 추가)
    writeCSV(name, add, tel, email)

    # 데이터 추가 후 테이블 페이지로 리다이렉트
    return redirect("/")

# writeCSV 함수 정의: 데이터를 CSV 파일에 추가
def writeCSV(name, add, tel, email):
    try:
        # 새로운 데이터 행 생성
        new_data = f"{name},{add},{tel},{email}\n"    
        # CSV 파일에 추가 (모드: 'a' -> append)     
        with open(CSV_FILE, mode="a", encoding="utf-8") as file:
            file.write(new_data)
        return "success write to CSV"
    except Exception as e:
        return f"Error writing to CSV: {e}"
        


if __name__ == "__main__":
    app.run(debug=True)
