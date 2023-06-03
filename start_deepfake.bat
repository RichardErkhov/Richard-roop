@echo off
:: Упаковано и собрано телеграм каналом Neutogen News: https://t.me/neurogen_news
:: Пояснения:
:: Перед запуском стоят переменные, нацеленные на оптимизацию работы видеопамяти. В принципе, можете удалить если они вас смущают.
:: --max-memory 16 - тут пишите сколько готовы выделить оперативной памяти в гигабайтах. У меня стоит 16 гигабайт.
:: --gpu-threads 16 - Количество потоков Видеокарты, для обработки видео. Ставите в зависимости от того сколько у вас видеопамяти, 6 - потребляет примерно 8 Gb, 16 - 20 Gb. По моему личному опыту, выше 8-10 уже прироста производительности практически нет.

:: packed and assembled by telegram channel Neutogen News: https://t.me/neurogen_news
:: Explanations:
:: Before the run there are variables, that are aimed for optimization of work of RAM. If you want, you can delete them if you don't want to use them.
:: --max-memory 16 - Here you write how much RAM you want to allocate to program. I have 16 GB.
:: --gpu-threads 16 - Amount of threads of GPU, for video processing. Put according to your VRAM. 6 threads - take around 8 GB, 16 - 20GB. In experience, higher than 8-10 almost no speedup 

set PYTORCH_CUDA_ALLOC_CONF=garbage_collection_threshold:0.8,max_split_size_mb:512
set CUDA_MODULE_LOADING=LAZY

call venv\Scripts\activate.bat
python run.py --gpu --max-memory 16000 --gpu-threads 8
pause
