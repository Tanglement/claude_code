# User Repository Tests

import pytest
from src.repositories.user_repo import (
    insert_user,
    get_user_by_username,
    verify_password,
    insert_user_holding,
    get_user_holdings,
    update_user_holding,
    delete_user_holding
)
from src.models.exceptions import UserNotFoundError, AuthenticationError, DatabaseError


# ==================== 用户管理测试 ====================

class TestInsertUser:
    """测试创建用户"""

    def test_insert_user_normal(self):
        """正常场景：创建用户成功"""
        result = insert_user(
            username="testuser",
            password="password123",
            email="test@example.com",
            phone="13800138000"
        )
        assert result is not None

    def test_insert_user_duplicate_username(self):
        """异常场景：用户名已存在"""
        with pytest.raises(DatabaseError, match="用户名已存在"):
            insert_user(
                username="testuser",
                password="password123"
            )

    def test_insert_user_empty_username(self):
        """边界场景：用户名为空"""
        with pytest.raises(ValueError, match="用户名不能为空"):
            insert_user(
                username="",
                password="password123"
            )

    def test_insert_user_empty_password(self):
        """边界场景：密码为空"""
        with pytest.raises(ValueError, match="密码不能为空"):
            insert_user(
                username="testuser",
                password=""
            )

    def test_insert_user_invalid_email(self):
        """异常场景：邮箱格式无效"""
        with pytest.raises(ValueError, match="邮箱格式无效"):
            insert_user(
                username="testuser",
                password="password123",
                email="invalid-email"
            )


class TestGetUserByUsername:
    """测试查询用户"""

    def test_get_user_normal(self):
        """正常场景：查询用户成功"""
        user = get_user_by_username("testuser")
        assert user is not None
        assert user["username"] == "testuser"

    def test_get_user_not_found(self):
        """异常场景：用户不存在"""
        with pytest.raises(UserNotFoundError, match="用户不存在"):
            get_user_by_username("nonexistent")

    def test_get_user_empty_username(self):
        """边界场景：用户名为空"""
        with pytest.raises(ValueError, match="用户名不能为空"):
            get_user_by_username("")


class TestVerifyPassword:
    """测试密码验证"""

    def test_verify_password_correct(self):
        """正常场景：密码正确"""
        result = verify_password("testuser", "password123")
        assert result is True

    def test_verify_password_incorrect(self):
        """异常场景：密码错误"""
        with pytest.raises(AuthenticationError, match="密码错误"):
            verify_password("testuser", "wrongpassword")

    def test_verify_password_nonexistent_user(self):
        """异常场景：用户不存在"""
        with pytest.raises(UserNotFoundError, match="用户不存在"):
            verify_password("nonexistent", "password123")


# ==================== 用户持仓测试 ====================

class TestInsertUserHolding:
    """测试插入用户持仓"""

    def test_insert_holding_normal(self):
        """正常场景：插入持仓成功"""
        result = insert_user_holding(
            user_id=1,
            symbol="600519",
            shares=100,
            cost_price=1600.00,
            purchase_date="2021-01-15"
        )
        assert result is not None

    def test_insert_holding_negative_shares(self):
        """异常场景：持股数量为负"""
        with pytest.raises(ValueError, match="持股数量必须大于0"):
            insert_user_holding(
                user_id=1,
                symbol="600519",
                shares=-100,
                cost_price=1600.00,
                purchase_date="2021-01-15"
            )

    def test_insert_holding_zero_cost(self):
        """边界场景：成本价为零"""
        with pytest.raises(ValueError, match="成本价必须大于0"):
            insert_user_holding(
                user_id=1,
                symbol="600519",
                shares=100,
                cost_price=0,
                purchase_date="2021-01-15"
            )

    def test_insert_holding_future_date(self):
        """异常场景：购买日期是未来"""
        with pytest.raises(ValueError, match="购买日期不能是未来"):
            insert_user_holding(
                user_id=1,
                symbol="600519",
                shares=100,
                cost_price=1600.00,
                purchase_date="2030-01-01"
            )


class TestGetUserHoldings:
    """测试查询用户持仓"""

    def test_get_holdings_normal(self):
        """正常场景：查询用户持仓"""
        holdings = get_user_holdings(1)
        assert isinstance(holdings, list)

    def test_get_holdings_empty(self):
        """边界场景：用户无持仓"""
        holdings = get_user_holdings(999)
        assert len(holdings) == 0

    def test_get_holdings_invalid_user_id(self):
        """异常场景：无效的用户ID"""
        with pytest.raises(ValueError, match="用户ID无效"):
            get_user_holdings(0)


class TestUpdateUserHolding:
    """测试更新用户持仓"""

    def test_update_holding_normal(self):
        """正常场景：更新持仓成功"""
        result = update_user_holding(
            holding_id=1,
            shares=200,
            cost_price=1700.00
        )
        assert result is True

    def test_update_holding_not_found(self):
        """异常场景：持仓记录不存在"""
        with pytest.raises(DatabaseError, match="持仓记录不存在"):
            update_user_holding(
                holding_id=999,
                shares=200,
                cost_price=1700.00
            )

    def test_update_holding_zero_shares(self):
        """边界场景：更新持股数量为零"""
        with pytest.raises(ValueError, match="持股数量必须大于0"):
            update_user_holding(
                holding_id=1,
                shares=0,
                cost_price=1700.00
            )


class TestDeleteUserHolding:
    """测试删除用户持仓"""

    def test_delete_holding_normal(self):
        """正常场景：删除持仓成功"""
        result = delete_user_holding(1)
        assert result is True

    def test_delete_holding_not_found(self):
        """异常场景：持仓记录不存在"""
        with pytest.raises(DatabaseError, match="持仓记录不存在"):
            delete_user_holding(999)
