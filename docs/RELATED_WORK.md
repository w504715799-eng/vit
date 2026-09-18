# 数据、基线与创新风险：初始来源表

核验日期：2026-09-18。下列来源为作者论文、官方仓库或官方文档。当前完成的是来源定位和关键摘要/代码核对，**不是完整查新或已完成精读**。G0须补齐最近文献与全文差异分析；摘要未写某项设计，不代表全文没有。

| 来源 | 入口 | 与本项目的关系及必须核验的差异 |
|---|---|---|
| LEVIR-CD / STANet，Chen & Shi，2020 | [数据官网](https://justchenhao.github.io/LEVIR/)；[原论文](https://doi.org/10.3390/rs12101662) | 主数据集；637对1024×1024图像、0.5m/px；限定学术用途，禁止商业使用。不要混用LEVIR-CD+，不要擅自再分发原图。 |
| S2Looking，Shen等，2021 | [论文](https://arxiv.org/abs/2107.09244)；[作者数据仓库](https://github.com/S2Looking/Dataset) | 第二数据集，侧视等挑战。其原生难度不能全部归因于配准误差；使用作者划分和标签说明。 |
| BIT，Chen等，2021 | [论文](https://arxiv.org/abs/2103.00208)；[作者实现](https://github.com/justchenhao/BIT_CD) | 轻量起点；不是足够代表全部近期方法的唯一对照。 |
| Changer，Fang等，2023 | [论文](https://arxiv.org/abs/2209.08290)；[Open-CD](https://github.com/likyoo/open-cd) | 已有FDAF双向流对齐融合，必须对比；不能将“加入对齐”写为首创。 |
| ChangeFormer，Bandara & Patel，2022 | [论文](https://arxiv.org/abs/2201.01293) | 常见Transformer变化检测参照；需区分其原始训练设置与统一公平设置。 |
| FAEWNet，Li等，2025 | [论文](https://arxiv.org/abs/2504.12619)；[作者代码](https://github.com/SUPERMAN123000/FAEWNet) | 明确研究分布适配和边缘约束warping，是直接创新风险；特别比较边界保护、背景噪声、光流估计和变化保留方式。 |
| DC-Mamba，Sun & Guo，2025 | [预印本](https://arxiv.org/abs/2509.15563) | 包含双时相可变形对齐和变化增强；预印本身份不能自动写成已获同行评审认可。需要精读相似机制及实验范围。 |
| Open-CD technical report，Li等 | [报告](https://arxiv.org/abs/2407.15317)；[官方仓库](https://github.com/likyoo/open-cd) | 开发基础与统一评价框架；记录commit和论文引用，不把框架现成功能算作自己的贡献。 |

## 已核对的工程事实

上游main读取到的提交：`790a1972b538baaaffd4c3022a4d9afaa3f861e5`。

[BIT配置](https://github.com/likyoo/open-cd/blob/790a1972b538baaaffd4c3022a4d9afaa3f861e5/configs/bit/bit_r18_256x256_40k_levircd.py)继承[统一256/40k配置](https://github.com/likyoo/open-cd/blob/790a1972b538baaaffd4c3022a4d9afaa3f861e5/configs/common/standard_256x256_40k_levircd.py)，其中batch_size=8、40k iteration、按val mIoU选best。配置内数据根目录需要同时覆盖train/val/test的dataset.data_root。

[BIT模型表](https://github.com/likyoo/open-cd/blob/790a1972b538baaaffd4c3022a4d9afaa3f861e5/configs/bit/README.md)给出LEVIR测试变化类F1=90.26、IoU=82.25。**这是特定实现的test参考，不是本项目已复现成绩，更不能作为val的官方指标。**

[依赖检查](https://github.com/likyoo/open-cd/blob/790a1972b538baaaffd4c3022a4d9afaa3f861e5/opencd/__init__.py)限制MMCV<2.2.0、MMSegmentation<1.3.0。训练环境须经真实硬件验证；本会话仅CPU辅助工具测试。

## G0必须完成的差异表

为每篇最接近论文补齐以下字段，并标明页码/公式/源码位置：

```text
paper_id / publication_status / alignment_operator / reliability_definition
raw_change_preservation / supervision_region / geometric_error_protocol
augmentation_control / parameter_matched_control / code_and_weights
what_is_same / what_is_different / experiment_that_can_disprove_our_claim
```

重点不是找“没用过某个缩写”，而是找可以被公平实验区分的机制或结论。若前人已覆盖同样的可靠性门控、变化保留和抗错位验证，G0应STOP_PATH或重新定义问题。

## 投稿认定

本仓库不维护未经核验的期刊分区或录用概率。G0记录单位认可的分区版本、大类/小类、文章类型、费用与时限；G9按投稿当日再次核验。JSTARS可作为范围候选，但任何“二区/三区”结论都应以单位最终口径为准。
