# 起步操作指南（先运行 G0–G2）

本指南的 shell 命令按 Linux / WSL2 的 Bash 写。Windows 原生 PowerShell 可执行最前面的 Python 检查，但后续多行反斜杠命令请在 Bash 中运行。GPU 型号未知，不能保证某一套历史 CUDA 依赖适配你的设备。

**已完成**：实验方案、辅助工具与14项合成单元测试。**未完成**：真实数据下载、CUDA训练、Open-CD端到端验证、扰动推理适配、创新模型与最终论文实验。不要把这个仓库误认成一键训练完整论文的成品。

## 1. 克隆和轻量检查

```bash
git clone https://github.com/w504715799-eng/vit.git
cd vit
python -m pip install -r requirements-tools.txt
python -m unittest discover -s tests -v
python tools/preflight.py doctor --out reports/environment.json
```

预期：14项测试全部通过；环境报告记录 Python、GPU/驱动、PyTorch 与主要依赖。`doctor` 返回0只表示报告生成成功，不表示GPU或G1过关。没有CUDA可以继续文献/数据检查，但不要启动正式训练。

先复制 `experiments/GATE_TEMPLATE.md` 为 `experiments/G0.md`，完成文献差异、设备、预算和投稿认定记录。模板不是自动验收器。

## 2. 获取并锁定上游

```bash
mkdir -p third_party
git clone https://github.com/likyoo/open-cd.git third_party/open-cd
git -C third_party/open-cd checkout 790a1972b538baaaffd4c3022a4d9afaa3f861e5
git -C third_party/open-cd rev-parse HEAD
```

该 SHA 是制定计划时读取到的 main 提交，已写入 `configs/upstream.json`。后续升级上游应另起实验轮次，不在同一比较表里混用版本。若网络/权限导致下载失败，停止该步骤并记录，不使用来源不明的整合包。

## 3. 安装训练环境：必须先确认硬件

建议单独建研究环境，不污染本机业务环境。下面是一套**历史兼容候选**，用于具备对应CUDA支持的设备；未在本会话实际安装/训练验证。较新GPU架构不能盲目使用旧版PyTorch；先通过官方安装选择器确认设备支持，再与MMCV可用wheel/源码编译条件一起选择。

```bash
conda create -n mr_cd python=3.10 -y
conda activate mr_cd
python -m pip install --upgrade pip
python -m pip install "numpy<2" "Pillow>=10,<13"
python -m pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cu118
python -m pip install "mmengine>=0.8,<1.0"
python -m pip install --only-binary=mmcv mmcv==2.1.0 -f https://download.openmmlab.com/mmcv/dist/cu118/torch2.1.0/index.html
python -m pip install mmsegmentation==1.2.2 mmdet==3.3.0 mmpretrain==1.2.0
python -m pip install -v -e third_party/open-cd
python -m pip check
python -c "import torch,mmcv,mmseg,mmdet,opencd; from mmcv.ops import nms; print(torch.__version__,torch.cuda.is_available(),mmcv.__version__)"
python tools/preflight.py doctor --out reports/environment.json
python -m pip freeze > reports/environment-lock.txt
```

`--only-binary=mmcv` 用于在没有匹配wheel时明确失败，避免无意进入漫长源码编译。历史PyTorch2.1.2和torchvision0.16.2的配对来自PyTorch官方历史版本页；wheel可用性和GPU兼容性必须在实际机器确认。

Open-CD当前版本检查要求 `mmcv<2.2.0`、`mmsegmentation<1.3.0`，不能机械安装全部“最新版”。不要同时装mmcv和mmcv-lite。导入成功不等于CUDA算子可执行，100步训练检查仍必需。

参考：[PyTorch历史版本](https://pytorch.org/get-started/previous-versions/)、[MMCV安装](https://mmcv.readthedocs.io/en/latest/get_started/installation.html)、[Open-CD依赖约束](https://github.com/likyoo/open-cd/blob/790a1972b538baaaffd4c3022a4d9afaa3f861e5/opencd/__init__.py)。两次明确修复后仍不兼容，按G1暂停/切换官方BIT实现，不用随机升级依赖碰碰运气。

## 4. 数据下载与组织

LEVIR-CD作者入口：https://justchenhao.github.io/LEVIR/ 。S2Looking作者入口：https://github.com/S2Looking/Dataset 。使用原始LEVIR-CD，不混用LEVIR-CD+。保留官方下载包、下载日期、hash与原始划分说明；不要把原图提交到Git。

将数据整理为：

```text
data/LEVIR-CD/
  train/A/       train/B/       train/label/
  val/A/         val/B/         val/label/
  test/A/        test/B/        test/label/
```

三目录同一对图像使用同名stem。源标签通常以白色表示变化，工具支持一致的0/1或0/255编码；框架输入应按上游loader的转换规则核验。S2Looking如为分开的变化标注，先核对作者语义，再转换并保留转换记录。

```bash
python tools/preflight.py audit --root data/LEVIR-CD --out reports/levir_audit.json
```

预期：结构检查通过，文件配对完整，无跨split重复图像对，所有warning人工解释。工具**不能**证明官方划分来源、近重复、空间重叠、标注语义和许可均正确；这些仍是G1人工检查项。不能因脚本退出0就直接记G1 PASS。

## 5. 检查配置，然后100步冒烟测试

以下命令都在本仓库根目录执行。`configs/bit_levir.py`继承锁定上游的BIT256/40k配置，仅显式覆盖数据根目录及seed。

```bash
python -c "from mmengine.config import Config; c=Config.fromfile('configs/bit_levir.py'); print(c.pretty_text)" > reports/resolved_bit_config.txt
python third_party/open-cd/tools/train.py configs/bit_levir.py --work-dir work_dirs/bit_smoke --cfg-options train_cfg.max_iters=100 train_cfg.val_interval=100 default_hooks.checkpoint.interval=100
```

检查：加载样本数/标签正确、loss有限、梯度可计算、预测不是永远全背景、显存无异常增长。100步只查流程，不用它判断准确率。随后按G1完成8–16个固定有变化训练裁剪的过拟合测试：复制一份独立配置、关闭随机增强、限定这些训练样本；不要修改正式数据划分。

batch=8若溢出，先记录硬件。降batch、梯度累积、AMP都必须在正式比较前统一设置；梯度累积不保证BatchNorm行为与真实大batch一致，不得直接宣称等价复现官方结果。

## 6. 正式基线（只有G0/G1过关后才运行）

```bash
python third_party/open-cd/tools/train.py configs/bit_levir.py --work-dir work_dirs/bit_levir_s17
```

训练使用train、选模使用val，默认40k iteration。记录源码SHA、预训练来源、最终展开配置、数据清单hash、GPU时间。模型输出写入`work_dirs/`，不提交权重。

先查看验证日志。需要复核验证集时，显式将test命令的三个路径改为val，避免开发期误看test：

```bash
CKPT="$(find work_dirs/bit_levir_s17 -maxdepth 1 -name 'best_mIoU*.pth' -print -quit)"
test -n "$CKPT" || { echo "Missing validation-selected checkpoint"; exit 1; }
python third_party/open-cd/tools/test.py configs/bit_levir.py "$CKPT" --cfg-options test_dataloader.dataset.data_prefix.img_path_from=val/A test_dataloader.dataset.data_prefix.img_path_to=val/B test_dataloader.dataset.data_prefix.seg_map_path=val/label
```

只读变化类这一行的F1，不把mFscore类平均值写成变化F1。不要照抄上游示例中的`latest.pth`作为最优checkpoint。

Changer官方入口是`configs/changer/changer_ex_r18_512x512_40k_levircd.py`。它的512裁剪结果与本项目BIT256不能直接视为同预算机制对照；G2中先明确官方复现版和统一设置版的区别，再建立版本化配置。

## 7. G3之后的代码工作清单

当前已经提供的`protocol_utils.py`是可测试的纯NumPy基础函数，不会自动运行Open-CD推理。

进入G3前需要接入：B-only扰动数据变换、共同mask的模型输出评价、逐原图TP/FP/FN/TN导出、验证集敏感性曲线。进入G4才实现相关性/可靠性/保留差异分支和对照配置。G5补齐消融，G6接S2Looking，G7接聚类bootstrap，G8冻结后才运行最终test。每个新模块先有合成测试，再在真实数据检查。

实现顺序、接口约束和验收标准见`PROTOCOL.md`与`EXPERIMENT_PLAN.md`。未实现的模块没有伪造可运行命令。

## 8. 实验记录与提交

```bash
git status --short
git diff --check
git diff --cached
```

每次只加入明确需要的代码/配置/脱敏结果文件，不使用`git add .`无差别提交。`reports/`默认忽略，因为可能包含本地路径和大文件；通过审查的简明结论应写到`experiments/G*.md`，保留真实原始报告的hash或私有存储标识。

完成第一轮后需要留存：environment.json、levir_audit.json、展开配置、100步日志、过拟合结果、G0/G1判定。此时还不应开始堆叠创新模块。
