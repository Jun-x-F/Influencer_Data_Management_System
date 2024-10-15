@echo off
call conda activate DataAnalysis_39

start "Flask app" cmd /k "conda activate DataAnalysis_39 && python D:\wzhData\BaiduSyncdisk\project\python\Influencer_Data_Management_System\app.py"
