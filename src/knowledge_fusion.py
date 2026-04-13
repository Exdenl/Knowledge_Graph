# src/knowledge_fusion.py
class KnowledgeFusion:
    def __init__(self):
        # 扩展别名库，涵盖维基百科中常见的称呼
        self.alias_map = {
            "Mathison": "艾伦·图灵",
            "Alan": "艾伦·图灵",
            "Turing": "艾伦·图灵",
            "Alan Turing": "艾伦·图灵",
            "艾伦": "艾伦·图灵",
            "诺伊曼": "约翰·冯·诺伊曼",
            "Neumann": "约翰·冯·诺伊曼",
            "剑桥": "剑桥大学",
            "普林斯顿": "普林斯顿大学",
            "曼彻斯特": "曼彻斯特大学"
        }
        self.rel_map = {
            "制造": "研发",
            "包含": "组成部分",
            "涉及": "研究领域",
            "用于": "应用场景",
            "评论": "学术评价",
            "协助": "合作伙伴"
        }

    def fuse(self, triples):
        fused_triples = []
        seen = set()

        for t in triples:
            h, r, o = t['head'], t['rel'], t['tail']
            
            # 1. 统一核心实体名称 (处理碎片)
            h = self.alias_map.get(h, h)
            o = self.alias_map.get(o, o)
            
             # 2. 关系清洗 (重点！)
            # 过滤掉长度为1的关系（如：论、称、造）
            if len(r) <= 1:
                continue
            
            # 关系语义映射
            r = self.rel_map.get(r, r)
            
            # 3. 噪声过滤：如果关系词仍然是介词性很强的词，丢弃
            if r in ['诸如', '关于', '对于', '具有']:
                continue

            # 4. 碎片节点过滤 (如：和子、即、马赛克等无意义实体)
            if len(h) <= 1 or len(o) <= 1:
                continue
            
            pair = f"{h}-{r}-{o}"
            if pair not in seen and h != o:
                fused_triples.append({"head": h, "rel": r, "tail": o})
                seen.add(pair)
                
        return fused_triples