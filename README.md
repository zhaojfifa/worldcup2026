# WorldCup2026 AI Intelligence Center

2026 世界杯 AI 情报中心 MVP。

## 项目定位

面向越南和缅甸球迷的世界杯 AI 预测与赛事情报平台。

本项目不做博彩，不提供真实投注，不承诺收益。MTC 仅为平台积分，不可提现、不可转让、不可交易，不作为金融资产。

## MVP 核心功能

1. 首页 / AI 预测卡片流
2. 单场预测详情页
3. 完整 AI 报告页
4. Token / MTC 积分中心
5. 社群订阅页
6. 自动数据获取
7. Baseline AI 预测
8. 自动解释报告
9. 赛前 30 分钟临场修正
10. Render 部署与 Cloudflare R2 存储预留

## 视觉方向

坚持世界杯官网式权威感，以蓝、白、金、绿为主色。  
不使用 FIFA 官方 Logo、奖杯图或受保护素材。  
Dribbble 仅作为移动端卡片与交互参考。

## 架构方向

DataSource → Feature Builder → Prediction Engine → Explanation Engine → Report Generator → Frontend API

第一版使用 baseline rules model，后续可替换为 LightGBM / CatBoost / SHAP。

## 合规边界

禁止：

- 博彩
- 下注
- 现金投注
- 稳赚
- 必中
- 跟单
- 购彩
- 回报率
- 返奖
- 提现

所有预测仅供 AI 数据分析和球迷娱乐参考。

## 当前原型

`wc-ai-h5.html` 是当前 H5 单文件交互原型，后续由 Claude 工程化拆分为前端组件。
