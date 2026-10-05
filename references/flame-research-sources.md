# 来源与可用性审计

核对日期：2026-10-05。已阅读论文摘要、官方仓库/模型卡与公开数据说明；**尚未下载完整数据、取得模型权重或复现任何结果**。公开入口不等于可以无条件再分发。论文/数据引用应在开跑前补齐版本与正式 BibTeX。

| 对象 | 直接来源 | 对本计划的意义 / 限制 |
| --- | --- | --- |
| FSSDINO，2026-02 | [论文](https://arxiv.org/abs/2602.07550)；[作者代码](https://github.com/hussni0997/fssdino) | 冻结 DINOv3 少样本分割与最后一层强基线；预印本。代码里的 oracle 不能用于目标集选层。部分 README 配置路径读取未成功，运行前须核对。 |
| DINOv3，2025 | [官方仓库](https://github.com/facebookresearch/dinov3) | 可选 ViT-B/16；权重可能需要访问申请，尚未核实本账号访问。2026 前沿来自研究问题，不来自冒称骨干年份。 |
| SAFIRE，2026-09 | [论文](https://arxiv.org/abs/2609.07823)；[作者代码](https://github.com/RISys-Lab/SAFIRE) | 论文标注 EMNLP 2026 Findings；火烟理解可靠性基准。原评测与本计划二分类子集不同。 |
| SAFIRE 数据 | [83K 图像](https://huggingface.co/datasets/RISys-Lab/SAFIRE_83K)；[193K 问答](https://huggingface.co/datasets/RISys-Lab/SAFIRE_193K_mcvqa) | 问答基于约 9.7K 图像，多问共享同图；含机器辅助标注，需独立标签审计和真实照片筛选。不能训练 83K 后无去重地评测问答集。 |
| Qwen2.5-VL-3B | [官方模型卡](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct) | 作为冻结小模型降低成本；不是 2026 新模型，也不能直接套用 SAFIRE 对更大模型的结果。 |
| DFire | [作者仓库](https://github.com/gaia-solutions-on-demand/DFireDataset) | 21K 以上图像，fire/smoke 框；可做火焰存在标签和无火校准，不提供本计划需要的像素 mask。下载链接存在，完整文件未验证。 |
| Khan Fire_Seg_Dataset | [作者仓库](https://github.com/hayatkhan8660-maker/Fire_Seg_Dataset)；[IEEE 论文](https://ieeexplore.ieee.org/abstract/document/9894370) | 提供分割图像与人工 mask 的入口；分组来源、下载、具体许可待核实。不能默认数据量等于独立组数。 |
| BoWFire | [原论文](https://arxiv.org/abs/1506.03495)；[作者相关数据说明](https://www.icmc.usp.br/pessoas/junio/PublishedPapers/Cazzolato_et_al_SBBD2017.pdf)；[原下载入口](https://bitbucket.org/gbdi/bowfire-dataset/downloads/) | 文献报告 226 图像及 mask；下载入口可打开但未读取到文件清单，必须将可获取性设为前置门。不是 2026 数据集。 |
| FLAME | [作者仓库](https://github.com/AlirezaShamsoshoara/Fire-Detection-UAV-Aerial-Image-Classification-Segmentation-UnmannedAerialVehicle)；[IEEE 数据](https://ieee-dataport.org/open-access/flame-dataset-aerial-imagery-pile-burn-detection-using-drones-uavs) | 提供航拍火焰图像和分割数据入口；受控采集与相关视频帧限制外推，只用作固定辅助诊断。 |
| 既有零样本火灾 VLM 研究 | [Neurocomputing 论文 DOI](https://doi.org/10.1016/j.neucom.2025.131403) | 2025 已有相关研究，使用 CLIP/LLM 本身不是新颖性。前置查新应阅读全文核对重叠。 |

本次提出的困难背景原型和全局—局部乘积规则，均为计划中的待测方法，不是文献已经证明有效的成果。性能门槛由项目决策制定，不能归因于上述论文。
