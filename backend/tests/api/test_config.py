"""
测试模型配置 API 端点
"""
import pytest
from fastapi import status


class TestCreateModelConfig:
    """创建模型配置测试"""

    def test_create_model_config_success(self, client, test_db):
        """测试成功创建模型配置"""
        # 先注册并登录用户
        user_data = {
            "username": "modeluser",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "modeluser",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建模型配置
        model_data = {
            "name": "Test OpenAI",
            "provider": "openai",
            "api_base": "https://api.openai.com/v1",
            "encrypted_api_key": "encrypted_key_here",
            "model_name": "gpt-3.5-turbo",
            "is_default": True,
            "is_active": True,
        }
        
        response = client.post(
            "/api/config/models",
            json=model_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test OpenAI"
        assert data["provider"] == "openai"

    def test_create_model_config_unauthorized(self, client, test_db):
        """测试未授权创建模型配置"""
        model_data = {
            "name": "Test Model",
            "provider": "openai",
            "api_base": "https://api.openai.com/v1",
            "encrypted_api_key": "encrypted_key",
            "model_name": "gpt-3.5-turbo",
        }
        
        response = client.post(
            "/api/config/models",
            json=model_data,
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListModelConfigs:
    """获取模型配置列表测试"""

    def test_list_model_configs_success(self, client, test_db):
        """测试成功获取模型配置列表"""
        # 注册并登录
        user_data = {
            "username": "listuser",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "listuser",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建两个模型配置
        for i in range(2):
            model_data = {
                "name": f"Model {i}",
                "provider": "openai",
                "api_base": "https://api.openai.com/v1",
                "encrypted_api_key": "key",
                "model_name": "gpt-3.5-turbo",
            }
            client.post("/api/config/models", json=model_data, headers=headers)
        
        # 获取列表
        response = client.get("/api/config/models", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_model_configs_empty(self, client, test_db):
        """测试空模型配置列表"""
        # 注册并登录
        user_data = {
            "username": "emptyuser",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "emptyuser",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/config/models", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0


class TestUpdateModelConfig:
    """更新模型配置测试"""

    def test_update_model_config_success(self, client, test_db):
        """测试成功更新模型配置"""
        # 注册并登录
        user_data = {
            "username": "updateuser",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "updateuser",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建模型配置
        model_data = {
            "name": "Original Name",
            "provider": "openai",
            "api_base": "https://api.openai.com/v1",
            "encrypted_api_key": "key",
            "model_name": "gpt-3.5-turbo",
        }
        create_response = client.post(
            "/api/config/models",
            json=model_data,
            headers=headers,
        )
        model_id = create_response.json()["id"]
        
        # 更新
        update_data = {
            "name": "Updated Name",
            "is_default": True,
        }
        response = client.put(
            f"/api/config/models/{model_id}",
            json=update_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["is_default"] == True

    def test_update_model_config_not_found(self, client, test_db):
        """测试更新不存在的模型配置"""
        # 注册并登录
        user_data = {
            "username": "notfounduser",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "notfounduser",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 更新不存在的配置
        update_data = {"name": "New Name"}
        response = client.put(
            "/api/config/models/nonexistent-id",
            json=update_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteModelConfig:
    """删除模型配置测试"""

    def test_delete_model_config_success(self, client, test_db):
        """测试成功删除模型配置"""
        # 注册并登录
        user_data = {
            "username": "deleteuser",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "deleteuser",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建模型配置
        model_data = {
            "name": "To Delete",
            "provider": "openai",
            "api_base": "https://api.openai.com/v1",
            "encrypted_api_key": "key",
            "model_name": "gpt-3.5-turbo",
        }
        create_response = client.post(
            "/api/config/models",
            json=model_data,
            headers=headers,
        )
        model_id = create_response.json()["id"]
        
        # 删除
        response = client.delete(
            f"/api/config/models/{model_id}",
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_model_config_not_found(self, client, test_db):
        """测试删除不存在的模型配置"""
        # 注册并登录
        user_data = {
            "username": "deleteuser2",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "deleteuser2",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 删除不存在的配置
        response = client.delete(
            "/api/config/models/nonexistent-id",
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
