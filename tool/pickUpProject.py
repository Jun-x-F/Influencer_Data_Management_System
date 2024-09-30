"""
@FileName：pickUpProject.py
@Description：
@Author：Libre
@Time：2024/5/27 上午9:19
@Department：IT信息中心-AI
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import requests
from PyInstaller import __main__

from tool.FileUtils import get_project_path


def pyinstaller_package(projectDir):
    dist_path = projectDir + r"\dist"
    app_dir = projectDir + r"\app.py"
    upx_dir = projectDir + r"\upx_4.2.4\upx-4.2.4-win64\upx-4.2.4-win64"
    __main__.run(
        [
            "-F",
            f"--upx-dir={upx_dir}",
            f"--distpath={dist_path}",
            f"-n=influencer_data_management",
            app_dir,
        ]
    )


def handle_remove_readonly(func, path, exc):
    """
    处理只读文件或目录的删除
    """
    # 尝试修改文件权限
    os.chmod(path, 0o755)
    # 再次尝试删除
    func(path)


def clean_last_build(projectDistDir):
    # 清理上次文件
    if os.path.isdir(projectDistDir):
        # 删除用户数据目录
        shutil.rmtree(
            projectDistDir, ignore_errors=True, onerror=handle_remove_readonly
        )


def get_all_file_paths(directory):
    file_paths = [
        r"D:\project\python\customerSpider\tools\pickUp\restart.bat",
    ]

    # 遍历给定目录及其所有子目录中的所有文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 将文件路径添加到列表中
            file_paths.append(os.path.join(root, file))

    return file_paths


def zip_list(application_list, zip_out_path):
    with zipfile.ZipFile(zip_out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for application in application_list:
            if os.path.isdir(application):
                zip_dir(application, zf)
            elif os.path.isfile(application):
                fileName = application.split(os.sep)[-1]
                print("zip adding file %s" % application)
                zf.write(application, fileName)


def zip_dir(application, zf):
    for path, dirs, files in os.walk(application):
        for file in files:
            file_path = os.path.join(path, file)
            print("zip adding file %s" % file_path)
            zf.write(file_path)


def upload_zip_file(file_path, version):
    url = "http://47.119.161.182:8080/smt/upload/runSpider"

    # 打开文件并读取二进制数据
    with open(file_path, "rb") as file:
        files = {"data": file}
        data = {"version": version}

        # 发送POST请求
        response = requests.post(url, files=files, data=data)

    # 检查响应状态码
    if response.status_code == 200:
        print("文件上传成功")
    else:
        print(f"文件上传失败，状态码：{response.status_code}")
        print("响应内容：", response.text)


def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(result.stdout)
        print(result.stderr)
        exit(result.returncode)
    else:
        print(result.stdout)


if __name__ == "__main__":
    current_version = "1.0.3"

    print("Running pip check...")
    run_command("pip check")

    print("Checking for outdated dependencies...")
    run_command("pip list --outdated")

    File = Path(__file__).resolve()

    projectDir = get_project_path()

    # input(projectDir)

    projectDistDir = get_project_path() + r"\dist"

    print(f"now version is {current_version}")
    print(f"now dir is {projectDir}")

    # 清除
    clean_last_build(projectDistDir)

    # 打包+upx压缩
    pyinstaller_package(projectDir)
