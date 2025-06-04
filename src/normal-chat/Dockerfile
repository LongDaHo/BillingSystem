# Sử dụng image python 3.10.12 chính thức
FROM python:3.10.12

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements (nếu có)
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose port 8000
EXPOSE 8080

# Chạy ứng dụng với uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
