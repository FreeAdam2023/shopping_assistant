shopping_assistant/
├── main.py                        # 主入口，负责运行主助理
├── assistants/                    # 各类助理相关代码
│   ├── __init__.py
│   ├── main_assistant.py          # 主助理逻辑
│   ├── product_search_assistant.py # 产品搜索助理
│   ├── cart_management_assistant.py # 购物车管理助理
│   ├── order_query_assistant.py   # 订单查询助理
├── tools/                         # 工具模块
│   ├── __init__.py
│   ├── product_tools.py           # 产品搜索工具
│   ├── cart_tools.py              # 购物车工具
│   ├── order_tools.py             # 订单工具
├── database/                      # 数据库相关
│   ├── __init__.py
│   ├── db_config.py               # 数据库配置
│   ├── initialize_db.py           # 数据库初始化脚本
├── utils/                         # 工具类
│   ├── __init__.py
│   ├── logger.py                  # 日志配置
├── requirements.txt               # 依赖列表
└── README.md                      # 项目说明文档
