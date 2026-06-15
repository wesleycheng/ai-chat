"""
测试密码安全和 JWT token 功能
"""
import pytest
from datetime import timedelta
from jose import jwt, JWTError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings


class TestPasswordSecurity:
    """密码安全测试"""

    def test_hash_password(self):
        """测试密码哈希"""
        password = "TestPass123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt 哈希格式
        assert len(hashed) == 60  # bcrypt 哈希长度

    def test_verify_password_success(self):
        """测试密码验证成功"""
        password = "TestPass123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True

    def test_verify_password_failure(self):
        """测试密码验证失败"""
        password = "TestPass123!"
        wrong_password = "WrongPass456!"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) == False

    def test_same_password_different_hash(self):
        """测试相同密码产生不同哈希"""
        password = "TestPass123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # bcrypt 使用随机盐


class TestAccessToken:
    """访问 Token 测试"""

    def test_create_access_token(self):
        """测试创建访问 token"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT token 长度

    def test_create_access_token_with_ttl(self):
        """测试创建带过期时间的 token"""
        data = {"sub": "testuser"}
        ttl = timedelta(minutes=30)
        token = create_access_token(data, ttl)
        
        # 解码验证
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["type"] == "access"

    def test_decode_token_success(self):
        """测试解码 token 成功"""
        data = {"sub": "testuser", "type": "access"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        assert payload["sub"] == "testuser"
        assert payload["type"] == "access"

    def test_decode_token_failure(self):
        """测试解码 token 失败"""
        invalid_token = "invalid.token.here"
        
        result = decode_token(invalid_token)
        assert result is None


class TestRefreshToken:
    """刷新 Token 测试"""

    def test_create_refresh_token(self):
        """测试创建刷新 token"""
        data = {"sub": "testuser"}
        token = create_refresh_token(data)
        
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"

    def test_refresh_token_longer_lived(self):
        """测试刷新 token 比访问 token 寿命更长"""
        access_data = {"sub": "testuser"}
        refresh_data = {"sub": "testuser"}
        
        access_token = create_access_token(access_data)
        refresh_token = create_refresh_token(refresh_data)
        
        access_payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        refresh_payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # 刷新 token 的过期时间应该更晚
        assert refresh_payload["exp"] > access_payload["exp"]
