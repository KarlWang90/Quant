# 本地量化交易系统说明书与操作指南

本文档面向当前仓库的使用者，目标是回答三件事：

1. 现在这个框架已经实现了什么。
2. 每个模块在系统里负责什么。
3. 以 A 股为例，怎样跑一遍完整测试流程。

注意：

- 当前项目已经从“纯脚手架”升级到“可跑通的原型系统”。
- 它适合研究、流程联调和小规模纸面测试。
- 它还不是完整实盘系统，尤其在港股自动数据接入、成交回写、完整风控和系统化测试方面仍有缺口。

## 1. 当前框架总览

系统现在的主流程是：

1. 读入数据
2. 清洗和标准化
3. 构建特征
4. 生成未来收益标签
5. 做 walk-forward 样本外训练与打分
6. 生成候选信号
7. 结合流动性约束和当前持仓，生成再平衡订单
8. 输出待审批订单
9. 通过 Open Claw 发送消息提示
10. 记录审批文件
11. 使用最新订单做延迟执行回测

当前已经实现的核心能力：

- A 股数据接入：支持 `csv`、`baostock`、`tushare`、`akshare`
- 本地持仓/成交 CSV 接入
- 价量、基本面、事件、RD-Agent 信号融合
- walk-forward 样本外打分，减少未来数据泄露
- 基于当前持仓生成 `BUY/SELL` 再平衡建议
- 生成待审批订单文件和审批记录
- Open Claw 消息提醒
- 基础 delay-aware backtest

当前仍未完全实现的能力：

- 港股自动数据抓取
- 审批后的成交回写与真实执行回放
- 更完整的风险控制，如行业暴露、止损、仓位上限矩阵
- 标准化测试套件

## 2. 目录与模块说明

### 2.1 配置层

- [config/base.yaml](/Users/karlwang/Working/Quant/config/base.yaml)
  - 系统主配置
  - 包含数据源、交易参数、模型参数、验证参数、信号参数
- [config/universe.yaml](/Users/karlwang/Working/Quant/config/universe.yaml)
  - 标的池定义
  - 真实运行时主要影响数据抓取范围

### 2.2 数据层

- [src/quant/data/ingestion/__init__.py](/Users/karlwang/Working/Quant/src/quant/data/ingestion/__init__.py)
  - 所有数据入口的统一调度
  - 负责读取行情、持仓、成交、基本面、事件、RD-Agent 输出
- [src/quant/data/cleaning.py](/Users/karlwang/Working/Quant/src/quant/data/cleaning.py)
  - 行情去重、字段校验、数值标准化
- [src/quant/data/corporate_actions.py](/Users/karlwang/Working/Quant/src/quant/data/corporate_actions.py)
  - 复权因子处理

### 2.3 特征与标签

- [src/quant/features/price_volume.py](/Users/karlwang/Working/Quant/src/quant/features/price_volume.py)
  - 收益率、均线、波动率、成交额、流动性特征
- [src/quant/features/fundamentals.py](/Users/karlwang/Working/Quant/src/quant/features/fundamentals.py)
  - 合并基本面
- [src/quant/features/events.py](/Users/karlwang/Working/Quant/src/quant/features/events.py)
  - 合并事件/情绪
- [src/quant/features/rdagent.py](/Users/karlwang/Working/Quant/src/quant/features/rdagent.py)
  - 合并 RD-Agent 研究分数
- [src/quant/labels/future_return.py](/Users/karlwang/Working/Quant/src/quant/labels/future_return.py)
  - 构建未来收益标签

### 2.4 模型与信号

- [src/quant/models/train.py](/Users/karlwang/Working/Quant/src/quant/models/train.py)
  - 支持 walk-forward 训练与样本外预测
- [src/quant/models/baseline_gbdt.py](/Users/karlwang/Working/Quant/src/quant/models/baseline_gbdt.py)
  - 当前默认模型：GBDT
- [src/quant/signals/signal_engine.py](/Users/karlwang/Working/Quant/src/quant/signals/signal_engine.py)
  - 根据预测分数挑选 top-k 候选信号

### 2.5 组合、订单与执行

- [src/quant/portfolio/constraints.py](/Users/karlwang/Working/Quant/src/quant/portfolio/constraints.py)
  - 最大持仓数、流动性、停牌过滤
- [src/quant/portfolio/optimizer.py](/Users/karlwang/Working/Quant/src/quant/portfolio/optimizer.py)
  - 当前采用等权目标权重
- [src/quant/execution/order_builder.py](/Users/karlwang/Working/Quant/src/quant/execution/order_builder.py)
  - 将“目标权重”映射为“基于现有持仓的买卖订单”
  - 会考虑 lot size、最大换手、最小现金缓冲、估算交易成本
- [src/quant/execution/approval.py](/Users/karlwang/Working/Quant/src/quant/execution/approval.py)
  - 输出待审批文件
  - 记录 approve/reject 决策
- [src/quant/execution/message_builder.py](/Users/karlwang/Working/Quant/src/quant/execution/message_builder.py)
  - 构造给 Open Claw 的交易建议包
- [src/quant/execution/openclaw.py](/Users/karlwang/Working/Quant/src/quant/execution/openclaw.py)
  - 通过 webhook、文件或控制台发送消息

### 2.6 主流程脚本

- [scripts/run_pipeline.py](/Users/karlwang/Working/Quant/scripts/run_pipeline.py)
  - 主入口
- [scripts/backtest.py](/Users/karlwang/Working/Quant/scripts/backtest.py)
  - 用订单文件回测
- [scripts/approve_orders.py](/Users/karlwang/Working/Quant/scripts/approve_orders.py)
  - 将最新订单标记为 `APPROVE` 或 `REJECT`
- [scripts/demo_a_share_smoke.py](/Users/karlwang/Working/Quant/scripts/demo_a_share_smoke.py)
  - 一键生成 A 股演示数据并跑通完整流程

## 3. 数据输入与输出

### 3.1 输入数据

最常见输入目录是 `data/raw/`，主要文件包括：

- `market.csv`
  - 行情数据
- `positions.csv`
  - 当前持仓快照
- `trades.csv`
  - 历史成交
- `fundamentals.csv`
  - 基本面数据
- `events.csv`
  - 舆情或事件数据
- `rdagent_signals.csv`
  - RD-Agent 输出的外部分数

数据字段说明见：

- [data/metadata/data_dictionary.md](/Users/karlwang/Working/Quant/data/metadata/data_dictionary.md)

### 3.2 输出数据

主流程运行后重点查看：

- `data/processed/market.csv`
  - 清洗后的行情
- `data/features/features.csv`
  - 特征表
- `data/signals/signal_history.csv`
  - 历史样本外信号
- `data/signals/latest_orders.csv`
  - 最新待执行订单
- `data/logs/approval_request_*.csv`
  - 待审批订单快照
- `data/logs/approval_approve_*.csv`
  - 人工批准记录
- `data/logs/approval_reject_*.csv`
  - 人工拒绝记录

## 4. 标准操作流程

### 4.1 环境准备

在仓库根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

如果你要通过 Open Claw 文件模式看消息，可以在 `.env` 里配置：

```bash
OPENCLAW_MESSAGE_FILE=/Users/karlwang/Working/Quant/openclaw_messages.jsonl
```

### 4.2 日常运行流程

1. 准备数据
   - 如果用 `csv` 模式，把数据放进 `data/raw/`
   - 如果用 `baostock/tushare/akshare`，修改 [config/base.yaml](/Users/karlwang/Working/Quant/config/base.yaml)
2. 运行主流程

```bash
./.venv/bin/python scripts/run_pipeline.py --config config/base.yaml
```

3. 查看输出
   - `data/signals/latest_orders.csv`
   - `data/logs/approval_request_*.csv`
4. 手动审批

```bash
./.venv/bin/python scripts/approve_orders.py --decision approve
```

或者：

```bash
./.venv/bin/python scripts/approve_orders.py --decision reject
```

5. 回测历史信号

更推荐直接回测 `signal_history.csv`，因为它包含历史样本外信号。

```bash
./.venv/bin/python scripts/backtest.py --config config/base.yaml
```

## 5. A 股完整流程测试

这里给两个测试方案：

### 方案 A：最快速的完整流程测试

适合先验证“系统能不能全链路跑通”。

直接执行：

```bash
./.venv/bin/python scripts/demo_a_share_smoke.py
```

这个脚本会自动完成：

1. 在 `demo_runs/a_share_smoke/<timestamp>/` 下创建一套独立测试目录
2. 生成 A 股演示行情、基本面、事件、持仓、成交数据
3. 自动生成一份测试配置
4. 跑完整主流程
5. 自动生成订单、审批文件、Open Claw 消息
6. 自动做一次基于 `signal_history.csv` 的基础回测
7. 在终端打印关键输出文件路径

跑完后重点看这些文件：

- `demo_runs/a_share_smoke/<timestamp>/signals/latest_orders.csv`
- `demo_runs/a_share_smoke/<timestamp>/signals/signal_history.csv`
- `demo_runs/a_share_smoke/<timestamp>/logs/approval_request_*.csv`

如果你想对这次演示订单做审批测试，再执行：

```bash
./.venv/bin/python scripts/approve_orders.py \
  --orders demo_runs/a_share_smoke/<timestamp>/signals/latest_orders.csv \
  --decision approve \
  --log-dir demo_runs/a_share_smoke/<timestamp>/logs
```

### 方案 B：使用真实 A 股数据做一次流程测试

适合你开始验证真实日频数据接入。

#### 步骤 1：确认配置为 A 股

检查 [config/base.yaml](/Users/karlwang/Working/Quant/config/base.yaml)：

- `data_sources.market.provider`
- `data_sources.market.start`
- `data_sources.market.end`
- `universe.markets`

如果你用 `baostock`，建议先保持默认：

```yaml
data_sources:
  market:
    provider: baostock
    start: "2020-01-01"
    end: "2024-12-31"
    universe_file: config/universe.yaml
```

#### 步骤 2：设置 A 股标的池

编辑：

- [config/universe.yaml](/Users/karlwang/Working/Quant/config/universe.yaml)

例如：

```yaml
A_SHARE:
  - 000001.SZ
  - 000002.SZ
  - 600000.SH
  - 510300.SH
```

#### 步骤 3：准备持仓与成交

如果你只想测流程，可以先复制样例：

```bash
cp data/raw/positions.sample.csv data/raw/positions.csv
cp data/raw/trades.sample.csv data/raw/trades.csv
```

如果你有真实券商导出文件，则把它们整理成系统定义的字段格式，覆盖：

- `data/raw/positions.csv`
- `data/raw/trades.csv`

#### 步骤 4：可选地准备基本面与事件数据

如果你暂时没有，也可以先不放，系统会继续运行。

如果要测试融合特征，可以复制样例：

```bash
cp data/raw/fundamentals.sample.csv data/raw/fundamentals.csv
cp data/raw/events.sample.csv data/raw/events.csv
```

#### 步骤 5：运行主流程

```bash
./.venv/bin/python scripts/run_pipeline.py --config config/base.yaml
```

你应该能看到：

1. 清洗后的行情写入 `data/processed/market.csv`
2. 特征写入 `data/features/features.csv`
3. 样本外信号写入 `data/signals/signal_history.csv`
4. 待执行订单写入 `data/signals/latest_orders.csv`
5. 待审批文件写入 `data/logs/approval_request_*.csv`
6. 控制台或 Open Claw 文件里出现交易建议消息

#### 步骤 6：查看订单内容

重点看：

```bash
head data/signals/latest_orders.csv
```

常见字段解释：

- `side`
  - `BUY` 或 `SELL`
- `trade_qty`
  - 建议交易股数
- `current_qty`
  - 当前持仓
- `target_qty`
  - 建议调整后的目标持仓
- `estimated_trade_value`
  - 估算成交金额
- `estimated_cost`
  - 估算交易成本
- `approval_status`
  - 默认 `PENDING`

#### 步骤 7：模拟人工审批

批准：

```bash
./.venv/bin/python scripts/approve_orders.py --decision approve
```

拒绝：

```bash
./.venv/bin/python scripts/approve_orders.py --decision reject
```

运行后会在 `data/logs/` 下生成审批记录文件。

#### 步骤 8：运行回测

```bash
./.venv/bin/python scripts/backtest.py --config config/base.yaml
```

如果你确实想单独检查某一份订单文件，也可以显式指定：

```bash
./.venv/bin/python scripts/backtest.py \
  --config config/base.yaml \
  --signals data/signals/latest_orders.csv
```

但要注意：`latest_orders.csv` 往往对应最新交易日，如果后面没有未来价格，回测结果里的 `count_days` 可能是 `0`，这是正常现象。

## 6. 推荐的第一次测试顺序

建议你第一次按下面顺序走：

1. 先跑 `scripts/demo_a_share_smoke.py`
2. 看懂输出文件之间的关系
3. 再切到 `config/base.yaml + baostock`
4. 再替换成你自己的 `positions.csv` 和 `trades.csv`
5. 最后再接入自己的基本面、事件和 RD-Agent 分数

## 7. 当前最重要的注意事项

- A 股目前是这个系统最成熟的路径，港股自动化接入还没完成。
- 当前模型是基线 GBDT，重点在“流程正确”和“可迭代”，不是追求模型花哨。
- `latest_orders.csv` 是“建议单”，不是自动交易指令。
- 真实实盘前，建议先做纸面交易或小资金联调至少 1 到 3 个月。
- 如果你改了数据字段格式，优先同步更新 [data/metadata/data_dictionary.md](/Users/karlwang/Working/Quant/data/metadata/data_dictionary.md)。

## 8. 下一步建议

如果你准备继续推进，最建议优先做这三件事：

1. 用你自己的券商持仓和成交文件替换样例，验证订单生成是否符合你的真实持仓逻辑。
2. 固定一套 A 股标的池，连续跑 2 到 4 周，观察信号稳定性和审批体验。
3. 再决定是先补“完整回放闭环”，还是先补“港股数据接入”。
