"""
Check CUDA availability and basic GPU properties using the venv Python.
Run with the project's venv python to inspect the system used for training.
"""
import sys
try:
    import torch
except Exception as e:
    print('error_importing_torch', e)
    sys.exit(2)

print('cuda_available:', torch.cuda.is_available())
print('torch_version:', torch.__version__)
print('cuda_version (build):', torch.version.cuda)
try:
    cnt = torch.cuda.device_count()
    print('device_count:', cnt)
    if cnt>0:
        for i in range(cnt):
            try:
                name = torch.cuda.get_device_name(i)
                prop = torch.cuda.get_device_properties(i)
                print(f'device[{i}] name: {name}')
                print(f'device[{i}] total_memory_MB: {prop.total_memory//(1024*1024)}')
                print(f'device[{i}] major_minor: {prop.major}.{prop.minor}')
            except Exception as e:
                print(f'device[{i}] info_error:', e)
except Exception as e:
    print('device_query_error', e)

sys.exit(0)
