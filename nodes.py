import os
import random
import json
from pathlib import Path
import torch
from PIL import Image
import numpy as np

class StringSaveNode:
    """字符串保存节点
    
    用于接收任何字符串，在节点下方展示内容，并将其保存到txt文档中。
    支持选择保存模式：单次保存或汇总保存为wildcards格式。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"multiline": True, "default": "", "placeholder": "在此输入或连接字符串..."}),
                "save_path": ("STRING", {"default": "E:/Project1/Wildcards-Generator/prompts", "vfile": {".": {"accept": ".", "save": True}}}),
                "file_name": ("STRING", {"default": "wildcards.txt"}),
                "save_mode": (["single_file", "wildcards_format"], {"default": "wildcards_format"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("文本",)
    FUNCTION = "save_string"
    OUTPUT_NODE = True
    CATEGORY = "🐱 CATS"
    
    def save_string(self, 文本, save_path, file_name, save_mode):
        """保存字符串到文件，并展示内容
        
        参数:
        - 文本: 要保存的字符串或复杂类型
        - save_path: 保存文件的目标路径
        - file_name: 保存的文件名
        - save_mode: 保存模式，single_file或wildcards_format
        
        返回:
        - 文本: 返回输入字符串，保持数据流
        """
        try:
            # 类型检查和转换
            input_type = type(文本).__name__
            
            # 处理不同类型的输入
            if isinstance(文本, str):
                # 纯字符串，直接使用
                string_text = 文本.strip()
                conversion_info = f"纯字符串类型，直接使用"
            elif isinstance(文本, dict):
                # 字典类型，尝试提取提示词字段
                conversion_info = f"字典类型，尝试提取提示词字段"
                # 常见的提示词字段名
                prompt_keys = ["output", "prompt", "text", "result", "content", "response"]
                for key in prompt_keys:
                    if key in 文本:
                        string_text = str(文本[key]).strip()
                        conversion_info += f"，提取字段: {key}"
                        break
                else:
                    # 没有找到匹配的字段，尝试将整个字典转换为字符串
                    string_text = str(文本).strip()
                    conversion_info += f"，未找到匹配字段，转换为字符串"
            elif isinstance(文本, (list, tuple)):
                # 列表或元组类型，处理第一个元素
                conversion_info = f"列表/元组类型，处理第一个元素"
                if 文本:
                    first_item = 文本[0]
                    if isinstance(first_item, str):
                        string_text = first_item.strip()
                        conversion_info += f"，第一个元素为字符串"
                    elif isinstance(first_item, dict):
                        # 处理第一个元素为字典的情况
                        prompt_keys = ["output", "prompt", "text", "result", "content", "response"]
                        for key in prompt_keys:
                            if key in first_item:
                                string_text = str(first_item[key]).strip()
                                conversion_info += f"，提取第一个元素的{key}字段"
                                break
                        else:
                            string_text = str(first_item).strip()
                            conversion_info += f"，未找到匹配字段，转换第一个元素为字符串"
                    else:
                        string_text = str(first_item).strip()
                        conversion_info += f"，转换第一个元素为字符串"
                else:
                    string_text = ""
                    conversion_info += f"，列表为空"
            else:
                # 其他类型，尝试转换为字符串
                string_text = str(文本).strip()
                conversion_info = f"{input_type}类型，转换为字符串"
            
            # 确保转换后的字符串不为空
            if not string_text:
                return {
                    "ui": {
                        "text": [
                            "转换后的字符串为空",
                            f"原始输入类型: {input_type}",
                            f"转换信息: {conversion_info}",
                            "请检查输入或连接的节点"
                        ]
                    },
                    "result": ("",)
                }
            
            # 确保保存路径存在
            Path(save_path).mkdir(parents=True, exist_ok=True)
            
            # 构建基础文件名（不含扩展名）
            base_name, _ = os.path.splitext(file_name)  # 忽略输入的扩展名
            ext = ".txt"  # 强制使用.txt扩展名
            
            file_path = ""
            
            if save_mode == "single_file":
                # 单文件模式：每次执行保存为新文件，自动添加累计数字
                counter = 0
                while True:
                    if counter == 0:
                        temp_file_path = os.path.join(save_path, f"{base_name}{ext}")
                    else:
                        temp_file_path = os.path.join(save_path, f"{base_name}{counter}{ext}")
                    
                    if not os.path.exists(temp_file_path):
                        file_path = temp_file_path
                        break
                    counter += 1
                
                # 保存文件
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(string_text + "\n")
                
                message = f"字符串已保存到新文件"
                saved = True
            else:
                # wildcards_format模式：每行一组提示词，每次执行的文本为一组
                file_path = os.path.join(save_path, f"{base_name}{ext}")
                
                # 直接追加到文件，每行一组提示词
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(string_text + "\n")
                
                message = f"提示词组已添加到wildcards文件"
                saved = True
            
            # 准备UI输出，确保文本显示在节点下方
            ui_output = {
                "text": [
                    string_text,
                    "",
                    f"原始输入类型: {input_type}",
                    f"转换信息: {conversion_info}",
                    message,
                    f"文件: {file_path}",
                    f"大小: {os.path.getsize(file_path)} 字节"
                ]
            }
            
            return {
                "ui": ui_output,
                "result": (文本,)
            }
        except Exception as e:
            error_msg = f"操作失败: {str(e)}"
            return {
                "ui": {
                    "text": [
                        error_msg,
                        f"错误: {type(e).__name__}",
                        f"输入类型: {type(文本).__name__}",
                        f"输入内容: {str(文本)[:100]}..."
                    ]
                },
                "result": ("",)
            }

class RandomWildcardNode:
    """随机提示词抽取节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "wildcard_file": ("STRING", {"default": "", "vfile": {".": {"accept": ".txt"}}}),
                "num_prompts": ("INT", {"default": 1, "min": 1, "max": 100}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "fixed_prompt": ("STRING", {"default": "", "multiline": True, "placeholder": "在此输入固定提示词..."}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("random_prompt",)
    FUNCTION = "get_random_prompt"
    CATEGORY = "🐱 CATS"
    
    def get_random_prompt(self, wildcard_file, num_prompts, seed, fixed_prompt=""):
        """从wildcard文件中随机抽取提示词，并与固定提示词合并
        
        参数:
        - wildcard_file: wildcards文件路径
        - num_prompts: 要抽取的提示词数量
        - seed: 随机种子，0表示使用随机种子
        - fixed_prompt: 固定提示词，用于添加前缀
        
        返回:
        - 合并后的提示词字符串
        """
        try:
            # 验证文件路径
            if not wildcard_file or not os.path.exists(wildcard_file):
                return (f"错误: 文件不存在或路径为空: {wildcard_file}",)
            
            if not os.path.isfile(wildcard_file):
                return (f"错误: 不是有效的文件: {wildcard_file}",)
            
            # 设置随机种子
            if seed > 0:
                random.seed(seed)
            else:
                # 使用基于时间的随机种子
                import time
                random.seed(time.time())
            
            # 读取wildcard文件
            with open(wildcard_file, "r", encoding="utf-8") as f:
                prompts = [line.strip() for line in f if line.strip()]
            
            if not prompts:
                return (f"警告: 文件中没有有效的提示词: {wildcard_file}",)
            
            # 随机抽取提示词
            random_prompts = random.choices(prompts, k=num_prompts)
            
            # 合并固定提示词和随机提示词
            if fixed_prompt:
                # 去除固定提示词两端的空格
                fixed_prompt = fixed_prompt.strip()
                if fixed_prompt:
                    # 如果有多个随机提示词，每个都添加固定前缀
                    if num_prompts > 1:
                        combined_prompts = []
                        for prompt in random_prompts:
                            combined_prompts.append(f"{fixed_prompt}, {prompt}")
                        result = "\n".join(combined_prompts)
                    else:
                        # 单个随机提示词，直接合并
                        result = f"{fixed_prompt}, {random_prompts[0]}"
                else:
                    # 固定提示词为空，直接返回随机提示词
                    result = "\n".join(random_prompts)
            else:
                # 没有固定提示词，直接返回随机提示词
                result = "\n".join(random_prompts)
            
            return (result,)
        except FileNotFoundError:
            return (f"错误: 文件未找到: {wildcard_file}",)
        except PermissionError:
            return (f"错误: 没有权限读取文件: {wildcard_file}",)
        except Exception as e:
            error_msg = f"错误: 读取文件失败: {str(e)}"
            print(error_msg)
            return (error_msg,)


class SequentialWildcardNode:
    """按顺序提取提示词节点
    
    从wildcards文件中按顺序提取提示词，每次执行切换到下一个提示词。
    支持添加固定前缀。
    """
    
    # --- 节点状态持久化 ---
    current_indices = {}  # 存储每个文件的当前索引
    prompts_cache = {}    # 缓存文件内容，避免重复读取
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "wildcard_file": ("STRING", {"default": "", "vfile": {".": {"accept": ".txt"}}}),
                "fixed_prompt": ("STRING", {"default": "", "multiline": True, "placeholder": "在此输入固定提示词..."}),
                "reset": ("BOOLEAN", {"default": False}),  # 重置到第一个提示词
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("prompt", "current_index", "file_info")
    FUNCTION = "get_next_prompt"
    CATEGORY = "🐱 CATS"
    
    def get_next_prompt(self, wildcard_file, fixed_prompt="", reset=False):
        """从wildcard文件中按顺序提取下一个提示词
        
        参数:
        - wildcard_file: wildcards文件路径
        - fixed_prompt: 固定提示词，用于添加前缀
        - reset: 是否重置到第一个提示词
        
        返回:
        - prompt: 合并后的提示词
        - current_index: 当前提取的索引
        - file_info: 文件信息
        """
        try:
            # 验证文件路径
            if not wildcard_file or not os.path.exists(wildcard_file):
                return (f"错误: 文件不存在或路径为空: {wildcard_file}", 0, "")
            
            if not os.path.isfile(wildcard_file):
                return (f"错误: 不是有效的文件: {wildcard_file}", 0, "")
            
            # 获取文件唯一标识
            file_key = os.path.abspath(wildcard_file)
            
            # 读取文件内容（如果不在缓存中或需要重置）
            if file_key not in self.prompts_cache or reset:
                with open(wildcard_file, "r", encoding="utf-8") as f:
                    self.prompts_cache[file_key] = [line.strip() for line in f if line.strip()]
                
                # 重置索引
                self.current_indices[file_key] = -1
            
            # 获取当前文件的提示词列表
            prompts = self.prompts_cache[file_key]
            
            if not prompts:
                return (f"警告: 文件中没有有效的提示词: {wildcard_file}", 0, "")
            
            # 递增索引，循环回到开头
            self.current_indices[file_key] = (self.current_indices[file_key] + 1) % len(prompts)
            current_index = self.current_indices[file_key]
            
            # 获取当前提示词
            current_prompt = prompts[current_index]
            
            # 合并固定提示词和当前提示词
            if fixed_prompt:
                # 去除固定提示词两端的空格
                fixed_prompt = fixed_prompt.strip()
                if fixed_prompt:
                    result = f"{fixed_prompt}, {current_prompt}"
                else:
                    result = current_prompt
            else:
                result = current_prompt
            
            # 准备文件信息
            file_info = f"文件: {os.path.basename(wildcard_file)} | 总数: {len(prompts)} | 当前: {current_index + 1}"
            
            return (result, current_index, file_info)
        except FileNotFoundError:
            return (f"错误: 文件未找到: {wildcard_file}", 0, "")
        except PermissionError:
            return (f"错误: 没有权限读取文件: {wildcard_file}", 0, "")
        except Exception as e:
            error_msg = f"错误: 读取文件失败: {str(e)}"
            print(error_msg)
            return (error_msg, 0, "")

def pil_to_tensor(image):
    img_np = np.array(image).astype(np.float32) / 255.0
    return torch.from_numpy(img_np).unsqueeze(0)

class ImageSequenceLoader:
    # --- 节点状态持久化 ---
    image_list = []
    current_index = -1
    # 存储标准化的路径，确保比较的稳定性
    _last_folder_path_standardized = "" 
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "input/sequence_folder", "multiline": False}),
                "trigger": ("INT", {"default": 0, "hidden": True}), 
            },
            "optional": {
                "filename_display": ("STRING", {"forceInput": True, "widget": "text", "default": "Waiting...", "hidden": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("IMAGE_OUT", "FILENAME")
    FUNCTION = "execute"
    CATEGORY = "🐱 CATS"
    
    def execute(self, folder_path, trigger, filename_display=None):
        
        # 🚨 修正点 1: 路径标准化
        # 获取绝对路径，并将 Windows 反斜杠 (\) 转换为稳定的正斜杠 (/)
        try:
            standardized_path = os.path.abspath(folder_path).replace("\\", "/")
        except Exception:
            standardized_path = folder_path.replace("\\", "/")
        
        # 1. 检查路径变化 / 初始化
        # 只有当标准化路径与上次存储的路径不一致时，才重新加载文件列表
        if standardized_path != self._last_folder_path_standardized:
            self._last_folder_path_standardized = standardized_path # 更新存储的路径
            
            valid_extensions = ['.png', '.jpg', '.jpeg', '.webp']
            
            try:
                # 使用标准化的路径进行文件操作
                all_files = os.listdir(standardized_path)
                image_files_with_path = []

                for f in all_files:
                    full_path = os.path.join(standardized_path, f)
                    if os.path.isfile(full_path) and f.lower().endswith(tuple(valid_extensions)):
                        # 按修改时间排序
                        image_files_with_path.append((f, os.path.getmtime(full_path))) 

                # 按修改时间排序
                image_files_with_path.sort(key=lambda x: x[1])
                self.image_list = [f[0] for f in image_files_with_path]

                print(f"ImageSequenceLoader: Loaded {len(self.image_list)} images from: {standardized_path}. Sorted by modification time.")

            except FileNotFoundError:
                 raise Exception(f"ImageSequenceLoader Error: Folder not found or inaccessible: {standardized_path}")

            # 🚨 修正点 2: 只有在路径发生变化时重置为 -1
            self.current_index = -1 
        
        # 2. 检查列表是否为空
        if not self.image_list:
            raise Exception("ImageSequenceLoader Error: Folder is empty or contains no valid images.")

        # 3. 自动切换到下一张图片（每次执行都 +1）
        # 如果路径稳定，current_index 将递增；如果路径变化，current_index 从 -1 变为 0。
        self.current_index = (self.current_index + 1) % len(self.image_list)
        
        # 4. 加载图片
        filename = self.image_list[self.current_index]
        full_path = os.path.join(standardized_path, filename) # 使用标准化路径加载

        try:
            image = Image.open(full_path).convert("RGB")
            image_tensor = pil_to_tensor(image)
        except Exception as e:
            print(f"ImageSequenceLoader Error: loading image {full_path}: {e}")
            raise

        # 5. 返回结果
        return (image_tensor, filename)
