# TDD 测试规范

## 测试文件组织

```
tests/
├── unit/              # 单元测试
│   ├── test_stock_repo.py
│   ├── test_user_repo.py
│   └── test_news_repo.py
├── integration/      # 集成测试
│   ├── test_db_integration.py
│   └── test_api_integration.py
└── e2e/              # 端到端测试
    └── test_workflow.py
```

## 测试用例要求

每个测试文件需包含：

### 1. 正常场景 (Normal Case)
- 测试核心功能正常工作
- 验证正常输入返回正确输出

### 2. 边界场景 (Boundary Case)
- 空值、空字符串
- 边界值（如最大值、最小值）
- 临界条件

### 3. 异常场景 (Error Case)
- 网络错误
- 数据库连接失败
- 无效输入
- 权限错误

## 测试工具

- pytest
- pytest-mock
- faker

## 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行端到端测试
pytest tests/e2e/
```
