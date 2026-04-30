# src/knowledge_fusion.py
import re

class KnowledgeFusion:
    def __init__(self):
        # 1. 核心实体统一词典 (通过正向映射表动态生成，方便后续扩充)
        self.core_entities = {
            "艾伦·图灵":["图灵", "Alan Turing", "Turing", "Alan", "Mathison", "艾伦"],
            "约翰·冯·诺伊曼":["诺伊曼", "冯·诺依曼", "Neumann"],
            "普林斯顿大学":["普林斯顿", "Princeton"],
            "剑桥大学": ["剑桥", "Cambridge"],
            "第二次世界大战":["二战", "WWII", "WW2"],
            "恩尼格玛密码机":["恩尼格玛", "Enigma", "密码机"]
        }
        # 自动展开为 O(1) 查找的字典
        self.alias_map = {}
        for standard_name, aliases in self.core_entities.items():
            for alias in aliases:
                self.alias_map[alias.lower()] = standard_name

        # 2. 基于正则的“本体关系映射” (Ontology Mapping)
        # 用来捕获前置抽取引擎拿到的复杂短语 (如“曾就读于” -> “求学于”)
        self.ontology_rules =[
            (r'就读|毕业|考入|求学|学习|进修', '求学于'),
            (r'工作|加入|任教|入职|调往|供职', '任职于'),
            (r'提出|创立|发明|设计|创造|开发|制造', '发明/提出'),
            (r'获得|授予|赢得|颁发|追授', '荣获'),
            (r'称赞|誉为|称为|评价|视为', '被誉为'),
            (r'研究|探讨|沉迷|致力|发表', '研究领域'),
            (r'结识|协助|指导|合作|认识', '合作伙伴/导师'),
            (r'影响|启发|奠定', '产生影响')
        ]

    def _clean_text(self, text):
        """实体边界清洗：去除 CRF 切词偶尔带入的头尾标点符号"""
        text = text.strip()
        # 去除开头和结尾的非字母、非汉字、非数字字符 (如："计算机科学，" -> "计算机科学")
        return re.sub(r'^[^\w\u4e00-\u9fa5]+|[^\w\u4e00-\u9fa5]+$', '', text)

    def _resolve_entity(self, name):
        """实体消歧与规范化"""
        name = self._clean_text(name)
        # 别名映射
        if name.lower() in self.alias_map:
            return self.alias_map[name.lower()]
            
        return name

    def _normalize_relation(self, rel):
        """关系本体对齐：利用正则模糊匹配复杂自然语言"""
        rel = self._clean_text(rel)
        for pattern, std_rel in self.ontology_rules:
            if re.search(pattern, rel):
                return std_rel
        # 如果没有匹配上任何规范本体，保留原本的复杂短语
        return rel

    def fuse(self, triples):
        print("[知识融合模块] 正在执行边界清洗、本体映射与图谱网络收敛...")
        fused_edges = {}

        for t in triples:
            h_name = self._resolve_entity(t['head']['name'])
            h_type = t['head']['type']
            t_name = self._resolve_entity(t['tail']['name'])
            t_type = t['tail']['type']
            rel = self._normalize_relation(t['rel'])

            # 过滤逻辑：丢弃单字实体、丢弃自循环边(A-rel-A)
            if len(h_name) <= 1 or len(t_name) <= 1 or h_name == t_name:
                continue
            if len(rel) <= 1:
                continue

            # 【核心逻辑】生成唯一边签名，用于边合并与置信度计算
            edge_signature = f"{h_name}-[{rel}]->{t_name}"

            if edge_signature not in fused_edges:
                fused_edges[edge_signature] = {
                    "head": {"name": h_name, "type": h_type},
                    "rel": rel,
                    "tail": {"name": t_name, "type": t_type},
                    "weight": 1  # 置信度/频率权重
                }
            else:
                # 如果同一对实体间存在相同的关系，增加边的权重
                fused_edges[edge_signature]["weight"] += 1

        # 将字典转化为列表输出
        final_triples = list(fused_edges.values())
        
        # (可选的高级操作) 过滤掉权重为1且非核心实体的“孤立噪音边”，这里为了展示丰富度暂时保留所有
        
        return final_triples