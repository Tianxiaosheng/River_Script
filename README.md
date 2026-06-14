# ROVER_SCRIPT

ROVER_SCRIPT 用于存放 Rover 相关的日常工具脚本。

## open_latest_log.sh

打开指定目录下最新修改的、以指定后缀结尾的文件。默认后缀配置在脚本内：

```bash
DEFAULT_SUFFIX=".log"
```

脚本会直接使用 `vim` 打开匹配文件。
执行过程中会在终端打印查找目录、匹配后缀、候选数量、候选文件和最终打开的文件，便于排查选中文件是否符合预期。

### 用法

```bash
./open_latest_log.sh [-e suffix] DIR
```

### 示例

打开目录下最新的 `.log` 文件：

```bash
./open_latest_log.sh /path/to/log_dir
```

打开目录下最新的 `.txt` 文件：

```bash
./open_latest_log.sh -e .txt /path/to/log_dir
```

### 参数

- `DIR`: 要查找文件的目录，只查找该目录当前层级下的普通文件。
- `-e suffix`: 指定文件名结尾，例如 `.txt`、`.record`。不传时使用脚本内的 `DEFAULT_SUFFIX`。
- `-h`: 显示帮助信息。

## run_case_opt.py

根据 case 目录自动选择仿真输入文件，并启动 `simulation2/python_script/simulation2.py`。

当前脚本内配置的 case 根目录为：

```python
base_path = "/home/xiaosheng/Documents/场景库/BugAnalyzed"
```

脚本会在 `base_path/<Case文件夹名>` 下查找输入文件，优先级如下：

1. 有效 `.desc` 文件，排除 `sim.desc` 结尾的文件；使用 `worldsim` 模式。
2. 有效 `.mcap` 文件，排除 `sim.mcap` 结尾的文件；使用 `logsim` 模式。
3. 有效 `.record` 文件，排除 `sim.record` 结尾的文件；使用 `logsim` 模式。

如果使用 `logsim` 模式，脚本还会读取 case 目录下的 `valid_range.txt`，查找包含 `srt:` 的行作为 `-srt` 参数；如果文件不存在或未解析到，默认使用 `0`。

### 用法

```bash
python run_case_opt.py <Case文件夹名> <on|off>
```

### 示例

开启 `SIM_CHASSIS`：

```bash
python run_case_opt.py case2 on
```

关闭 `SIM_CHASSIS`：

```bash
python run_case_opt.py case2 off
```

### 参数

- `<Case文件夹名>`: `base_path` 下的 case 子目录名。
- `<on|off>`: 控制仿真模块中使用 `SIM_CHASSIS_ON` 或 `SIM_CHASSIS_OFF`。

### 注意

- 运行 `run_case_opt.py` 时，需要在能够访问 `simulation2/python_script/simulation2.py` 的工作目录下执行。
- 如果同一目录下存在多个同类型输入文件，脚本会使用找到的第一个文件，并输出警告。
