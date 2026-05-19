import os
import sys
import subprocess
import glob

def main():
    # 1. 检查命令行参数
    if len(sys.argv) != 3:
        print("用法: python run_case_opt.py <Case文件夹名> <on|off>")
        print("示例: python run_case_opt.py case2 on")
        sys.exit(1)

    case_folder_name = sys.argv[1]
    sim_chassis_flag = sys.argv[2].lower()

    if sim_chassis_flag not in {"on", "off"}:
        print("❌ 错误: 第二个参数必须是 on 或 off")
        sys.exit(1)

    sim_chassis_module = "SIM_CHASSIS_ON" if sim_chassis_flag == "on" else "SIM_CHASSIS_OFF"
    
    # 2. 定义基础路径
    #base_path = "/home/xiaosheng/Documents/场景库/序列场景"
    #base_path = "/home/xiaosheng/Documents/场景库/对比库"
    base_path = "/home/xiaosheng/Documents/场景库/脑补场景"
    #base_path = "/home/xiaosheng/Documents/场景库/大场景集"
    #base_path = "/home/xiaosheng/Documents/场景库/低速跑行"
    #base_path = "/home/xiaosheng/Documents/场景库/博弈安全"
    #base_path = "/home/xiaosheng/Documents/场景库/开放博弈"
    #base_path = "/home/xiaosheng/Documents/场景库/开放博弈2"
    #base_path = "/home/xiaosheng/Documents/场景库/unexpect_speed_limit"
    #base_path = "/home/xiaosheng/Documents/场景库/BugAnalyzed"
    target_dir = os.path.join(base_path, case_folder_name)

    # 检查文件夹是否存在
    if not os.path.exists(target_dir):
        print(f"❌ 错误: 找不到文件夹 '{target_dir}'")
        sys.exit(1)

    # 3. 查找有效文件 (优先 .desc, 其次 .mcap, 最后 .record)
    input_file = None
    use_worldsim = False

    # --- 第一步：尝试查找 .desc ---
    all_descs = glob.glob(os.path.join(target_dir, "*.desc"))
    valid_descs = [f for f in all_descs if not f.endswith("sim.desc")]

    if valid_descs:
        input_file = valid_descs[0]
        use_worldsim = True
        if len(valid_descs) > 1:
            print(f"⚠️  警告: 发现多个有效 .desc 文件，默认使用第一个: {os.path.basename(input_file)}")
    else:
        # --- 第二步：如果没有 .desc，尝试查找 .mcap ---
        all_mcaps = glob.glob(os.path.join(target_dir, "*.mcap"))
        # 过滤：排除以 sim.mcap 结尾的文件
        valid_mcaps = [f for f in all_mcaps if not f.endswith("sim.mcap")]

        if valid_mcaps:
            input_file = valid_mcaps[0]
            if len(valid_mcaps) > 1:
                print(f"⚠️  警告: 发现多个有效 .mcap 文件，默认使用第一个: {os.path.basename(input_file)}")
        else:
            # --- 第三步：如果没有 .mcap，尝试查找 .record ---
            print("ℹ️  未找到有效 .desc/.mcap 文件，正在查找 .record 文件...")
            all_records = glob.glob(os.path.join(target_dir, "*.record"))
            # 同样过滤掉以 sim.record 结尾的文件（如果存在这种命名习惯）
            valid_records = [f for f in all_records if not f.endswith("sim.record")]

            if valid_records:
                input_file = valid_records[0]
                if len(valid_records) > 1:
                    print(f"⚠️  警告: 发现多个有效 .record 文件，默认使用第一个: {os.path.basename(input_file)}")
            else:
                # --- 第四步：如果三者都没有，报错退出 ---
                print(f"❌ 错误: 在 '{target_dir}' 中未找到有效的 .desc、.mcap 或 .record 文件")
                sys.exit(1)

    # 4. 解析 valid_range.txt 获取 srt
    range_file = os.path.join(target_dir, "valid_range.txt")
    srt_value = "0" # 默认值

    if os.path.exists(range_file):
        with open(range_file, 'r', encoding='utf-8') as f:
            for line in f:
                # 查找包含 "srt :" 的行
                if "srt" in line and ":" in line:
                    try:
                        # 分割字符串并提取数字部分
                        parts = line.split(":")
                        if len(parts) >= 2:
                            srt_value = parts[1].strip()
                            break
                    except Exception as e:
                        print(f"⚠️  解析 valid_range.txt 出错: {e}")
    else:
        print(f"⚠️  警告: 未找到 valid_range.txt，使用默认 srt: 0")

    # 5. 构建并执行命令
    script_path = "simulation2/python_script/simulation2.py"
    if use_worldsim:
        modules = f"PREDICTION,PLANNING,{sim_chassis_module},PERFECT_CONTROL,OFFLINE_ROUTING,ARTIFICIAL_OBSTACLE"
        final_command = [
            "python", script_path,
            "-i", input_file,
            "-m", modules,
            "-t", "worldsim"
        ]
    else:
        #modules = f"PREDICTION,PLANNING,PERFECT_CONTROL,{sim_chassis_module},OFFLINE_ROUTING,ARTIFICIAL_OBSTACLE"
        modules = f"PREDICTION,PLANNING,PERFECT_CONTROL,{sim_chassis_module},OFFLINE_ROUTING"
        final_command = [
            "python", script_path,
            "-i", input_file,
            "-m", modules,
            "-srt", srt_value
        ]

    print(f"🚀 准备执行仿真:")
    print(f"   输入文件: {input_file}")
    print(f"   回归模式: {'worldsim' if use_worldsim else 'logsim'}")
    print(f"   SIM_CHASSIS 模块: {sim_chassis_module}")
    if not use_worldsim:
        print(f"   SRT 数值: {srt_value}")
    print("-" * 30)
    
    # 执行命令
    try:
        subprocess.run(final_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 仿真运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
