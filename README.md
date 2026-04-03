# 艾伦·图灵 知识图谱 (Alan Turing Knowledge Graph)

## 📌 项目简介
本项目为个人作业01，旨在通过自然语言处理技术，从非结构化文本中提取关于“计算机科学之父”艾伦·图灵的信息，完成实体抽取、关系抽取与实体消歧，最终构建并可视化知识图谱。

## 📁 目录结构
- `data/`: 存放原始文本语料 (`turing_raw.txt`) 和抽取后的三元组数据 (`triples.json`)
- `src/`: 核心源代码目录
  - `extract.py`: 负责基于规则与正则的实体抽取、关系抽取及实体消歧逻辑
  - `build_graph.py`: 读取三元组数据，利用 NetworkX 和 PyVis 进行图谱可视化
- `output/`: 存放生成的交互式网页知识图谱 (`.html`)

## 🚀 运行流程
1. 安装依赖: `pip install -r requirements.txt`
2. 运行抽取脚本: `python src/extract.py` (将在 data 目录下生成 triples.json)
3. 运行建图脚本: `python src/build_graph.py` (将在 output 目录下生成 HTML 文件)
4. 在浏览器中打开 `output/turing_kg.html` 查看图谱。