# src/model_trainer.py
import os
import joblib
import jieba.posseg as pseg
import sklearn_crfsuite
from sklearn_crfsuite import metrics
from sklearn.model_selection import train_test_split
from .utils import word2features

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'crf_model.pkl')

class ModelTrainer:
    def __init__(self):
        # 初始化 CRF 序列标注算法
        # 引入 L1(c1) 和 L2(c2) 正则化惩罚项，防止模型在稀疏特征上过拟合
        self.model = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=0.1,
            c2=0.1,
            max_iterations=100,
            all_possible_transitions=True
        )
        
        # 扩展的远程监督种子词库
        self.seed_per =[
            "图灵", "冯·诺依曼", "哥德尔", "马斯克", "艾伦", "丘吉尔", 
            "罗素", "邱奇", "牛顿", "爱因斯坦", "香农", "康托尔"
        ]
        self.seed_org =[
            "剑桥大学", "普林斯顿大学", "曼彻斯特大学", "布莱切利园", 
            "皇家学会", "麻省理工", "军情六处", "政府密码学校", "贝尔实验室", "国王学院"
        ]
        self.seed_misc =[
            "恩尼格玛", "图灵机", "图灵测试", "计算机科学", "人工智能", 
            "算法", "密码学", "停机问题", "二战", "炸弹机", "逻辑", "数学", 
            "物理学", "同性恋", "法案", "计算"
        ]

    def _prepare_training_data(self):
        """
        利用启发式规则与种子词典，生成(Distant Supervision)带伪标签的语料
        """
        train_data =[]
        if not os.path.exists(RAW_DATA_DIR):
            return[]

        for filename in os.listdir(RAW_DATA_DIR):
            if filename.endswith(".txt"):
                with open(os.path.join(RAW_DATA_DIR, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    sentences =[s.strip() for s in content.split('\n') if len(s.strip()) > 5]
                    
                    for sent in sentences:
                        words_with_pos =[(w.word, w.flag) for w in pseg.cut(sent)]
                        labels =[]
                        
                        for w, p in words_with_pos:
                            # 【优化点1】严格去噪逻辑：结合种子词 + 词性 + 词长过滤
                            # 如果单纯靠 Jieba 词性，必须满足长度大于1，防止单字噪音(如："他" 被误判)
                            if any(e in w for e in self.seed_per) or (p == 'nr' and len(w) > 1):
                                labels.append('B-PER')
                            elif any(e in w for e in self.seed_org) or (p == 'nt' and len(w) > 2):
                                labels.append('B-ORG')
                            elif any(e in w for e in self.seed_misc) or (p == 'nz' and len(w) > 1):
                                labels.append('B-MISC')
                            else:
                                labels.append('O')
                        
                        # 特征抽取 (调用 utils.py 的滑动窗口特征)
                        features =[word2features(words_with_pos, i) for i in range(len(words_with_pos))]
                        train_data.append((features, labels))
                        
        return train_data

    def train(self):
        data = self._prepare_training_data()
        if not data:
            print("❌ 错误：未发现有效训练数据。")
            return

        # 剥离特征和标签
        X = [d[0] for d in data]
        y = [d[1] for d in data]

        # 【优化点2】划分训练集和验证集 (80% 训练, 20% 验证)
        # 这是遵循严谨机器学习流程的关键步骤
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print(f"[模型训练] 构建完成，训练集样本数: {len(X_train)}，验证集样本数: {len(X_test)}")
        print("[模型训练] 正在使用 L-BFGS 拟合条件随机场 (CRF) 模型...")
        self.model.fit(X_train, y_train)

        # 保存模型
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        
        # 评估模型：只关注我们关心的实体标签，忽略背景 'O'
        labels =[l for l in self.model.classes_ if l != 'O']
        y_pred = self.model.predict(X_test)
        
        print("\n" + "="*50)
        print("📊 模型独立验证集评估报告 (Hold-out Validation):")
        print("="*50)
        print(metrics.flat_classification_report(y_test, y_pred, labels=labels, digits=3))
        
        # 【优化点3】分析 CRF 的内部转移矩阵 (揭开黑盒)
        self._print_transitions(self.model.transition_features_)

    def _print_transitions(self, trans_features):
        """
        打印模型学到的转移特征权重，展示不同状态之间的转移概率倾向
        """
        print("\n🔍 CRF 内部状态转移矩阵 Top 5 (揭示模型学到的语法规则):")
        sorted_trans = sorted(trans_features.items(), key=lambda x: x[1], reverse=True)
        for (label_from, label_to), weight in sorted_trans[:5]:
            print(f"   {label_from:6} -> {label_to:6} | 权重: {weight:+.4f}")
        print("...")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train()