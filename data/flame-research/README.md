# 火焰研究数据登记与划分

> 2026-10-07：SAFIRE 公开 schema 使用 image_name，未提供 video_id/event_id。内部 image_id 需由 scenario + image_name 构造并用哈希核实；推定去重簇和可追溯事件须分列。BoWFire 原下载 API 已列出压缩包，完整数据仍未下载。

当前仅有规范，没有已下载的数据。来源入口和限制见[来源审计](../../references/flame-research-sources.md)。

每个实际图像写一行 JSON 到本地 manifest.jsonl，字段必须包含：

- dataset、dataset_revision、source_url、license_reference；
- image_id、relative_path、sha256、width、height；
- group_id、group_basis（video/event/source/near_duplicate）、unknown_source；
- task_label（visible_flame/no_visible_flame）、mask_path、mask_sha256；没有 mask 时为 null；
- direction（D1/D2）、split（support/calibration/screen/confirm/audit/auxiliary）；
- original_question_ids（SAFIRE 同图多问映射）、scenario；
- exclusion_reason；不符合任务的样本登记原因后排除，不能静默删掉预测错误样本。

source_url 不放含令牌或临时签名的下载地址。清单可以只保存公开 ID、摘要和相对路径，不上传原图。来源组映射、抽样脚本和最终 manifest 的 SHA-256 必须在开跑前提交。

组级拆分顺序：跨库完全去重 → 疑似近重复复核 → 合并来源组 → 任务标签/适用性审计 → 固定种子分层划分 → 写入哈希并冻结。先分组再抽图，避免长视频占据大部分名额。

获取后填写真实统计：原图数、去重后图数、独立组数、来源未知组数、正负数、每个 split 计数、排除理由分布。论文中分别报告这些数量。空字段不得通过启动检查。
