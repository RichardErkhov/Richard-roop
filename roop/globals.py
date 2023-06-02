import onnxruntime

use_gpu = False
all_faces = False
providers = onnxruntime.get_available_providers()
results = []
if 'TensorrtExecutionProvider' in providers:
    providers.remove('TensorrtExecutionProvider')
