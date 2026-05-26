---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'Noto Sans TC', 'PingFang TC', sans-serif;
    font-size: 28px;
  }
  section.lead {
    text-align: center;
    justify-content: center;
  }
  section.lead h1 {
    font-size: 96px;
    font-weight: 900;
    color: #1a1a2e;
    letter-spacing: 4px;
  }
  section.lead p {
    font-size: 24px;
    color: #555;
  }
  h2 {
    border-bottom: 3px solid #4a90e2;
    padding-bottom: 8px;
    color: #1a1a2e;
  }
  table {
    font-size: 22px;
    width: 100%;
  }
  th {
    background: #4a90e2;
    color: white;
  }
  strong {
    color: #4a90e2;
  }
  ul li {
    margin-bottom: 8px;
  }
---

<!-- _class: lead -->

# GenBI

**BI 報表的最後一哩路**

---

## Laurence Chen / 陳家宏

- Clojure、dbt-Taipei 線下活動主辦人
- IT 顧問、講者、作家
- 《從試算表到資料平台－重構資料工程的技術與團隊》

![](images/book.png)

---

## Agenda

* BI 報表的最後一哩路
* LLM && GenBI
* Data Privacy
* Implementation Issues

---

## BI 報表的最後一哩路

假設你的公司已經有了 (資料平台) **Modern Data Stack**，資料倉儲的資料已整理好了。

但是，你的 user 告訴你：

- 😕 **「很難用，因為我不會寫 SQL」**
- 🐌 **「很難用，有一些複雜的需求，不知如何表達」**

---

## 解法的矛盾 (problem)

**BI Visualization Layer**
- Application 生成 SQL
- 彈性有限

**Pure SQL**
- 幾乎可以處理 95% 的問題
- 一般 user 不會寫

---

## 用 LLM 來生成 SQL (solution)

用 LLM 來理解三件事：

1. 理解 **Ontology**（資料語意）
2. 理解 **User Intention**（使用者意圖）
3. **翻譯** Intention → Query

---

## Data Privacy

> 公司資料庫裡的資料會不會外流到 LLM provider？

- 只傳送 **Ontology（結構定義）**，不傳原始資料
- 可搭配 private/local LLM 方案

---

## Access Control

- Identity-First Architecture

> 每一個 request 從進入系統的那一刻起，就攜帶著 user identity、permissions 和 workspace context，直到 tools 執行完畢。

---

## Complex User Intent

- 兩大類解法
  - 建立「語意模型」　 
 - 持續從記憶學習 

---

## Decision Criteria

- 是否想要跟 BI view layer 整合？
   - Metabase 已經有 Metabot 
- Access control?
- Complex User Intent？