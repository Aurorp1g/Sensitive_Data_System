# 敏感数据识别与分类系统
<!-- Author: 谭鸿威、郭欣、潘永键、张泽佳 -->
<!-- University: 佛山大学 -->
<!-- Laboratory: 网络安全实验室 -->
<!-- Date: 2025-04-17-->

本项目是基于paddleocr和tshark的敏感数据识别与分类系统。

以下是一个格式化为 Markdown 的 `README.md` 文件内容，适用于在 GitHub 上展示你的项目结构和模块架构：

---

# Sensitive Data System

## 系统目录结构

```
Sensitive_Data_System/
│
├── .conda/                     # 系统运行虚拟环境配置
│
├── Final_result/               # 最终结果输出目录
│
├── config/                     # 配置模块
│   └── PATH.py                 # 系统路径配置
│
├── Log/                        # 系统 pcap 处理日志目录
│
├── pcap_analysis/              # pcap 处理核心模块
│   ├── data_processor.py       # 数据解析器
│   ├── flow_processor.py       # 网络流处理器
│   ├── pcap_parser.py          # pcap 文件解析器
│   └── report_generator.py     # 报告生成器
│
├── image_ocr/                  # OCR 处理模块
│   ├── OCR_model/              # 身份证/银行卡 OCR 模型
│   ├── card_processor.py       # 身份证/银行卡识别处理器
│   ├── parallel.py             # 多线程处理
│   └── process_utils.py        # 高效合并工具
│
├── Temp/                       # 临时文件目录
│
├── requirements.txt            # 依赖包列表
│
├── tshark/                     # tshark 工具
│
├── utils/                      # 工具模块
│   ├── clean_utils.py          # 进度显示工具
│   └── logger.py               # 日志工具
│
├── Step_1.py                   # 步骤一：pcap 文件解析
├── Step_2.py                   # 步骤二：图片 OCR 识别
├── Step_3.py                   # 步骤三：csv 结果整合
│
└── run.bat                     # 批处理文件——系统入口
```

## 系统模块架构

### pcap 处理核心模块

```
└── pcap_analysis/
    ├── report_generator.py - 主控模块
    │   ├─ PCAP 文件分片处理（>1GB 自动分割）
    │   ├─ 动态资源管理（根据 CPU 核心数自动调整进程池大小）
    │   ├─ 改进的结果合并策略（保留最新数据）
    │   ├─ 增强型错误处理（分片失败自动重试）
    │   └─ CSV 报告生成（sensitive_data.csv）
    │
    ├── pcap_parser.py - pcap 解析器
    │   ├─ 调用 TShark 解析网络包
    │   ├─ 提取 HTTP 请求元数据（时间戳/方法/URI）
    │   └─ 请求分组（按 TCP 流 ID + 端点地址）
    │
    ├── data_processor.py - 数据处理器
    │   ├─ parse_multipart_data() 解析 multipart 请求
    │   └─ parse_sensitive_data() 解析 URL 编码参数
    │
    └── flow_processor.py - 流分析器
        ├─ 敏感路径识别（/login.php, /survey.php）
        └─ 图片文件自动归类（身份证/银行卡）
```

### OCR 处理核心模块

```
└── image_ocr/
    ├── OCR_model/              # 预训练模型目录
    │   ├── idcard.onnx         # 身份证识别模型
    │   └── bankcard.pth        # 银行卡识别模型
    │
    ├── card_processor.py       # 核心识别器
    │   ├─ 身份证关键字段提取：
    │   │   - 姓名/性别/民族
    │   │   - 出生日期/住址
    │   │   - 身份证号码
    │   └─ 银行卡信息提取：
    │       - 卡号/有效期
    │       - 持卡人姓名
    │
    ├── parallel.py             # 并行处理框架
    │   ├─ 基于 ThreadPoolExecutor
    │   ├─ 批量任务调度（每批次 100 张）
    │   └─ 异常重试机制（max_retries=3）
    │
    └── process_utils.py
        │
        └─ merge_results()      # 多线程结果合并
            - 按手机号聚合数据
            - 自动去重（保留最高质量图片）
```

### 工具模块

```
└── utils/
    ├── logger.py - 增强型日志系统
    │   ├─ 分片处理日志跟踪
    │   └─ 多进程安全日志记录
    │
    └── clean_utils.py - 安全清理模块
        ├─ 临时文件生命周期管理
        └─ 异常安全删除（自动重试机制）
```

### 配置模块

```
└── config/
    └── PATH.py - 系统路径配置
        ├─ 路径常量定义
        └─ 动态路径生成
```
