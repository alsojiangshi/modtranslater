# modtranslator
这是一个利用QQ翻译api自动翻译Minecraft的mod的python脚本，可以将.jar格式的mod解包后将其中的.lang，.json，.yml文件机翻为中文并保存，然后重新打包为.jar包。作者还是学生，不是计算机类专业，刚接触python，写这玩意儿写了4个版本，很多功能尚存问题，大佬勿喷。随缘更新~(真的有时间吗......)
# Minecraft Mod 翻译工具
该项目提供一个自动化翻译Minecraft Mod资源文件的工具，支持翻译.lang、.json、.yml格式的文件，能够帮助Mod开发者快速将Mod的文本内容进行语言翻译。本工具使用了外部翻译API并通过并行处理提高翻译效率。

# 项目简介
这个工具通过解压.jar文件并提取其中的.lang、.json、.yml等文本文件，调用外部翻译API进行翻译，最后将翻译后的文件重新打包为.jar文件。程序使用并行处理（最多4线程）以加快批量翻译的速度。

# 功能特性
自动识别并处理.lang、.json、.yml文件。
使用桑帛云API进行自动翻译。
支持对.jar文件内的文件进行解压、翻译和重打包。
提供日志记录功能，方便查看处理进度和错误。
支持排除特定的文件进行翻译（通过命令行参数）。
支持并行处理多个.jar文件，优化处理效率。
# 使用方法
克隆或下载项目：

bash
复制代码
git clone https://github.com/alsojiangshi/modtranslator.git
cd modtranslator
安装依赖：

本工具需要Python 3.7及以上版本。首先安装所需依赖包：

bash
复制代码
pip install -r requirements.txtPIP install -r requirements.txt
准备.jar文件：

将您要翻译的Minecraft Mod的.jar文件放在项目根目录下。
确保有ymal,request,tqdm三个包后运行它。

# 日志记录
程序会生成translation.log日志文件，记录翻译过程中的关键信息和错误。如果翻译失败或发生错误，程序会将错误信息记录到日志中，方便查看和调试。

# 错误处理
程序在翻译过程中会捕获异常，并记录到日志中，确保即使某些文件处理失败，整个程序也能继续运行。
例如，如果翻译API调用失败，程序会返回原文并在日志中记录错误。
对于.jar文件解压、翻译和重打包等操作，程序也做了异常处理，确保在出错时提供清晰的错误信息。
# 贡献
如果您想贡献代码或提出建议，请提交拉取请求（Pull Request）或创建问题（Issue）。在贡献之前，请确保遵守以下规则：

确保代码风格统一，遵循PEP 8规范。
为主要功能添加单元测试。
详细描述问题及解决方案，尤其是在拉取请求中。
