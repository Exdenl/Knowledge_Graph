# src/crawler.py
import wikipedia
import os

class WikiCrawler:
    def __init__(self):
        # 设置语言为中文
        wikipedia.set_lang("zh")
        self.save_dir = "data/raw"
        os.makedirs(self.save_dir, exist_ok=True)

    def fetch(self, keyword):
        """为了匹配 main.py，将 fetch_data 改名为 fetch"""
        print(f"🌐 正在通过 Wikipedia 获取词条: {keyword}...")
        try:
            # auto_suggest=False 防止自动跳转到不相关的词条
            page = wikipedia.page(keyword, auto_suggest=False)
            content = page.content
            
            # 清洗：去掉末尾的参考资料等部分
            content = content.split("== 参见 ==")[0]
            content = content.split("== 参考文献 ==")[0]
            
            file_path = os.path.join(self.save_dir, f"{keyword}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 成功获取 {keyword}，长度: {len(content)} 字")
            return content
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"⚠️  词条 {keyword} 存在歧义，尝试获取第一个选项: {e.options[0]}")
            return self.fetch(e.options[0])
        except Exception as e:
            print(f"❌ 无法获取词条 {keyword}: {e}")
            return None

    def run(self):
        target_list = [
            "艾伦·图灵", "约翰·冯·诺伊曼", "计算机科学", "人工智能", 
            "恩尼格玛密码机", "剑桥大学", "普林斯顿大学", "图灵奖", 
            "库尔特·哥德尔", "布莱切利园", "曼彻斯特大学", "算法"
        ]
        for item in target_list:
            self.fetch(item)

# 关键修复：添加这个函数以解决 main.py 的导入错误
def crawl_baike(keyword):
    crawler = WikiCrawler()
    return crawler.fetch(keyword)