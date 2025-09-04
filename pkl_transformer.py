import pickle
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import argparse
import sys


def check_nuscenes_path_prefix(pkl_path):
    """检查nuscenes-info.pkl中的路径前缀"""
    if not os.path.exists(pkl_path):
        print(f"错误：未找到文件 {pkl_path}")
        return

    try:
        # 加载pkl文件
        with open(pkl_path, 'rb') as f:
            info_data = pickle.load(f)

        print(f"正在分析文件: {os.path.basename(pkl_path)}")
        print("=" * 50)

        # 确定样本数据的存储键（更全面的键检查）
        samples = None
        possible_keys = ['samples', 'data_list', 'infos', 'data']

        for key in possible_keys:
            if key in info_data:
                samples = info_data[key]
                print(f"找到数据键: {key}")
                break

        if samples is None:
            # 尝试直接获取列表类型的数据
            for key, value in info_data.items():
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    samples = value
                    print(f"找到列表数据键: {key}")
                    break

        if samples is None:
            print("未找到样本数据字段，请检查pkl文件结构")
            print(f"文件中的键: {list(info_data.keys())}")
            return

        # 检查多个样本（最多5个）以确保找到所有可能的路径字段
        path_fields = set()
        sample_count = min(5, len(samples))

        print(f"\n检查前 {sample_count} 个样本中的路径字段:")
        print("-" * 30)

        for i in range(sample_count):
            sample = samples[i]
            current_fields = [key for key in sample.keys() if key.endswith('_path') or 'path' in key.lower()]
            path_fields.update(current_fields)

            if current_fields:
                print(f"样本 {i}: 找到路径字段 - {', '.join(current_fields)}")
            else:
                print(f"样本 {i}: 未找到路径字段")

        if not path_fields:
            print("所有检查的样本中均未找到路径字段")
            return

        print(f"\n所有发现的路径字段: {', '.join(current_fields)}")

        # 分析路径前缀
        print("\n路径前缀分析:")
        print("-" * 30)

        for field in path_fields:
            # 收集所有样本中该字段的值
            paths = []
            for i in range(min(20, len(samples))):  # 检查更多样本以获得更准确的前缀
                if field in samples[i]:
                    path = samples[i][field]
                    if isinstance(path, str) and path.strip():
                        paths.append(path)

            if not paths:
                print(f"字段 '{field}' 在所有检查的样本中均为空或不存在")
                continue
            # 查找共同前缀
            common_prefix = os.path.commonprefix(paths)
            if common_prefix:
                print(f"{field}: 共同前缀 -> {common_prefix}")

                # 显示一些示例路径
                print(f"  示例: {paths[0]}")
                if len(paths) > 1:
                    print(f"         {paths[1]}")
                if len(paths) > 2:
                    print(f"         ...")
            else:
                print(f"{field}: 未找到共同前缀")

        print("\n提示: 路径前缀通常是上述路径中相同的目录结构部分")

    except Exception as e:
        print(f"处理出错：{str(e)}")
        import traceback
        traceback.print_exc()


def select_file_dialog():
    """通过文件对话框选择文件"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    file_path = filedialog.askopenfilename(
        title="选择NuScenes PKL文件",
        filetypes=[("PKL files", "*.pkl"), ("All files", "*.*")]
    )

    return file_path


def main():
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 使用命令行指定的文件路径
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"错误：未找到文件 {file_path}")
            return
        check_nuscenes_path_prefix(file_path)
    else:
        # 询问用户是否要使用文件对话框
        use_dialog = input("是否使用文件对话框选择文件？(y/n): ").lower().strip()

        if use_dialog == 'y':
            file_path = select_file_dialog()
            if file_path:
                check_nuscenes_path_prefix(file_path)
            else:
                print("未选择文件")
        else:
            # 使用原始的逻辑
            pkl_files = [f for f in os.listdir('.') if f.endswith('.pkl')]

            if not pkl_files:
                print("当前目录下未找到pkl文件")
                return

            print("找到以下pkl文件:")
            for i, f in enumerate(pkl_files):
                print(f"{i + 1}. {f}")

            try:
                choice = int(input("\n请选择要分析的文件编号 (输入0分析所有文件): "))
                if choice == 0:
                    selected_files = pkl_files
                else:
                    selected_files = [pkl_files[choice - 1]]
            except (ValueError, IndexError):
                print("输入无效，将分析所有文件")
                selected_files = pkl_files

            for file in selected_files:
                print("\n" + "=" * 60)
                check_nuscenes_path_prefix(file)


if __name__ == "__main__":
    main()