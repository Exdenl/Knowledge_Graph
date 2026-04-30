# src/visualizer.py
import networkx as nx
from pyvis.network import Network
import os

TAG_STYLES = {
    "PER": {"color": "#ff7675", "border": "#d63031", "label": "👤 人物实体"},
    "ORG": {"color": "#74b9ff", "border": "#0984e3", "label": "🏛️ 机构实体"},
    "MISC": {"color": "#55efc4", "border": "#00b894", "label": "💡 概念实体"},
    "CORE": {"color": "#fdcb6e", "border": "#e17055", "label": "🌟 核心主角"}
}

def generate_graph(triples_data, output_path="output_graph.html"):
    print("[可视化模块] 正在进行图谱美化渲染...")
    G = nx.DiGraph()
    
    # 1. 统计节点度数
    node_degrees = {}
    for item in triples_data:
        h_name, t_name = item["head"]["name"], item["tail"]["name"]
        node_degrees[h_name] = node_degrees.get(h_name, 0) + 1
        node_degrees[t_name] = node_degrees.get(t_name, 0) + 1

    # 2. 构建图节点与边
    for item in triples_data:
        h, r, t, weight = item['head'], item['rel'], item['tail'], item.get('weight', 1)
        h_name, h_type = h['name'], h.get('type', 'MISC')
        t_name, t_type = t['name'], t.get('type', 'MISC')
        
        if h_name == "艾伦·图灵": h_type = "CORE"
        if t_name == "艾伦·图灵": t_type = "CORE"

        h_style = TAG_STYLES.get(h_type, TAG_STYLES["MISC"])
        t_style = TAG_STYLES.get(t_type, TAG_STYLES["MISC"])
        
        # 修复大小计算，确保为浮点数
        h_size = float(min(15 + (node_degrees.get(h_name, 0) * 2.0), 55))
        t_size = float(min(15 + (node_degrees.get(t_name, 0) * 2.0), 55))
        
        h_title = f"{h_style['label']}\n名称: {h_name}\n图谱连接度: {node_degrees.get(h_name, 0)}"
        t_title = f"{t_style['label']}\n名称: {t_name}\n图谱连接度: {node_degrees.get(t_name, 0)}"

        font_style = {"color": "#ecf0f1", "strokeWidth": 2, "strokeColor": "#2c3e50"}

        # 删除了有冲突的 shadow=True，保证最高兼容性
        G.add_node(h_name, title=h_title, size=h_size, shape="dot", borderWidth=2,
                   color={"background": h_style["color"], "border": h_style["border"]},
                   font=font_style)
        
        G.add_node(t_name, title=t_title, size=t_size, shape="dot", borderWidth=2,
                   color={"background": t_style["color"], "border": t_style["border"]},
                   font=font_style)
        
        edge_title = f"关系: {r}\n证据频次: {weight}"
        G.add_edge(h_name, t_name, label=r, title=edge_title, value=float(weight), 
                   color="#7f8c8d", arrows="to")
        
    # 3. PyVis 画布配置
    # 【修复1】删除了引起 Bug 的 heading 参数
    net = Network(height='100vh', width='100%', bgcolor='#1e272e', font_color='#dfe6e9', directed=True)
    net.from_nx(G)
    
    # 4. 高级物理引擎与 UI 配置
    # 【修复2】使用原生 Python 方法代替 JavaScript 字符串注入，彻底解决卡死 0%
    net.force_atlas_2based(
        gravity=-120, 
        central_gravity=0.01, 
        spring_length=180, 
        spring_strength=0.05, 
        damping=0.8
    )
    
    # 开启物理参数调节面板 (答辩装逼利器)
    net.show_buttons(filter_=['physics'])
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    net.write_html(output_path)
    print(f"🎉 动态交互图谱渲染完毕！")