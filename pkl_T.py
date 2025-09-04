import pickle
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import argparse
import sys


def find_all_path_fields(samples):
    """查找所有可能的路径字段"""
    path_fields = set()

    # 检查多个样本以确保找到所有可能的路径字段
    for sample in samples[:10]:  # 检查前10个样本
        for key in sample.keys():
            # 检查字段名是否包含"path"或结尾为"_path"
            if 'path' in key.lower() or key.endswith('_path'):
                path_fields.add(key)

    return list(path_fields)


def replace_nuscenes_path_prefix(pkl_path, output_path=None):
    """替换nuscenes-info.pkl中的所有路径前缀"""
    if not os.path.exists(pkl_path):
        print(f"错误：未找到文件 {pkl_path}")
        return

    try:
        # 加载pkl文件
        with open(pkl_path, 'rb') as f:
            info_data = pickle.load(f)

        print(f"正在处理文件: {os.path.basename(pkl_path)}")
        print("=" * 50)

        # 确定样本数据的存储键
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
            print("未找到样本数据字段，无法处理")
            print(f"文件中的键: {list(info_data.keys())}")
            return

        # 查找所有可能的路径字段
        path_fields = find_all_path_fields(samples)

        if not path_fields:
            print("未找到任何路径字段，无需处理")
            return

        print(f"找到的路径字段: {', '.join(path_fields)}")

        # 替换路径前缀
        old_prefix = "./data/nuscenes/"
        new_prefix = "/mnt/sda/xgh-nuscenes/"

        count = 0
        for sample in samples:
            for field in path_fields:
                if field in sample and isinstance(sample[field], str) and sample[field].strip():
                    original_value = sample[field]

                    # 只替换以"./data/nuscenes/"开头的路径
                    if original_value.startswith(old_prefix):
                        sample[field] = original_value.replace(old_prefix, new_prefix, 1)
                        count += 1
                        print(f"替换: {original_value} -> {sample[field]}")

        print(f"成功替换了 {count} 个路径前缀")
        print(f"从 '{old_prefix}' 替换为 '{new_prefix}'")

        # 保存修改后的文件
        if output_path is None:
            # 在原文件名后添加 "_modified"
            base_name = os.path.splitext(pkl_path)[0]
            output_path = base_name + "_modified.pkl"

        with open(output_path, 'wb') as f:
            pickle.dump(info_data, f)

        print(f"已保存修改后的文件到: {output_path}")

    except Exception as e:
        print(f"处理出错：{str(e)}")
        import traceback
        traceback.print_exc()


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

        # 查找所有可能的路径字段
        path_fields = find_all_path_fields(samples)

        if not path_fields:
            print("所有检查的样本中均未找到路径字段")
            return

        print(f"\n所有发现的路径字段: {', '.join(path_fields)}")

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
    parser = argparse.ArgumentParser(description="处理NuScenes PKL文件中的路径")
    parser.add_argument("file_path", nargs="?", help="PKL文件路径")
    parser.add_argument("--replace", action="store_true", help="执行路径替换操作")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    if args.file_path:
        file_path = args.file_path
        if not os.path.exists(file_path):
            print(f"错误：未找到文件 {file_path}")
            return

        if args.replace:
            replace_nuscenes_path_prefix(file_path, args.output)
        else:
            check_nuscenes_path_prefix(file_path)
    else:
        # 询问用户是否要使用文件对话框
        use_dialog = input("是否使用文件对话框选择文件？(y/n): ").lower().strip()

        if use_dialog == 'y':
            file_path = select_file_dialog()
            if file_path:
                action = input("是否执行路径替换操作？(y/n): ").lower().strip()
                if action == 'y':
                    output_path = input("请输入输出文件路径（直接回车使用默认名称）: ").strip()
                    output_path = output_path if output_path else None
                    replace_nuscenes_path_prefix(file_path, output_path)
                else:
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

            action = input("是否执行路径替换操作？(y/n): ").lower().strip()

            for file in selected_files:
                print("\n" + "=" * 60)
                if action == 'y':
                    output_path = input(f"请输入 {file} 的输出文件路径（直接回车使用默认名称）: ").strip()
                    output_path = output_path if output_path else None
                    replace_nuscenes_path_prefix(file, output_path)
                else:
                    check_nuscenes_path_prefix(file)


if __name__ == "__main__":
    main()