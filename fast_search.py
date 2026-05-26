import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import imagehash

# ================= 配置区域 =================
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
HASH_THRESHOLD = 15 
# ============================================

def calculate_file_hash(file_path):
    try:
        with Image.open(file_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return file_path, imagehash.phash(img)
    except Exception:
        return None

def scan_directory(folder_path):
    file_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                file_paths.append(os.path.join(root, file))
    return file_paths

if __name__ == '__main__':
    print("=== 12600KF 专属高性能图片检索与管理工具 ===")
    
    target_img_path = input("1. 请拖入或输入【精选缩略图】的绝对路径: ").strip('"').strip("'")
    library_folder_path = input("2. 请拖入或输入【待查找的素材库】文件夹路径: ").strip('"').strip("'")
    
    if not os.path.exists(target_img_path) or not os.path.exists(library_folder_path):
        print("错误：路径不存在，请检查后重新运行！")
        input("\n按回车键退出...")
        exit()

    start_time = time.time()
    
    print("\n正在解析目标精选图...")
    target_res = calculate_file_hash(target_img_path)
    if target_res is None:
        print("无法解析目标图片！")
        input("\n按回车键退出...")
        exit()
    target_hash = target_res[1]

    print("正在扫描素材库目录结构...")
    all_files = scan_directory(library_folder_path)
    total_files = len(all_files)
    print(f"共找到 {total_files} 张待比对图片。")

    print(f"正在唤醒 12600KF 多核心进行暴走检索...")
    results = []
    
    # 16线程跑满你电脑大核小核，榨干算力
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = executor.map(calculate_file_hash, all_files)
        
        for idx, res in enumerate(futures):
            if res is not None:
                file_path, current_hash = res
                distance = target_hash - current_hash
                if distance <= HASH_THRESHOLD:
                    similarity = (1 - distance / 64) * 100
                    results.append((file_path, similarity))
            
            if (idx + 1) % 50 == 0 or (idx + 1) == total_files:
                print(f"进度: {idx + 1}/{total_files} 张图片已比对完成...", end='\r')

    results.sort(key=lambda x: x[1], reverse=True)
    print(f"\n\n⚡ 检索完毕！总耗时: {time.time() - start_time:.2f} 秒。")
    
    if not results:
        print("没有在素材库中找到相似的图片。")
        input("\n按回车键退出...")
        exit()

    print("\n" + "="*60)
    print("🔍 检索到最相似的原图如下（已按相似度排序）：")
    for i, (path, sim) in enumerate(results[:5]):
        print(f"[{i+1}] 相似度: {sim:.1f}% | 路径: {path}")
    print("="*60)

    try:
        choice = input("\n请输入你想操作的图片编号 (如 1) 进行后续管理 (直接回车退出): ")
        if choice.isdigit() and 0 < int(choice) <= len(results):
            selected_path = results[int(choice)-1][0]
            filename = os.path.basename(selected_path)
            
            print(f"\n已选中原图: {filename}")
            print("请选择操作： [1] 复制到别处  [2] 移动到别处  [3] 直接删除该原图  [Enter] 放弃")
            action = input("请输入操作数字: ").strip()
            
            if action == '1':
                dest_dir = input("请输入要复制到的目标文件夹路径: ").strip('"').strip("'")
                if os.path.exists(dest_dir):
                    shutil.copy(selected_path, dest_dir)
                    print(f"✅ 已成功复制到 {dest_dir}")
                else: print("目标路径不存在，操作取消。")
                    
            elif action == '2':
                dest_dir = input("请输入要移动到的目标文件夹路径: ").strip('"').strip("'")
                if os.path.exists(dest_dir):
                    shutil.move(selected_path, dest_dir)
                    print(f"✅ 已成功移动到 {dest_dir}")
                else: print("目标路径不存在，操作取消。")
                    
            elif action == '3':
                confirm = input(f"⚠️ 确认要在硬盘上彻底删除 {filename} 吗？(y/n): ")
                if confirm.lower() == 'y':
                    os.remove(selected_path)
                    print("✅ 文件已从硬盘永久删除！")
        else:
            print("已安全退出。")
    except Exception as e:
        print(f"文件操作失败: {e}")
        
    input("\n操作结束，按回车键关闭窗口...")
