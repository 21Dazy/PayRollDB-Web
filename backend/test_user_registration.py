#!/usr/bin/env python3
"""
用户注册API测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_verify_employee():
    """测试员工验证API"""
    url = f"{BASE_URL}/registration/verify-employee"
    data = {
        "real_name": "张三",
        "id_card": "110101199001011234",  # 示例身份证号
        "employee_id": 1  # 示例员工ID
    }
    
    response = requests.post(url, json=data)
    print("=== 测试员工验证 ===")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_send_verification_code():
    """测试发送验证码API"""
    url = f"{BASE_URL}/registration/send-verification-code"
    data = {
        "phone": "13800138000"
    }
    
    response = requests.post(url, json=data)
    print("=== 测试发送验证码 ===")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    
    return response.json().get("debug_code")

def test_register_user(verification_code=None):
    """测试用户注册API"""
    url = f"{BASE_URL}/registration/register"
    data = {
        "username": "testuser001",
        "password": "password123",
        "real_name": "张三",
        "id_card": "110101199001011234",
        "phone": "13800138000",
        "email": "test@example.com",
        "employee_id": 1,
        "verification_code": verification_code
    }
    
    response = requests.post(url, json=data)
    print("=== 测试用户注册 ===")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    
    return response.json()

def test_get_my_registration(username):
    """测试查询注册状态API"""
    url = f"{BASE_URL}/registration/my-registration"
    params = {"username": username}
    
    response = requests.get(url, params=params)
    print("=== 测试查询注册状态 ===")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def main():
    """主测试函数"""
    print("开始测试用户注册API...")
    print("注意：请确保后端服务正在运行在 http://localhost:8000")
    print()
    
    try:
        # 1. 测试员工验证
        test_verify_employee()
        
        # 2. 测试发送验证码
        verification_code = test_send_verification_code()
        
        # 3. 测试用户注册
        registration_result = test_register_user(verification_code)
        if registration_result and "username" in registration_result:
            username = registration_result["username"]
            
            # 4. 测试查询注册状态
            test_get_my_registration(username)
        
        print("测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("错误：无法连接到后端服务，请确保服务正在运行")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    main() 