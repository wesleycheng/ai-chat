"""
测试 Agent API 端点
"""
import pytest
from fastapi import status


class TestCreateAgent:
    """创建 Agent 测试"""

    def test_create_agent_success(self, client, test_db):
        """测试成功创建 Agent"""
        # 注册并登录
        user_data = {
            "username": "agentcreator",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "agentcreator",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建 Agent
        agent_data = {
            "name": "Test Agent",
            "description": "An agent for testing",
            "system_prompt": "You are a test assistant.",
            "tools": [],
            "is_active": True,
        }
        
        response = client.post(
            "/api/agents",
            json=agent_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["system_prompt"] == "You are a test assistant."

    def test_create_agent_unauthorized(self, client, test_db):
        """测试未授权创建 Agent"""
        agent_data = {
            "name": "Unauthorized Agent",
            "system_prompt": "You should not be created.",
        }
        
        response = client.post(
            "/api/agents",
            json=agent_data,
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListAgents:
    """获取 Agent 列表测试"""

    def test_list_agents_success(self, client, test_db):
        """测试成功获取 Agent 列表"""
        # 注册并登录
        user_data = {
            "username": "agentlister",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "agentlister",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建两个 Agent
        for i in range(2):
            agent_data = {
                "name": f"Agent {i}",
                "system_prompt": f"You are assistant {i}.",
            }
            client.post("/api/agents", json=agent_data, headers=headers)
        
        # 获取列表
        response = client.get("/api/agents", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_agents_empty(self, client, test_db):
        """测试空 Agent 列表"""
        # 注册并登录
        user_data = {
            "username": "emptyagent",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "emptyagent",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/agents", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0


class TestGetAgent:
    """获取单个 Agent 测试"""

    def test_get_agent_success(self, client, test_db):
        """测试成功获取 Agent"""
        # 注册并登录
        user_data = {
            "username": "agentgetter",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "agentgetter",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建 Agent
        agent_data = {
            "name": "Get Me",
            "system_prompt": "You should be retrieved.",
        }
        create_response = client.post(
            "/api/agents",
            json=agent_data,
            headers=headers,
        )
        agent_id = create_response.json()["id"]
        
        # 获取
        response = client.get(f"/api/agents/{agent_id}", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Get Me"

    def test_get_agent_not_found(self, client, test_db):
        """测试获取不存在的 Agent"""
        # 注册并登录
        user_data = {
            "username": "agentnotfound",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "agentnotfound",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/agents/nonexistent-id", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateAgent:
    """更新 Agent 测试"""

    def test_update_agent_success(self, client, test_db):
        """测试成功更新 Agent"""
        # 注册并登录
        user_data = {
            "username": "agentupdater",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "agentupdater",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建 Agent
        agent_data = {
            "name": "Original Name",
            "system_prompt": "Original prompt.",
        }
        create_response = client.post(
            "/api/agents",
            json=agent_data,
            headers=headers,
        )
        agent_id = create_response.json()["id"]
        
        # 更新
        update_data = {
            "name": "Updated Name",
            "system_prompt": "Updated prompt.",
        }
        response = client.put(
            f"/api/agents/{agent_id}",
            json=update_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["system_prompt"] == "Updated prompt."

    def test_update_agent_not_found(self, client, test_db):
        """测试更新不存在的 Agent"""
        # 注册并登录
        user_data = {
            "username": "agentupdate404",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "agentupdate404",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {"name": "New Name"}
        response = client.put(
            "/api/agents/nonexistent-id",
            json=update_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteAgent:
    """删除 Agent 测试"""

    def test_delete_agent_success(self, client, test_db):
        """测试成功删除 Agent"""
        # 注册并登录
        user_data = {
            "username": "agentdeleter",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "agentdeleter",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建 Agent
        agent_data = {
            "name": "To Delete",
            "system_prompt": "Delete me.",
        }
        create_response = client.post(
            "/api/agents",
            json=agent_data,
            headers=headers,
        )
        agent_id = create_response.json()["id"]
        
        # 删除
        response = client.delete(
            f"/api/agents/{agent_id}",
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_agent_not_found(self, client, test_db):
        """测试删除不存在的 Agent"""
        # 注册并登录
        user_data = {
            "username": "agentdelete404",
            "email": "<EMAIL_REMOVED>",
            "password": "StrongPass123!",
        }
        client.post("/api/auth/register", json=user_data)
        
        login_response = client.post("/api/auth/login", json={
            "username": "agentdelete404",
            "password": "StrongPass123!",
        })
        <SECRET_REMOVED>"access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(
            "/api/agents/nonexistent-id",
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
