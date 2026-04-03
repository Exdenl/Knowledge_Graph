# Career Knowledge Graph Recommendation System

## 项目简介

本项目构建了一个基于知识图谱的职业推荐系统，实现了从文本数据中进行信息抽取，并基于知识图谱进行职位匹配推荐。

## 方法流程

1. 数据收集：构建招聘文本数据
2. 信息抽取：

   * 实体识别（职位、技能）
   * 关系抽取（requires）
3. 知识图谱构建（三元组）
4. 推荐系统：

   * 基于技能匹配的评分机制

## 推荐算法

Matching Score = 匹配技能数 / 职位需求技能数

## 项目结构

* extraction：信息抽取
* kg：知识图谱构建
* recommendation：推荐系统

## 运行方式

python main.py

## 示例结果

系统可根据用户技能推荐最适合的职位，并给出匹配度评分。

## 作者

YM
