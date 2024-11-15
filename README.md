# modtranslater
作者还是学生，不是计算机类专业，刚接触python，写这玩意儿写了4个版本，很多功能尚存问题，大佬勿喷。随缘更新~(真的有时间吗......)
modtranslater 是一个用于汉化 Minecraft Mod 的工具。它支持自动翻译 `.lang`、`.json` 和 `.yml` 文件中的文本内容，并将其重新打包为 `.jar` 文件。该项目通过调用在线翻译 API 来实现文本的自动翻译，旨在简化 Minecraft Mod 的本地化过程。

## 功能

- **支持文件类型**：`.lang`、`.json` 和 `.yml` 文件的自动翻译。
- **自动化翻译**：通过调用外部翻译 API 自动翻译文本，减少手动翻译的工作量。
- **批量处理**：支持批量处理多个 Minecraft Mod 文件，节省时间。
- **输出**：将翻译后的文件重新打包为 `.jar` 文件，生成一个新版本的 Mod。

## 安装

### 前提条件

1. 安装 Python 3.x 及相关依赖库。

   ```bash
   pip install -r requirements.txt
