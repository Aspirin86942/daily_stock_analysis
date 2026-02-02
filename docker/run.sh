#!/bin/bash
# 群晖 NAS 定时任务脚本
# 用法：在群晖任务计划中填入此脚本路径
docker run --rm --env-file /volume1/docker/daily_stock_analysis/.env -e TZ=Asia/Shanghai -v /volume1/docker/daily_stock_analysis/data:/app/data -v /volume1/docker/daily_stock_analysis/logs:/app/logs -v /volume1/docker/daily_stock_analysis/reports:/app/reports -v /volume1/docker/daily_stock_analysis/assets:/app/assets stock-analyzer python main.py
