"""
测试认证 API 端点
"""
import pytest
from fastapi import status


class TestUserRegistration:
    """用户注册测试"""

    def test_register_success(self, client, test_db):
        """测试成功注册"""
        user_data = {
            "username": "newuser",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["username"] == "newuser"
        assert data["email"] == "<EMAIL_REMOVED>"

    def test_register_duplicate_username(self, client, test_db):
        """测试重复用户名注册"""
        user_data = {
            "username": "testuser",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        
        # 先创建一个用户
        client.post("/api/auth/register", json=user_data)
        
        # 尝试创建同名用户
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, client, test_db):
        """测试无效邮箱注册"""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "StrongPass123!",
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """用户登录测试"""

    def test_login_success(self, client, test_db):
        """测试成功登录"""
        # 先注册用户
        user_data = {
            "username": "logintest",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        # 登录
        login_data = {
            "username": "logintest",
            "password": "StrongPass123!",
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_db):
        """测试错误密码登录"""
        # 先注册用户
        user_data = {
            "username": "logintest2",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        # 错误密码登录
        login_data = {
            "username": "logintest2",
            "password": "WrongPass123!",
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client, test_db):
        """测试不存在的用户登录"""
        login_data = {
            "username": "nonexistent",
            "password": "SomePass123!",
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefresh:
    """Token 刷新测试"""

    def test_refresh_token_success(self, client, test_db):
        """测试成功刷新 token"""
        # 注册并登录
        user_data = {
            "username": "refreshtest",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "refreshtest",
            "password": "StrongPass123!",
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # 刷新 token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

    def test_refresh_token_invalid(self, client, test_db):
        """测试无效刷新 token"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentUser:
    """获取当前用户测试"""

    def test_get_me_success(self, client, test_db):
        """测试成功获取当前用户信息"""
        # 注册并登录
        user_data = {
            "username": "me",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "me",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取用户信息
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "me"

    def test_get_me_no_token(self, client, test_db):
        """测试无 token 获取用户信息"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
