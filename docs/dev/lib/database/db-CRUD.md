---
icon: simple/markdown
title: 数据库CRUD函数使用说明
---


## 概述
这是一个基于SQLAlchemy和NoneBot-Plugin-ORM的高性能数据库CRUD工具库，提供类型安全的通用数据库操作函数。

## 快速开始

### 1. 定义数据模型
```python
from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column

class User(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    email: Mapped[str | None] = mapped_column(default=None)
```

### 2. 基本CRUD操作

#### 创建记录
```python
from your_crud_module import create

# 创建单个用户
user = await create(User, name="张三", age=25, email="zhangsan@example.com")

# 批量创建（循环调用create）
users = []
for i in range(5):
    user = await create(User, name=f"用户{i}", age=20+i)
    users.append(user)
```

#### 查询记录
```python
from your_crud_module import get_one, list_items, count, exists

# 查询单个用户
user = await get_one(User, {"name": "张三"})

# 查询用户列表（带分页和排序）
users = await list_items(
    User,
    filters={"age": 25},           # 过滤条件
    order_by=["-id", "name"],       # 排序：id降序，name升序
    offset=0,                       # 偏移量
    limit=10                        # 每页数量
)

# 统计数量
user_count = await count(User, {"age": 25})

# 判断是否存在
user_exists = await exists(User, {"name": "张三"})
```

#### 更新记录
```python
from your_crud_module import update

# 更新年龄为25的所有用户，将邮箱设置为统一值
updated_count = await update(
    User,
    filters={"age": 25},
    values={"email": "updated@example.com"}
)
```

#### 删除记录
```python
from your_crud_module import delete

# 删除年龄小于18的用户
deleted_count = await delete(User, {"age": 18})
```

#### 获取或创建
```python
from your_crud_module import get_or_create

# 如果用户不存在则创建，存在则返回现有用户
user, created = await get_or_create(
    User,
    defaults={"age": 30, "email": "default@example.com"},
    name="李四"
)
```

### 3. 高级查询功能

#### 复杂过滤条件
```python
# 多条件查询
users = await list_items(
    User,
    filters={
        "age": [25, 26, 27],        # age IN (25, 26, 27)
        "email": None,              # email IS NULL
        "name": "张三"               # name = '张三'
    }
)

# 支持的操作符
filters = {
    "age__gt": 20,                  # 大于
    "age__gte": 18,                 # 大于等于
    "age__lt": 30,                  # 小于
    "age__lte": 25,                 # 小于等于
    "name__like": "%张%",           # 模糊匹配
}
```

#### 排序和分页
```python
# 复杂排序和分页
users = await list_items(
    User,
    order_by=["-created_at", "name"],  # 按创建时间降序，姓名升序
    offset=20,                         # 跳过前20条
    limit=50                          # 取50条
)
```

## 查询条件语法

### 基本比较
```python
# 等于
{"name": "张三"}

# 不等于（使用NOT IN技巧）
{"name": ["李四", "王五"]}  # 注意：这是IN查询，需要额外处理不等于

# 为空
{"email": None}

# 不为空（使用NOT IN空列表技巧）
{"email": []}  # email NOT IN (空列表) 相当于 email IS NOT NULL
```

### 列表查询（IN操作）
```python
# 查询年龄为25、26、27的用户
{"age": [25, 26, 27]}

# 查询姓名在指定列表中的用户
{"name": ["张三", "李四", "王五"]}
```

### 排序语法
```python
# 升序
["name", "age"]          # 按name升序，然后按age升序

# 降序（前缀减号）
["-created_at", "name"]  # 按created_at降序，然后按name升序
```

## 错误处理

所有函数都包含完整的错误处理机制：

```python
try:
    user = await create(User, name="测试用户", age=25)
except IntegrityError:
    # 处理唯一约束冲突等完整性错误
    print("创建用户失败：数据冲突")
except SQLAlchemyError as e:
    # 处理其他数据库错误
    print(f"数据库操作失败：{e}")
```

## 性能建议

1. **批量操作**：使用`update`和`delete`进行批量操作，避免循环单个处理
2. **分页查询**：大数据集查询时务必使用`limit`和`offset`
3. **索引优化**：为常用的查询字段建立数据库索引
4. **连接管理**：使用完session后会自动关闭，无需手动管理

## 注意事项

1. 所有函数都是异步的，需要使用`await`调用
2. 过滤条件中的字段名必须与模型类属性名完全一致
3. 更新操作会自动过滤掉模型中不存在的字段
4. 事务在函数内部自动管理，无需外部控制

这个工具库提供了企业级的数据库操作解决方案，具有高性能、类型安全和易用性的特点。