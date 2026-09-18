# Start from the pinned Open-CD recipe. Run commands from this repo root.
# End-to-end CUDA training has not been validated in this starter repository.
_base_ = '../third_party/open-cd/configs/bit/bit_r18_256x256_40k_levircd.py'
data_root = 'data/LEVIR-CD'
train_dataloader = dict(dataset=dict(data_root=data_root))
val_dataloader = dict(dataset=dict(data_root=data_root))
test_dataloader = dict(dataset=dict(data_root=data_root))
randomness = dict(seed=17, deterministic=False)
