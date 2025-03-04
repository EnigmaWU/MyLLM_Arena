#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPT2PDF - 将 PPT 文件转换为 PDF 文件的工具
支持 .ppt 和 .pptx 格式，可以输出合并 PDF 或单页 PDF 文件
"""

import os
import sys
import argparse
import logging
import platform
import tempfile
import shutil
from pathlib import Path
import textwrap  # 导入textwrap用于处理多行字符串缩进

__version__ = "1.0.0"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PPT2PDF")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="PPT2PDF - 将PPT文件转换为PDF文件")
    parser.add_argument("--PPT", required=True, help="输入PPT文件的路径")
    parser.add_argument("--Output", required=True, help="输出PDF文件的路径")
    parser.add_argument("--Split", action="store_true", help="是否将每页独立输出为PDF文件")
    parser.add_argument("--Help", action="store_true", help="查看帮助信息")
    parser.add_argument("--Version", action="store_true", help="查看版本信息")
    parser.add_argument("--Debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    if args.Help:
        parser.print_help()
        sys.exit(0)
    
    if args.Version:
        print(f"PPT2PDF 版本: {__version__}")
        sys.exit(0)
    
    if args.Debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    return args

def check_file_exists(file_path):
    """检查文件是否存在"""
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return False
    return True

def check_file_extension(file_path, allowed_extensions):
    """检查文件扩展名是否符合要求"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in allowed_extensions:
        logger.error(f"不支持的文件类型: {ext}，仅支持: {', '.join(allowed_extensions)}")
        return False
    return True

def convert_ppt_to_pdf_windows(ppt_path, output_path, split=False):
    """在Windows平台使用COM接口将PPT转换为PDF"""
    try:
        import comtypes.client
        
        logger.debug("使用Windows COM接口转换PPT")
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = True
        
        presentation = powerpoint.Presentations.Open(ppt_path, ReadOnly=True)
        
        if split:
            # 导出每页为单独的PDF
            base_name = os.path.splitext(output_path)[0]
            slide_count = presentation.Slides.Count
            
            for i in range(1, slide_count + 1):
                pdf_path = f"{base_name}_{i}.pdf"
                logger.debug(f"导出第 {i} 页到 {pdf_path}")
                presentation.Slides(i).Export(pdf_path, "PDF")
        else:
            # 导出为单个PDF
            presentation.SaveAs(output_path, 32)  # 32 对应 PDF 格式
        
        presentation.Close()
        powerpoint.Quit()
        
        return True
    except Exception as e:
        logger.error(f"Windows转换失败: {str(e)}")
        return False

def convert_ppt_to_pdf_mac(ppt_path, output_path, split=False):
    """在Mac平台使用py-appscript将PPT转换为PDF"""
    try:
        # 检查PowerPoint是否已安装
        if not os.path.exists("/Applications/Microsoft PowerPoint.app"):
            logger.error("未找到Microsoft PowerPoint")
            return False
        
        # 使用原始的文件路径
        absolute_ppt_path = os.path.abspath(ppt_path)
        absolute_output_path = os.path.abspath(output_path)
        
        # 如果是分页模式，获取输出基本路径
        base_name = os.path.splitext(absolute_output_path)[0]
        
        logger.debug("使用Python子进程方式转换PPT")
        
        if split:
            # 创建临时文件用于合并输出
            temp_pdf = tempfile.mktemp(suffix='.pdf')
            
            # 首先将PPT转为单个PDF (使用textwrap.dedent移除多余缩进)
            convert_script = textwrap.dedent('''
                import sys
                import os
                try:
                    from appscript import app, k
                    
                    # 打开PowerPoint
                    powerpoint = app('Microsoft PowerPoint')
                    
                    # 打开文件
                    pres = powerpoint.open('{ppt_path}')
                    
                    # 另存为PDF
                    pres.save_as(in_='{temp_pdf}', as_=k.PDF)
                    
                    # 关闭文件
                    pres.close(saving=k.no)
                    
                    print("转换成功")
                    sys.exit(0)
                except Exception as e:
                    print(f"错误: {{str(e)}}")
                    sys.exit(1)
            ''').format(ppt_path=absolute_ppt_path, temp_pdf=temp_pdf)
            
            # 创建临时Python脚本
            fd, temp_script = tempfile.mkstemp(suffix='.py')
            with os.fdopen(fd, 'w') as f:
                f.write(convert_script)
            
            # 执行脚本
            import subprocess
            result = subprocess.run([sys.executable, temp_script], capture_output=True, text=True)
            
            # 清理临时脚本
            os.unlink(temp_script)
            
            if result.returncode != 0:
                logger.error(f"Python执行失败: {result.stderr}")
                return False
            
            # 现在分割PDF
            try:
                # 使用PyPDF2分割PDF
                from PyPDF2 import PdfReader, PdfWriter
                
                reader = PdfReader(temp_pdf)
                total_pages = len(reader.pages)
                
                for i in range(total_pages):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[i])
                    
                    output_file = f"{base_name}_{i+1}.pdf"
                    with open(output_file, 'wb') as f:
                        writer.write(f)
                
                # 删除临时PDF
                os.unlink(temp_pdf)
                return True
            
            except ImportError:
                logger.error("未安装PyPDF2。请使用pip install PyPDF2安装。")
                return False
        else:
            # 非分页模式，直接转换为单个PDF (使用textwrap.dedent移除多余缩进)
            convert_script = textwrap.dedent('''
                import sys
                try:
                    from appscript import app, k
                    
                    # 打开PowerPoint
                    powerpoint = app('Microsoft PowerPoint')
                    
                    # 打开文件
                    pres = powerpoint.open('{ppt_path}')
                    
                    # 另存为PDF
                    pres.save_as(in_='{output_path}', as_=k.PDF)
                    
                    # 关闭文件
                    pres.close(saving=k.no)
                    
                    print("转换成功")
                    sys.exit(0)
                except Exception as e:
                    print(f"错误: {{str(e)}}")
                    sys.exit(1)
            ''').format(ppt_path=absolute_ppt_path, output_path=absolute_output_path)
            
            # 创建临时Python脚本
            fd, temp_script = tempfile.mkstemp(suffix='.py')
            with os.fdopen(fd, 'w') as f:
                f.write(convert_script)
            
            # 执行脚本
            import subprocess
            result = subprocess.run([sys.executable, temp_script], capture_output=True, text=True)
            
            # 清理临时脚本
            os.unlink(temp_script)
            
            if result.returncode != 0:
                logger.error(f"Python执行失败: {result.stderr}")
                return False
            
            return True
            
    except Exception as e:
        logger.error(f"Mac转换失败: {str(e)}")
        return False

def convert_ppt_to_pdf_linux(ppt_path, output_path, split=False):
    """在Linux平台使用LibreOffice将PPT转换为PDF"""
    try:
        import subprocess
        
        logger.debug("使用LibreOffice转换PPT")
        
        # 创建临时目录用于输出
        temp_dir = tempfile.mkdtemp()
        temp_output = os.path.join(temp_dir, "output.pdf")
        
        # 调用LibreOffice进行转换
        cmd = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", temp_dir, ppt_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"LibreOffice执行失败: {result.stderr}")
            shutil.rmtree(temp_dir)
            return False
        
        if split:
            # 使用pdftk或pdfseparate分割PDF
            try:
                # 首先尝试使用pdftk
                base_name = os.path.splitext(output_path)[0]
                cmd = ["pdftk", temp_output, "burst", "output", f"{base_name}_%d.pdf"]
                subprocess.run(cmd, capture_output=True, check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                try:
                    # 如果pdftk不可用，尝试使用pdfseparate
                    base_name = os.path.splitext(output_path)[0]
                    cmd = ["pdfseparate", temp_output, f"{base_name}_%d.pdf"]
                    subprocess.run(cmd, capture_output=True, check=True)
                except (subprocess.SubprocessError, FileNotFoundError):
                    logger.error("未找到PDF分割工具(pdftk或pdfseparate)")
                    shutil.rmtree(temp_dir)
                    return False
        else:
            # 复制生成的PDF到目标位置
            shutil.copy2(temp_output, output_path)
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        return True
    
    except Exception as e:
        logger.error(f"Linux转换失败: {str(e)}")
        return False

def convert_ppt_to_pdf(ppt_path, output_path, split=False):
    """根据操作系统类型选择合适的转换方法"""
    system = platform.system()
    
    logger.debug(f"检测到操作系统: {system}")
    
    if system == "Windows":
        return convert_ppt_to_pdf_windows(ppt_path, output_path, split)
    elif system == "Darwin":  # macOS
        return convert_ppt_to_pdf_mac(ppt_path, output_path, split)
    elif system == "Linux":
        return convert_ppt_to_pdf_linux(ppt_path, output_path, split)
    else:
        logger.error(f"不支持的操作系统: {system}")
        return False

def main():
    """主函数"""
    args = parse_arguments()
    
    # 检查输入文件
    ppt_path = os.path.abspath(args.PPT)
    if not check_file_exists(ppt_path):
        return 1
    if not check_file_extension(ppt_path, [".ppt", ".pptx"]):
        return 1
    
    # 准备输出路径
    output_path = os.path.abspath(args.Output)
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.debug(f"创建输出目录: {output_dir}")
        except OSError as e:
            logger.error(f"无法创建输出目录: {str(e)}")
            return 1
    
    # 执行转换
    logger.info(f"开始转换 {ppt_path} -> {output_path}")
    success = convert_ppt_to_pdf(ppt_path, output_path, args.Split)
    
    if success:
        if args.Split:
            logger.info(f"转换成功，已将每页独立输出为PDF文件（前缀: {os.path.splitext(output_path)[0]}_）")
        else:
            logger.info(f"转换成功，已输出到 {output_path}")
        return 0
    else:
        logger.error("转换失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
