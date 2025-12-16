# 导入所有节点类
from .nodes import StringSaveNode, RandomWildcardNode, ImageSequenceLoader

# 配置web目录
WEB_DIRECTORY = "./web"

# 注册所有节点
NODE_CLASS_MAPPINGS = {
    "StringSaveNode": StringSaveNode,
    "RandomWildcardNode": RandomWildcardNode,
    "ImageSequenceLoader": ImageSequenceLoader,
}

# 定义友好的显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "StringSaveNode": "🔤 字符串保存节点",
    "RandomWildcardNode": "🎲 随机抽取提示词",
    "ImageSequenceLoader": "🖼️ 图像序列加载器"
}

print("Loaded 🐱 CATS (Creative Assistant Tools Suite) nodes.")
