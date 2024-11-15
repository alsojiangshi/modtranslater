import os
import zipfile
import json
import yaml
import logging
import hashlib
import time
from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests
import argparse

# 日志配置
LOG_FILE = "translation.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)
logger = logging.getLogger()

# 翻译 API 配置（api来自桑帛云）
TRANSLATE_URL = "https://api.lolimi.cn/API/qqfy/api.php"


class Translator:
    """处理翻译操作的类"""
    def __init__(self, translate_url=TRANSLATE_URL):
        self.translate_url = translate_url

    def translate_text(self, text):
        """使用翻译 API 翻译文本"""
        params = {"msg": text, "type": "text"}
        try:
            logger.info(f"Sending translation request for text: '{text}'")
            response = requests.get(self.translate_url, params=params)
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 1:
                translated = result.get("text", text)
                logger.info(f"Translated text: '{text}' -> '{translated}'")
                return translated
            else:
                logger.warning(f"Translation failed for text: '{text}' | Response: {result}")
                return text  # 返回原文
        except Exception as e:
            logger.error(f"Error during translation: '{text}' | Error: {e}")
            return text


class JarFileHandler:
    """处理 .jar 文件的类"""
    def __init__(self, jar_path, output_dir):
        self.jar_path = jar_path
        self.output_dir = output_dir

    def extract(self):
        """解压 .jar 文件"""
        try:
            with zipfile.ZipFile(self.jar_path, 'r') as jar:
                for file in jar.namelist():
                    # 过滤掉不需要翻译的文件，例如 .class 文件
                    if file.endswith(('.class',)):
                        continue
                    jar.extract(file, self.output_dir)
            logger.info(f"Extracted {self.jar_path} to {self.output_dir}")
        except Exception as e:
            logger.error(f"Error extracting {self.jar_path} to {self.output_dir} | Error: {e}")

    def repack(self, new_jar_path):
        """将文件夹重新打包为 .jar 文件"""
        try:
            with zipfile.ZipFile(new_jar_path, 'w', zipfile.ZIP_DEFLATED) as jar:
                for root, _, files in os.walk(self.output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.output_dir)
                        jar.write(file_path, arcname)
            logger.info(f"Repacked into {new_jar_path}")
        except Exception as e:
            logger.error(f"Error repacking to {new_jar_path} | Error: {e}")


class FileHandler:
    """通用文件处理基类"""
    def __init__(self, file_path, translator):
        self.file_path = file_path
        self.translator = translator

    def translate(self):
        raise NotImplementedError("Subclasses should implement this method")


class LangFileHandler(FileHandler):
    """处理 .lang 文件的类"""
    def translate(self):
        try:
            logger.info(f"Reading LANG file: {self.file_path}")
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            translated_lines = []
            for line in tqdm(lines, desc=f"Translating {os.path.basename(self.file_path)}"):
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    translated = self.translator.translate_text(value.strip())
                    translated_lines.append(f"{key}={translated}\n")
                else:
                    translated_lines.append(line + "\n")

            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.writelines(translated_lines)
            logger.info(f"Successfully translated LANG file: {self.file_path}")
        except Exception as e:
            logger.error(f"Error processing LANG file: {self.file_path} | Error: {e}")


class JsonFileHandler(FileHandler):
    """处理 .json 文件的类"""
    def translate(self):
        try:
            logger.info(f"Reading JSON file: {self.file_path}")
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            def translate_json(obj):
                if isinstance(obj, dict):
                    return {key: translate_json(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [translate_json(item) for item in obj]
                elif isinstance(obj, str):
                    return self.translator.translate_text(obj)
                return obj

            translated_data = translate_json(data)

            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=4)
            logger.info(f"Successfully translated JSON file: {self.file_path}")
        except Exception as e:
            logger.error(f"Error processing JSON file: {self.file_path} | Error: {e}")


class YmlFileHandler(FileHandler):
    """处理 .yml 文件的类"""
    def translate(self):
        try:
            logger.info(f"Reading YML file: {self.file_path}")
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            def translate_yaml(obj):
                if isinstance(obj, dict):
                    return {key: translate_yaml(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [translate_yaml(item) for item in obj]
                elif isinstance(obj, str):
                    return self.translator.translate_text(obj)
                return obj

            translated_data = translate_yaml(data)

            with open(self.file_path, 'w', encoding='utf-8') as f:
                yaml.dump(translated_data, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"Successfully translated YML file: {self.file_path}")
        except Exception as e:
            logger.error(f"Error processing YML file: {self.file_path} | Error: {e}")


class ModTranslator:
    """主程序，负责自动汉化 Minecraft Mod"""

    def __init__(self, translator, output_dir="output"):
        self.translator = translator
        self.output_dir = output_dir

    def process_file(self, file_path):
        if file_path.endswith(".lang"):
            handler = LangFileHandler(file_path, self.translator)
        elif file_path.endswith(".json"):
            handler = JsonFileHandler(file_path, self.translator)
        elif file_path.endswith((".yml", ".yaml")):
            handler = YmlFileHandler(file_path, self.translator)
        else:
            logger.warning(f"Unsupported file format or file type (e.g., .class): {file_path}")
            return
        handler.translate()

    def translate_mod(self, jar_path):
        jar_name = jar_path.stem
        temp_dir = f"temp_{jar_name}"
        jar_handler = JarFileHandler(jar_path, temp_dir)

        try:
            jar_handler.extract()

            for root, _, files in os.walk(temp_dir):
                for file in files:
                    self.process_file(os.path.join(root, file))

            jar_hash = hashlib.md5(jar_path.read_bytes()).hexdigest()[:8]
            timestamp = time.strftime("%Y%m%d%H%M%S")
            output_jar_name = f"{jar_name}_translated_{timestamp}_{jar_hash}.jar"
            output_jar_path = os.path.join(self.output_dir, output_jar_name)

            jar_handler.repack(output_jar_path)
            logger.info(f"Successfully translated and repacked {jar_path} to {output_jar_path}")
        except Exception as e:
            logger.error(f"Error occurred while translating mod: {e}")
        finally:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(temp_dir)
                logger.info(f"Temporary directory {temp_dir} deleted.")


def process_mod(jar_path, mod_translator):
    try:
        mod_translator.translate_mod(jar_path)
    except Exception as e:
        logger.error(f"Error translating {jar_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Translate Minecraft Mods")
    parser.add_argument("--exclude", type=str, nargs="+", help="Exclude specific files")
    args = parser.parse_args()

    current_dir = os.getcwd()
    translator = Translator()
    mod_translator = ModTranslator(translator)

    jar_files = list(Path(current_dir).glob("*.jar"))

    if args.exclude:
        jar_files = [f for f in jar_files if f.name not in args.exclude]

    if not jar_files:
        logger.info("No .jar files found in the current directory.")
        return

    os.makedirs(mod_translator.output_dir, exist_ok=True)

    # 使用线程池并行处理多个 mod 文件（最多4线程）
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(tqdm(executor.map(process_mod, jar_files, [mod_translator] * len(jar_files)),
                  total=len(jar_files),
                  desc="Translating Mods"))

    logger.info("All mods processed.")

if __name__ == "__main__":
    main()
