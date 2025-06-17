import streamlit as st
import random
import re
import json
from datetime import datetime
import itertools
import pandas as pd

# --- Streamlitの設定（必ずスクリプトの最初に配置） ---
st.set_page_config(page_title="プロンプトジェネレーター", layout="centered")

# --- Language Dictionary ---
# 各言語のテキストをここに定義します
LANGUAGES = {
    "en": { # ★デフォルト言語を英語に変更★
        "title": "Image Generation Prompt Generator",
        "divider": "---",
        "sidebar_data_management": "Save/Load Data",
        "upload_file": "Upload Settings File",
        "upload_success": "Settings loaded successfully.",
        "upload_invalid_format": "Invalid file format. 'keyword_lists' and 'list_sets' keys are required.",
        "upload_invalid_json": "Invalid JSON file.",
        "upload_invalid_key_type": "Invalid key format in JSON file (could not convert to integer).",
        "download_settings_button": "Download Current Settings (JSON)",
        "download_start_json": "Start Download (JSON)",
        "download_prompts_button": "Download Generated Prompts (TXT)",
        "download_start_txt": "Start Download (TXT)",
        "no_prompts_yet": "No prompts generated yet.",
        "keyword_list_management_title": "Keyword/Text List Input",
        "keyword_list_instruction": "Enter keywords or text phrases for each list, one per line.",
        "list_name_prefix": "List",
        "delete_button": "Delete",
        "list_content_label": "Content",
        "upload_txt_to_list": "Load TXT to",
        "add_new_list": "Add New List",
        "list_set_management_title": "List Set Management",
        "list_set_instruction": "Combine keyword/text lists to define 'sets' for prompt generation.",
        "no_set_yet": "No list sets have been created yet. Please create a new set.",
        "available_keyword_lists": "Currently Available Keyword/Text Lists:",
        "id_col": "ID",
        "name_col": "Name",
        "keyword_count_col": "Item Count",
        "no_keyword_lists": "No keyword/text lists available.",
        "set_name_prefix": "Set",
        "set_order_label": "Order (e.g., 1 3 2)",
        "invalid_list_num_warning": "List number **`{}`** is invalid. Please specify a list ID within the available range (1 to {}) and that exists.",
        "invalid_input_warning": "**`{}`** is invalid input. Please use half-width numbers and spaces.",
        "value_error_warning": "Order must be entered with half-width numbers and spaces.",
        "include_in_generation": "Include this set in generation",
        "new_set_name_input": "Enter name for new list set",
        "create_new_set_button": "Add New Set",
        "set_created_success": "Set **`{}`** created. Please specify the order.",
        "enter_set_name": "Please enter a name for the new set.",
        "prompt_generation_title": "Prompt Generation",
        "generation_mode_label": "Prompt Generation Mode",
        "random_gen_mode": "Random Generation",
        "all_combinations_gen_mode": "All Combinations Generation",
        "specific_list_sweep_gen_mode": "Specific List Sweep + Other Random Generation",
        "num_prompts_to_generate": "Number of prompts to generate per set",
        "all_combinations_info": "In 'All Combinations' mode, all possible combinations of the selected list set will be generated. This may result in a very large number of prompts.",
        "specific_list_sweep_info": "This mode generates all combinations of specified lists, with other lists chosen randomly. The **number of prompts generated will be the number of combinations from the full sweep lists**.",
        "full_sweep_list_ids_title": "Specify Full Sweep Lists",
        "full_sweep_list_ids_instruction": "Enter the **numbers of the lists you want to sweep all combinations** for, separated by half-width spaces.\nE.g., `1 3` will generate all combinations of List 1 and List 3 from the set, and choose randomly from other lists.",
        "full_sweep_list_num_input": "List numbers for full sweep",
        "output_display_method": "Prompt Display Method",
        "display_by_set": "Display by Set",
        "display_all_together": "Display All Together",
        "shuffle_results": "Shuffle generated prompts for display",
        "line_spacing_display": "Output Line Spacing",
        "line_spacing_single": "Display with one empty line (for copy/paste)",
        "line_spacing_none": "Display without empty lines",
        "generate_button": "Generate Prompts",
        "no_keyword_in_list_warning": "List **`{list_num}`** in set '{set_name}' has no items. This list will be skipped.",
        "no_full_sweep_list_warning": "For set '{set_name}', no full sweep lists were specified or invalid numbers were included. Falling back to random generation for this set.",
        "partial_gen_warning": "For set '{set_name}', 'Specific List Sweep + Other Random Generation' was expected to generate **{target_count}** prompts, but only **{generated_count}** were generated. This can happen if random choices are too limited.",
        "generated_from_set": "--- Generated from Set: 『**{}**』 ---", # 削除予定
        "generated_prompts_count": "✅ Generated Prompts ({} items):", # 削除予定
        "failed_to_generate_set": "Failed to generate prompts from set '{}'.",
        "generated_from_all_sets": "--- Prompts Generated from All Sets ---", # 削除予定
        "no_prompts_generated": "No prompts generated.",
        "set_data_corrupt_error": "Set '{}' data is corrupted or invalid. Please re-save the set.",
        "select_at_least_one_set": "Please select at least one list set to generate prompts.",
        "prompt_edit_corner": "Prompt Editing Corner",
        "no_prompts_to_edit": "Generate prompts to edit them here.",
        "remove_specific_words": "Remove Specific Words",
        "remove_words_input_label": "Enter words to remove, separated by commas (e.g., masterpiece, best quality)",
        "remove_words_button": "Remove Words",
        "words_removed_success": "Specified words removed.",
        "prompts_for_copy": "Prompts for Copying",
        "copy_button": "Copy Prompts", # このキーは使われなくなる
        "copy_success": "Copied to clipboard!", # このキーは使われなくなる
        "set_separator": "--- SET: {set_name} ({count} prompts) ---",

        "sample_list_name_1": "Quality",
        "sample_list_name_2": "Hair Description",
        "sample_list_name_3": "Outfit Details",
        "sample_list_name_4": "Eye Details",
        "sample_list_name_5": "Background Scene",
        "sample_list_content_1": "masterpiece, best quality, ultra detailed\n1girl, solo, cute face",
        "sample_list_content_2": "long blonde hair, twin tails\nshort brown hair, messy\nsilver hair, braided",
        "sample_list_content_3": "japanese school uniform\ntraditional kimono, floral pattern\nmaid outfit, frilly apron",
        "sample_list_content_4": "blue eyes, sparkling\ngreen eyes, narrow pupils\nbrown eyes, gentle gaze",
        "sample_list_content_5": "lush flower field, sunny day\nvibrant city street, night lights\nsecluded beach, sunset view",
        "sample_set_name_0": "Character Full Prompt",
        "sample_set_name_1": "Landscape Base",
        "sample_set_name_2": "Person & Expression",
    },
    "ja": {
        "title": "画像生成プロンプトジェネレーター",
        "divider": "---",
        "sidebar_data_management": "データの保存・読み込み",
        "upload_file": "設定ファイルをアップロード",
        "upload_success": "設定を正常に読み込みました。",
        "upload_invalid_format": "無効なファイル形式です。'keyword_lists'と'list_sets'のキーが必要です。",
        "upload_invalid_json": "無効なJSONファイルです。",
        "upload_invalid_key_type": "JSONファイル内のキーが不正な形式です（整数に変換できませんでした）。",
        "download_settings_button": "現在の設定をダウンロード (JSON)",
        "download_start_json": "ダウンロード開始 (JSON)",
        "download_prompts_button": "生成されたプロンプトをダウンロード (TXT)",
        "download_start_txt": "ダウンロード開始 (TXT)",
        "no_prompts_yet": "まだ生成されたプロンプトがありません。",
        "keyword_list_management_title": "キーワード／テキストリスト入力",
        "keyword_list_instruction": "各リストにキーワードまたはテキストフレーズを1行ずつ入力してください。",
        "list_name_prefix": "リスト",
        "delete_button": "削除",
        "list_content_label": "内容",
        "upload_txt_to_list": "にTXTを読み込む",
        "add_new_list": "新しいリストを追加",
        "list_set_management_title": "リストセット管理",
        "list_set_instruction": "使用するキーワード／テキストリストを組み合わせて、プロンプト生成の「セット」を定義します。",
        "no_set_yet": "リストセットがまだ作成されていません。新しいセットを作成してください。",
        "available_keyword_lists": "現在利用可能なキーワード／テキストリスト:",
        "id_col": "ID",
        "name_col": "名前",
        "keyword_count_col": "項目数",
        "no_keyword_lists": "キーワード／テキストリストがありません。",
        "set_name_prefix": "セット",
        "set_order_label": "順序 (例: 1 3 2)",
        "invalid_list_num_warning": "リスト番号 **`{}`** は無効です。利用可能なリストIDの範囲 (1から{}) で、かつ存在するリストIDを指定してください。",
        "invalid_input_warning": "**`{}`** は無効な入力です。半角数字とスペースで入力してください。",
        "value_error_warning": "順序は半角数字とスペースで入力してください。",
        "include_in_generation": "このセットを生成に含める",
        "new_set_name_input": "新しいリストセットの名前を入力",
        "create_new_set_button": "新しいセットを追加",
        "set_created_success": "セット **`{}`** が作成されました。順序を指定してください。",
        "enter_set_name": "新しいセット名を入力してください。",
        "prompt_generation_title": "プロンプト生成",
        "generation_mode_label": "プロンプト生成モード",
        "random_gen_mode": "ランダム生成",
        "all_combinations_gen_mode": "総当たり生成 (全組み合わせ)",
        "specific_list_sweep_gen_mode": "特定リスト一巡＋他ランダム生成",
        "num_prompts_to_generate": "各セットで生成するプロンプトの数",
        "all_combinations_info": "「総当たり生成」モードでは、選択されたリストセットのすべての組み合わせが生成されます。生成されるプロンプト数が非常に多くなる可能性があります。",
        "specific_list_sweep_info": "指定されたリストの組み合わせをすべて一巡し、残りのリストはランダムに選択してプロンプトを生成します。**出力されるプロンプトの数は、一巡対象リストの組み合わせ数**となります。",
        "full_sweep_list_ids_title": "総当たり対象リストの指定",
        "full_sweep_list_ids_instruction": "このモードで**すべての組み合わせを一巡させたいリストの番号**を、半角数字とスペース区切りで入力してください。\n例: `1 3` と入力すると、セットに含まれるリストのうちリスト1とリスト3のすべての組み合わせを生成し、残りのリストからはランダムに選択します。",
        "full_sweep_list_num_input": "一巡させたいリスト番号",
        "output_display_method": "プロンプトの表示方法",
        "display_by_set": "セットごとに表示",
        "display_all_together": "すべてまとめて表示",
        "shuffle_results": "生成されたプロンプトをシャッフルして表示",
        "line_spacing_display": "出力行間の表示",
        "line_spacing_single": "一行空きで表示（コピー＆ペースト用）",
        "line_spacing_none": "空白行なしで表示",
        "generate_button": "プロンプト生成",
        "no_keyword_in_list_warning": "セット '{set_name}' のリスト **`{list_num}`** には項目がありません。このリストはスキップされます。",
        "no_full_sweep_list_warning": "セット '{set_name}' について、総当たり対象リストが指定されていないか、無効な番号が含まれています。このセットではランダム生成にフォールバックします。",
        "partial_gen_warning": "セット '{set_name}' の「特定リスト一巡＋他ランダム生成」において、**{target_count}** 個のプロンプトを生成する予定でしたが、生成されたのは **{generated_count}** 個です。ランダム部分の選択肢が少なすぎると、期待通りの数が生成されない場合があります。",
        "generated_from_set": "--- セット: 『**{}**』から生成 ---", # 削除予定
        "generated_prompts_count": "✅ 生成されたプロンプト ({}件):", # 削除予定
        "failed_to_generate_set": "セット '{}' からプロンプトを生成できませんでした。",
        "generated_from_all_sets": "--- すべてのセットから生成されたプロンプト ---", # 削除予定
        "no_prompts_generated": "生成されたプロンプトがありません。",
        "set_data_corrupt_error": "セット '{}' のデータが破損しているか、無効です。セットを再保存してください。",
        "select_at_least_one_set": "プロンプトを生成するには、使用するリストセットを1つ以上選択してください。",
        "prompt_edit_corner": "プロンプト編集コーナー",
        "no_prompts_to_edit": "プロンプトを生成すると、ここで編集できます。",
        "remove_specific_words": "特定のワードを取り除く",
        "remove_words_input_label": "取り除きたいワードをカンマ区切りで入力 (例: masterpiece, best quality)",
        "remove_words_button": "ワードを取り除く",
        "words_removed_success": "指定されたワードを取り除きました。",
        "prompts_for_copy": "コピー用プロンプト",
        "copy_button": "プロンプトをコピー",
        "copy_success": "クリップボードにコピーしました！",
        "set_separator": "--- セット: {set_name} ({count}件のプロンプト) ---",

        "sample_list_name_1": "画質・主題",
        "sample_list_name_2": "髪の特徴",
        "sample_list_name_3": "服装の詳細",
        "sample_list_name_4": "瞳の詳細",
        "sample_list_name_5": "背景シーン",
        "sample_list_content_1": "masterpiece, best quality, ultra detailed\n1girl, solo, cute face",
        "sample_list_content_2": "long blonde hair, twin tails\nshort brown hair, messy\nsilver hair, braided",
        "sample_list_content_3": "japanese school uniform\ntraditional kimono, floral pattern\nmaid outfit, frilly apron",
        "sample_list_content_4": "blue eyes, sparkling\ngreen eyes, narrow pupils\nbrown eyes, gentle gaze",
        "sample_list_content_5": "lush flower field, sunny day\nvibrant city street, night lights\nsecluded beach, sunset view",
        "sample_set_name_0": "キャラクター完全プロンプト",
        "sample_set_name_1": "風景基本",
        "sample_set_name_2": "人物と表情",
    },
    "zh": {
        "title": "图片生成提示词生成器",
        "divider": "---",
        "sidebar_data_management": "数据保存/加载",
        "upload_file": "上传配置文件",
        "upload_success": "配置已成功加载。",
        "upload_invalid_format": "文件格式无效。需要'keyword_lists'和'list_sets'键。",
        "upload_invalid_json": "无效的JSON文件。",
        "upload_invalid_key_type": "JSON文件中的键格式无效（无法转换为整数）。",
        "download_settings_button": "下载当前配置 (JSON)",
        "download_start_json": "开始下载 (JSON)",
        "download_prompts_button": "下载生成的提示词 (TXT)",
        "download_start_txt": "开始下载 (TXT)",
        "no_prompts_yet": "暂未生成提示词。",
        "keyword_list_management_title": "关键词/文本列表输入",
        "keyword_list_instruction": "请在每个列表中输入关键词或文本短语，每行一个。",
        "list_name_prefix": "列表",
        "delete_button": "删除",
        "list_content_label": "内容",
        "upload_txt_to_list": "加载TXT到",
        "add_new_list": "添加新列表",
        "list_set_management_title": "列表集管理",
        "list_set_instruction": "组合关键词/文本列表以定义用于提示词生成的“集”。",
        "no_set_yet": "尚未创建列表集。请创建新集。",
        "available_keyword_lists": "当前可用关键词/文本列表:",
        "id_col": "ID",
        "name_col": "名称",
        "keyword_count_col": "项目数量",
        "no_keyword_lists": "没有可用关键词/文本列表。",
        "set_name_prefix": "集",
        "set_order_label": "顺序 (例如: 1 3 2)",
        "invalid_list_num_warning": "列表编号 **`{}`** 无效。请指定在可用范围 (1到{}) 内且存在的列表ID。",
        "invalid_input_warning": "**`{}`** 是无效输入。请使用半角数字和空格。",
        "value_error_warning": "顺序必须用半角数字和空格输入。",
        "include_in_generation": "包含此集进行生成",
        "new_set_name_input": "输入新列表集名称",
        "create_new_set_button": "添加新集",
        "set_created_success": "集 **`{}`** 已创建。请指定顺序。",
        "enter_set_name": "请输入新集名称。",
        "prompt_generation_title": "提示词生成",
        "generation_mode_label": "提示词生成模式",
        "random_gen_mode": "随机生成",
        "all_combinations_gen_mode": "所有组合生成",
        "specific_list_sweep_gen_mode": "特定列表遍历+其他随机生成",
        "num_prompts_to_generate": "每个集生成的提示词数量",
        "all_combinations_info": "在“所有组合生成”模式下，将生成所选列表集的所有可能组合。这可能会导致生成大量提示词。",
        "specific_list_sweep_info": "此模式遍历指定列表的所有组合，其余列表随机选择生成提示词。**生成的提示词数量将是完全遍历列表的组合数量**。",
        "full_sweep_list_ids_title": "指定完全遍历列表",
        "full_sweep_list_ids_instruction": "输入您想要**完全遍历所有组合的列表编号**，用半角空格分隔。\n例如: 输入`1 3`将生成集合中列表1和列表3的所有组合，并从其他列表中随机选择。",
        "full_sweep_list_num_input": "完全遍历列表编号",
        "output_display_method": "提示词显示方式",
        "display_by_set": "按集显示",
        "display_all_together": "全部一起显示",
        "shuffle_results": "打乱生成的提示词显示顺序",
        "line_spacing_display": "输出行间距",
        "line_spacing_single": "一行空行显示（用于复制/粘贴）",
        "line_spacing_none": "无空行显示",
        "generate_button": "生成提示词",
        "no_keyword_in_list_warning": "集 '{set_name}' 中的列表 **`{list_num}`** 没有项目。此列表将被跳过。",
        "no_full_sweep_list_warning": "对于集 '{set_name}'，未指定完全遍历列表或包含无效数字。将回退到随机生成此集。",
        "partial_gen_warning": "对于集 '{set_name}'，“特定列表遍历+其他随机生成”模式原计划生成 **{target_count}** 个提示词，但只生成了 **{generated_count}** 个。如果随机选择的范围太有限，可能会发生这种情况。",
        "generated_from_set": "--- 从集: 『**{}**』生成 ---", # 削除予定
        "generated_prompts_count": "✅ 生成的提示词 ({}项):", # 削除予定
        "failed_to_generate_set": "未能从集 '{}' 生成提示词。",
        "generated_from_all_sets": "--- 从所有集生成的提示词 ---", # 削除予定
        "no_prompts_generated": "没有生成提示词。",
        "set_data_corrupt_error": "集 '{}' 数据损坏或无效。请重新保存此集。",
        "select_at_least_one_set": "请至少选择一个列表集来生成提示词。",
        "prompt_edit_corner": "提示词编辑区",
        "no_prompts_to_edit": "生成提示词后可在此处编辑。",
        "remove_specific_words": "移除特定词语",
        "remove_words_input_label": "输入要移除的词语，用逗号分隔 (例如: masterpiece, best quality)",
        "remove_words_button": "移除词语",
        "words_removed_success": "已移除指定词语。",
        "prompts_for_copy": "复制用提示词",
        "copy_button": "复制提示词",
        "copy_success": "已复制到剪贴板！",
        "set_separator": "--- 集: {set_name} ({count}项提示词) ---",

        "sample_list_name_1": "画質",
        "sample_list_name_2": "髪の特徴",
        "sample_list_name_3": "服装の詳細",
        "sample_list_name_4": "瞳の詳細",
        "sample_list_name_5": "背景シーン",
        "sample_list_content_1": "masterpiece, best quality, ultra detailed\n1girl, solo, cute face",
        "sample_list_content_2": "long blonde hair, twin tails\nshort brown hair, messy\nsilver hair, braided",
        "sample_list_content_3": "japanese school uniform\ntraditional kimono, floral pattern\nmaid outfit, frilly apron",
        "sample_list_content_4": "blue eyes, sparkling\ngreen eyes, narrow pupils\nbrown eyes, gentle gaze",
        "sample_list_content_5": "lush flower field, sunny day\nvibrant city street, night lights\nsecluded beach, sunset view",
        "sample_set_name_0": "キャラクター完全プロンプト",
        "sample_set_name_1": "風景基本",
        "sample_set_name_2": "人物と表情",
    },
    "zh": {
        "title": "图片生成提示词生成器",
        "divider": "---",
        "sidebar_data_management": "数据保存/加载",
        "upload_file": "上传配置文件",
        "upload_success": "配置已成功加载。",
        "upload_invalid_format": "文件格式无效。需要'keyword_lists'和'list_sets'键。",
        "upload_invalid_json": "无效的JSON文件。",
        "upload_invalid_key_type": "JSON文件中的键格式无效（无法转换为整数）。",
        "download_settings_button": "下载当前配置 (JSON)",
        "download_start_json": "开始下载 (JSON)",
        "download_prompts_button": "下载生成的提示词 (TXT)",
        "download_start_txt": "开始下载 (TXT)",
        "no_prompts_yet": "暂未生成提示词。",
        "keyword_list_management_title": "关键词/文本列表输入",
        "keyword_list_instruction": "请在每个列表中输入关键词或文本短语，每行一个。",
        "list_name_prefix": "列表",
        "delete_button": "删除",
        "list_content_label": "内容",
        "upload_txt_to_list": "加载TXT到",
        "add_new_list": "添加新列表",
        "list_set_management_title": "列表集管理",
        "list_set_instruction": "组合关键词/文本列表以定义用于提示词生成的“集”。",
        "no_set_yet": "尚未创建列表集。请创建新集。",
        "available_keyword_lists": "当前可用关键词/文本列表:",
        "id_col": "ID",
        "name_col": "名称",
        "keyword_count_col": "项目数量",
        "no_keyword_lists": "没有可用关键词/文本列表。",
        "set_name_prefix": "集",
        "set_order_label": "顺序 (例如: 1 3 2)",
        "invalid_list_num_warning": "列表编号 **`{}`** 无效。请指定在可用范围 (1到{}) 内且存在的列表ID。",
        "invalid_input_warning": "**`{}`** 是无效输入。请使用半角数字和空格。",
        "value_error_warning": "顺序必须用半角数字和空格输入。",
        "include_in_generation": "包含此集进行生成",
        "new_set_name_input": "输入新列表集名称",
        "create_new_set_button": "添加新集",
        "set_created_success": "集 **`{}`** 已创建。请指定顺序。",
        "enter_set_name": "请输入新集名称。",
        "prompt_generation_title": "提示词生成",
        "generation_mode_label": "提示词生成模式",
        "random_gen_mode": "随机生成",
        "all_combinations_gen_mode": "所有组合生成",
        "specific_list_sweep_gen_mode": "特定列表遍历+其他随机生成",
        "num_prompts_to_generate": "每个集生成的提示词数量",
        "all_combinations_info": "在“所有组合生成”模式下，将生成所选列表集的所有可能组合。这可能会导致生成大量提示词。",
        "specific_list_sweep_info": "此模式遍历指定列表的所有组合，其余列表随机选择生成提示词。**生成的提示词数量将是完全遍历列表的组合数量**。",
        "full_sweep_list_ids_title": "指定完全遍历列表",
        "full_sweep_list_ids_instruction": "输入您想要**完全遍历所有组合的列表编号**，用半角空格分隔。\n例如: 输入`1 3`将生成集合中列表1和列表3的所有组合，并从其他列表中随机选择。",
        "full_sweep_list_num_input": "完全遍历列表编号",
        "output_display_method": "提示词显示方式",
        "display_by_set": "按集显示",
        "display_all_together": "全部一起显示",
        "shuffle_results": "打乱生成的提示词显示顺序",
        "line_spacing_display": "输出行间距",
        "line_spacing_single": "一行空行显示（用于复制/粘贴）",
        "line_spacing_none": "无空行显示",
        "generate_button": "生成提示词",
        "no_keyword_in_list_warning": "集 '{set_name}' 中的列表 **`{list_num}`** 没有项目。此列表将被跳过。",
        "no_full_sweep_list_warning": "对于集 '{set_name}'，未指定完全遍历列表或包含无效数字。将回退到随机生成此集。",
        "partial_gen_warning": "对于集 '{set_name}'，“特定列表遍历+其他随机生成”模式原计划生成 **{target_count}** 个提示词，但只生成了 **{generated_count}** 个。如果随机选择的范围太有限，可能会发生这种情况。",
        "generated_from_set": "--- 从集: 『**{}**』生成 ---", # 削除予定
        "generated_prompts_count": "✅ 生成的提示词 ({}项):", # 削除予定
        "failed_to_generate_set": "未能从集 '{}' 生成提示词。",
        "generated_from_all_sets": "--- 从所有集生成的提示词 ---", # 削除予定
        "no_prompts_generated": "没有生成提示词。",
        "set_data_corrupt_error": "集 '{}' 数据损坏或无效。请重新保存此集。",
        "select_at_least_one_set": "请至少选择一个列表集来生成提示词。",
        "prompt_edit_corner": "提示词编辑区",
        "no_prompts_to_edit": "生成提示词后可在此处编辑。",
        "remove_specific_words": "移除特定词语",
        "remove_words_input_label": "输入要移除的词语，用逗号分隔 (例如: masterpiece, best quality)",
        "remove_words_button": "移除词语",
        "words_removed_success": "已移除指定词语。",
        "prompts_for_copy": "复制用提示词",
        "copy_button": "复制提示词",
        "copy_success": "已复制到剪贴板！",
        "set_separator": "--- 集: {set_name} ({count}项提示词) ---",

        "sample_list_name_1": "画質",
        "sample_list_name_2": "发型描述",
        "sample_list_name_3": "服装细节",
        "sample_list_name_4": "眼睛细节",
        "sample_list_name_5": "背景场景",
        "sample_list_content_1": "masterpiece, best quality, ultra detailed\n1girl, solo, cute face",
        "sample_list_content_2": "long blonde hair, twin tails\nshort brown hair, messy\nsilver hair, braided",
        "sample_list_content_3": "japanese school uniform\ntraditional kimono, floral pattern\nmaid outfit, frilly apron",
        "sample_list_content_4": "blue eyes, sparkling\ngreen eyes, narrow pupils\nbrown eyes, gentle gaze",
        "sample_list_content_5": "lush flower field, sunny day\nvibrant city street, night lights\nsecluded beach, sunset view",
        "sample_set_name_0": "角色完整提示词",
        "sample_set_name_1": "风景基础",
        "sample_set_name_2": "人物与表情",
    },
    "fr": {
        "title": "Générateur de Prompts d'Images",
        "divider": "---",
        "sidebar_data_management": "Sauvegarder/Charger les données",
        "upload_file": "Importer le fichier de paramètres",
        "upload_success": "Paramètres chargés avec succès.",
        "upload_invalid_format": "Format de fichier invalide. Les clés 'keyword_lists' et 'list_sets' sont requises.",
        "upload_invalid_json": "Fichier JSON invalide.",
        "upload_invalid_key_type": "Format de clé invalide dans le fichier JSON (impossible de convertir en entier).",
        "download_settings_button": "Télécharger les paramètres actuels (JSON)",
        "download_start_json": "Démarrer le téléchargement (JSON)",
        "download_prompts_button": "Télécharger les prompts générés (TXT)",
        "download_start_txt": "Démarrer le téléchargement (TXT)",
        "no_prompts_yet": "Aucun prompt généré pour l'instant.",
        "keyword_list_management_title": "Saisie de la liste de mots-clés/texte",
        "keyword_list_instruction": "Saisissez les mots-clés ou les phrases textuelles pour chaque liste, une par ligne.",
        "list_name_prefix": "Liste",
        "delete_button": "Supprimer",
        "list_content_label": "Contenu",
        "upload_txt_to_list": "Charger TXT dans",
        "add_new_list": "Ajouter une nouvelle liste",
        "list_set_management_title": "Gestion des ensembles de listes",
        "list_set_instruction": "Combinez les listes de mots-clés/texte pour définir des 'ensembles' pour la génération de prompts.",
        "no_set_yet": "Aucun ensemble de listes n'a encore été créé. Veuillez créer un nouvel ensemble.",
        "available_keyword_lists": "Listes de mots-clés/texte actuellement disponibles :",
        "id_col": "ID",
        "name_col": "Nom",
        "keyword_count_col": "Nombre d'éléments",
        "no_keyword_lists": "Aucune liste de mots-clés/texte disponible.",
        "set_name_prefix": "Ensemble",
        "set_order_label": "Ordre (ex: 1 3 2)",
        "invalid_list_num_warning": "Le numéro de liste **`{}`** est invalide. Veuillez spécifier un ID de liste dans la plage disponible (1 à {}) et qui existe.",
        "invalid_input_warning": "**`{}`** est une saisie invalide. Veuillez utiliser des chiffres et des espaces en demi-largeur.",
        "value_error_warning": "L'ordre doit être saisi avec des chiffres et des espaces en demi-largeur.",
        "include_in_generation": "Inclure cet ensemble dans la génération",
        "new_set_name_input": "Saisir le nom du nouvel ensemble de listes",
        "create_new_set_button": "Ajouter un nouvel ensemble",
        "set_created_success": "Ensemble **`{}`** créé. Veuillez spécifier l'ordre.",
        "enter_set_name": "Veuillez saisir un nom pour le nouvel ensemble.",
        "prompt_generation_title": "Génération de Prompts",
        "generation_mode_label": "Mode de génération de prompts",
        "random_gen_mode": "Génération aléatoire",
        "all_combinations_gen_mode": "Génération de toutes les combinaisons",
        "specific_list_sweep_gen_mode": "Parcours de liste spécifique + autre génération aléatoire",
        "num_prompts_to_generate": "Nombre de prompts à générer par ensemble",
        "all_combinations_info": "En mode 'Toutes les combinaisons', toutes les combinaisons possibles de l'ensemble de listes sélectionné seront générées. Cela peut entraîner un très grand nombre de prompts.",
        "specific_list_sweep_info": "Ce mode génère toutes les combinaisons des listes spécifiées, les autres listes étant choisies aléatoirement. Le **nombre de prompts générés sera le nombre de combinaisons des listes de balayage complet**.",
        "full_sweep_list_ids_title": "Spécifier les listes de balayage complet",
        "full_sweep_list_ids_instruction": "Saisissez les **numéros des listes pour lesquelles vous souhaitez balayer toutes les combinaisons**, séparés par des espaces.\nEx: `1 3` générera toutes les combinaisons de la Liste 1 et de la Liste 3 de l'ensemble, et choisira aléatoirement dans les autres listes.",
        "full_sweep_list_num_input": "Numéros de liste pour le balayage complet",
        "output_display_method": "Méthode d'affichage des prompts",
        "display_by_set": "Afficher par ensemble",
        "display_all_together": "Afficher tout ensemble",
        "shuffle_results": "Mélanger les prompts générés pour l'affichage",
        "line_spacing_display": "Espacement des lignes de sortie",
        "line_spacing_single": "Afficher avec une ligne vide (pour copier/coller)",
        "line_spacing_none": "Afficher sans lignes vides",
        "generate_button": "Générer les Prompts",
        "no_keyword_in_list_warning": "La liste **`{list_num}`** de l'ensemble '{set_name}' n'a pas d'éléments. Cette liste sera ignorée.",
        "no_full_sweep_list_warning": "Pour l'ensemble '{set_name}', aucune liste de balayage complet n'a été spécifiée ou des numéros invalides ont été inclus. Retour à la génération aléatoire pour cet ensemble.",
        "partial_gen_warning": "Pour l'ensemble '{set_name}', la 'Génération spécifique + autre aléatoire' devait générer **{target_count}** prompts, mais seulement **{generated_count}** ont été générés. Cela peut arriver si les choix aléatoires sont trop limités.",
        "generated_from_set": "--- Généré à partir de l'ensemble : 『**{}**』 ---", # 削除予定
        "generated_prompts_count": "✅ Prompts générés ({} éléments) :", # 削除予定
        "failed_to_generate_set": "Échec de la génération des prompts de l'ensemble '{}'.",
        "generated_from_all_sets": "--- Prompts générés de tous les ensembles ---", # 削除予定
        "no_prompts_generated": "Aucun prompt généré.",
        "set_data_corrupt_error": "Les données de l'ensemble '{}' sont corrompues ou invalides. Veuillez enregistrer à nouveau l'ensemble.",
        "select_at_least_one_set": "Veuillez sélectionner au moins un ensemble de listes pour générer des prompts.",
        "prompt_edit_corner": "Coin d'édition de prompts",
        "no_prompts_to_edit": "Générez des prompts pour les éditer ici.",
        "remove_specific_words": "Supprimer des mots spécifiques",
        "remove_words_input_label": "Saisir les mots à supprimer, séparés par des virgules (ex: masterpiece, best quality)",
        "remove_words_button": "Supprimer les mots",
        "words_removed_success": "Mots spécifiés supprimés.",
        "prompts_for_copy": "Prompts à copier",
        "copy_button": "Copier les prompts",
        "copy_success": "Copié dans le presse-papiers !",
        "set_separator": "--- ENSEMBLE: {set_name} ({count} prompts) ---",

        "sample_list_name_1": "Qualité",
        "sample_list_name_2": "Description des cheveux",
        "sample_list_name_3": "Détails de la tenue",
        "sample_list_name_4": "Détails des yeux",
        "sample_list_name_5": "Scène d'arrière-plan",
        "sample_list_content_1": "masterpiece, best quality, ultra detailed\n1girl, solo, cute face",
        "sample_list_content_2": "long blonde hair, twin tails\nshort brown hair, messy\nsilver hair, braided",
        "sample_list_content_3": "japanese school uniform\ntraditional kimono, floral pattern\nmaid outfit, frilly apron",
        "sample_list_content_4": "blue eyes, sparkling\ngreen eyes, narrow pupils\nbrown eyes, gentle gaze",
        "sample_list_content_5": "lush flower field, sunny day\nvibrant city street, night lights\nsecluded beach, sunset view",
        "sample_set_name_0": "Prompt complet du personnage",
        "sample_set_name_1": "Base de paysage",
        "sample_set_name_2": "Personne & Expression",
    },
    "es": {
        "title": "Generador de Prompts de Imágenes",
        "divider": "---",
        "sidebar_data_management": "Guardar/Cargar datos",
        "upload_file": "Subir archivo de configuración",
        "upload_success": "Configuración cargada exitosamente.",
        "upload_invalid_format": "Formato de archivo inválido. Se requieren las claves 'keyword_lists' y 'list_sets'.",
        "upload_invalid_json": "Archivo JSON inválido.",
        "upload_invalid_key_type": "Formato de clave inválido en el archivo JSON (no se pudo convertir a entero).",
        "download_settings_button": "Descargar configuración actual (JSON)",
        "download_start_json": "Iniciar descarga (JSON)",
        "download_prompts_button": "Descargar prompts generados (TXT)",
        "download_start_txt": "Iniciar descarga (TXT)",
        "no_prompts_yet": "Aún no se han generado prompts.",
        "keyword_list_management_title": "Entrada de lista de palabras clave/texto",
        "keyword_list_instruction": "Ingrese las palabras clave o frases de texto para cada lista, una por línea.",
        "list_name_prefix": "Lista",
        "delete_button": "Eliminar",
        "list_content_label": "Contenido",
        "upload_txt_to_list": "Cargar TXT a",
        "add_new_list": "Agregar nueva lista",
        "list_set_management_title": "Gestión de conjuntos de listas",
        "list_set_instruction": "Combine las listas de palabras clave/texto para definir 'conjuntos' para la generación de prompts.",
        "no_set_yet": "Aún no se han creado conjuntos de listas. Por favor, cree un nuevo conjunto.",
        "available_keyword_lists": "Listas de palabras clave/texto disponibles actualmente:",
        "id_col": "ID",
        "name_col": "Nombre",
        "keyword_count_col": "Conteo de elementos",
        "no_keyword_lists": "No hay listas de palabras clave/texto disponibles.",
        "set_name_prefix": "Conjunto",
        "set_order_label": "Orden (ej: 1 3 2)",
        "invalid_list_num_warning": "El número de lista **`{}`** es inválido. Por favor, especifique un ID de lista dentro del rango disponible (1 a {}) y que exista.",
        "invalid_input_warning": "**`{}`** es una entrada inválida. Por favor, use números de ancho medio y espacios.",
        "value_error_warning": "El orden debe ingresarse con números de ancho medio y espacios.",
        "include_in_generation": "Incluir este conjunto en la generación",
        "new_set_name_input": "Ingresar nombre para nuevo conjunto de listas",
        "create_new_set_button": "Agregar nuevo conjunto",
        "set_created_success": "Conjunto **`{}`** creado. Por favor, especifique el orden.",
        "enter_set_name": "Por favor, ingrese un nombre para el nuevo conjunto.",
        "prompt_generation_title": "Generación de Prompts",
        "generation_mode_label": "Modo de generación de prompts",
        "random_gen_mode": "Generación aleatoria",
        "all_combinations_gen_mode": "Generación de todas las combinaciones",
        "specific_list_sweep_gen_mode": "Barrido de lista específica + otra generación aleatoria",
        "num_prompts_to_generate": "Número de prompts a generar por conjunto",
        "all_combinations_info": "En el modo 'Todas las combinaciones', se generarán todas las combinaciones posibles del conjunto de listas seleccionado. Esto puede resultar en un número muy grande de prompts.",
        "specific_list_sweep_info": "Este modo genera todas las combinaciones de las listas especificadas, con otras listas elegidas al azar. El **número de prompts generados será el número de combinaciones de las listas de barrido completo**.",
        "full_sweep_list_ids_title": "Especificar listas de barrido completo",
        "full_sweep_list_ids_instruction": "Ingrese los **números de las listas para las cuales desea realizar un barrido completo de todas las combinaciones**, separados por espacios de ancho medio.\nEj: `1 3` generará todas las combinaciones de la Lista 1 y la Lista 3 del conjunto, y elegirá aleatoriamente de otras listas.",
        "full_sweep_list_num_input": "Números de lista para barrido completo",
        "output_display_method": "Método de visualización de prompts",
        "display_by_set": "Mostrar por conjunto",
        "display_all_together": "Mostrar todo junto",
        "shuffle_results": "Mezclar prompts generados para mostrar",
        "line_spacing_display": "Espaciado de línea de salida",
        "line_spacing_single": "Mostrar con una línea vacía (para copiar/pegar)",
        "line_spacing_none": "Mostrar sin líneas vacías",
        "generate_button": "Generar Prompts",
        "no_keyword_in_list_warning": "La lista **`{list_num}`** en el conjunto '{set_name}' no tiene elementos. Esta lista se omitirá.",
        "no_full_sweep_list_warning": "Para el conjunto '{set_name}' no se especificaron listas de barrido completo o se incluyeron números inválidos. Se volverá a la generación aleatoria para este conjunto.",
        "partial_gen_warning": "Para el conjunto '{set_name}', se esperaba que 'Barrido de lista específica + otra generación aleatoria' generara **{target_count}** prompts, pero solo se generaron **{generated_count}**. Esto puede ocurrir si las opciones aleatorias son demasiado limitadas.",
        "generated_from_set": "--- Generado desde el conjunto: 『**{}**』 ---", # 削除予定
        "generated_prompts_count": "✅ Prompts generados ({} elementos):", # 削除予定
        "failed_to_generate_set": "No se pudieron generar prompts desde el conjunto '{}'.",
        "generated_from_all_sets": "--- Prompts generados de todos los conjuntos ---", # 削除予定
        "no_prompts_generated": "No se generaron prompts.",
        "set_data_corrupt_error": "Los datos del conjunto '{}' están corruptos o no son válidos. Por favor, vuelva a guardar el conjunto.",
        "select_at_least_one_set": "Por favor, seleccione al menos un conjunto de listas para generar prompts.",
        "prompt_edit_corner": "Esquina de edición de prompts",
        "no_prompts_to_edit": "Genere prompts para editarlos aquí.",
        "remove_specific_words": "Eliminar palabras específicas",
        "remove_words_input_label": "Ingrese palabras a eliminar, separadas por comas (ej: masterpiece, best quality)",
        "remove_words_button": "Eliminar palabras",
        "words_removed_success": "Palabras especificadas eliminadas.",
        "prompts_for_copy": "Prompts para copiar",
        "copy_button": "Copiar prompts",
        "copy_success": "Copiado al portapapeles.",
        "set_separator": "--- CONJUNTO: {set_name} ({count} prompts) ---",

        "sample_list_name_1": "Calidad",
        "sample_list_name_2": "Descripción del cabello",
        "sample_list_name_3": "Detalles del atuendo",
        "sample_list_name_4": "Detalles de los ojos",
        "sample_list_name_5": "Escena de fondo",
        "sample_list_content_1": "masterpiece, best quality, ultra detailed\n1girl, solo, cute face",
        "sample_list_content_2": "long blonde hair, twin tails\nshort brown hair, messy\nsilver hair, braided",
        "sample_list_content_3": "japanese school uniform\ntraditional kimono, floral pattern\nmaid outfit, frilly apron",
        "sample_list_content_4": "blue eyes, sparkling\ngreen eyes, narrow pupils\nbrown eyes, gentle gaze",
        "sample_list_content_5": "lush flower field, sunny day\nvibrant city street, night lights\nsecluded beach, sunset view",
        "sample_set_name_0": "Prompt completo del personaje",
        "sample_set_name_1": "Base de paisaje",
        "sample_set_name_2": "Persona y Expresión",
    }
}

# --- Session State for Language ---
# 初期言語設定（デフォルトは英語）
if 'current_lang' not in st.session_state:
    st.session_state.current_lang = "en"

# 言語選択のUIをサイドバーに追加
st.sidebar.header(f"Language / 言語 / 语言 / Langue / Idioma")
selected_lang_code = st.sidebar.radio(
    f"Select Language / 言語を選択 / 选择语言 / Choisir la langue / Seleccionar idioma",
    options=["en", "ja", "zh", "fr", "es"],
    format_func=lambda x: {"en": "English", "ja": "日本語", "zh": "中文", "fr": "Français", "es": "Español"}[x],
    key="language_selector"
)
if selected_lang_code != st.session_state.current_lang:
    st.session_state.current_lang = selected_lang_code
    # 言語変更時に初期データを再生成するため、'initialized' フラグをリセット
    st.session_state.initialized = False
    st.rerun()

# 現在の言語に対応するテキストを取得するヘルパー関数
def get_text(key):
    return LANGUAGES[st.session_state.current_lang].get(key, key) # キーが見つからない場合はキー自体を返す

# --- Helper Functions (変更なし) ---
def parse_list(raw_text):
    """テキストエリアの文字列をリスト形式に変換する"""
    return [line.strip() for line in raw_text.strip().split("\n") if line.strip()]

def generate_unique_combinations_random(all_lists_for_generation, num_results):
    """選択されたリストと順序に基づいてユニークなプロンプトをランダムに生成する"""
    combinations = set()

    if not all_lists_for_generation:
        st.warning(get_text("no_keyword_in_list_warning").format(set_name="", list_num=""))
        return []

    for lst_content in all_lists_for_generation:
        if not lst_content:
            st.warning(get_text("no_keyword_in_list_warning").format(set_name="", list_num=""))
            return []

    max_possible_combinations = 1
    for lst_content in all_lists_for_generation:
        max_possible_combinations *= len(lst_content)

    if num_results > max_possible_combinations:
        num_results = max_possible_combinations
        if num_results == 0:
            st.error(get_text("no_prompts_generated"))
            return []

    attempts = 0
    max_attempts_multiplier = 50
    while len(combinations) < num_results and attempts < num_results * max_attempts_multiplier:
        try:
            combo = tuple(random.choice(lst_content) for lst_content in all_lists_for_generation)
            combinations.add(combo)
        except IndexError:
            st.error(get_text("no_keyword_in_list_warning").format(set_name="", list_num=""))
            return []
        attempts += 1

    if len(combinations) < num_results:
        st.warning(get_text("partial_gen_warning").format(set_name="", target_count=num_results, generated_count=len(combinations)))
    return [", ".join(combo) for combination_tuple in combinations]

def generate_all_combinations(all_lists_for_generation):
    """すべての可能な組み合わせを生成する (総当たり)"""
    if not all_lists_for_generation:
        st.warning(get_text("no_keyword_in_list_warning").format(set_name="", list_num=""))
        return []

    for lst_content in all_lists_for_generation:
        if not lst_content:
            st.warning(get_text("no_keyword_in_list_warning").format(set_name="", list_num=""))
            return []

    try:
        all_combos = list(itertools.product(*all_lists_for_generation))
        return [", ".join(combo) for combo in all_combos]
    except Exception as e:
        st.error(f"{get_text('failed_to_generate_set')}: {e}")
        return []


# --- Session State Initialization ---
if 'initialized' not in st.session_state or not st.session_state.initialized:
    st.session_state.keyword_lists = {
        1: {"content": LANGUAGES["en"]["sample_list_content_1"], "display_name": get_text("sample_list_name_1")},
        2: {"content": LANGUAGES["en"]["sample_list_content_2"], "display_name": get_text("sample_list_name_2")},
        3: {"content": LANGUAGES["en"]["sample_list_content_3"], "display_name": get_text("sample_list_name_3")},
        4: {"content": LANGUAGES["en"]["sample_list_content_4"], "display_name": get_text("sample_list_name_4")},
        5: {"content": LANGUAGES["en"]["sample_list_content_5"], "display_name": get_text("sample_list_name_5")},
    }
    st.session_state.next_list_id = max(st.session_state.keyword_lists.keys()) + 1 if st.session_state.keyword_lists else 1
    st.session_state.list_sets = {
        0: {"display_name": get_text("sample_set_name_0"), "order": [1, 2, 3, 4, 5]},
        1: {"display_name": get_text("sample_set_name_1"), "order": [1, 5]},
        2: {"display_name": get_text("sample_set_name_2"), "order": [1, 2, 4]}
    }
    st.session_state.next_set_id = max(st.session_state.list_sets.keys()) + 1 if st.session_state.list_sets else 0
    st.session_state.selected_set_ids_for_generation = []
    st.session_state.generated_prompts = [] # これは常にフラットな全プロンプト
    st.session_state.generated_prompts_by_set = {} # セットごとのプロンプトを保持する新しいセッションステート
    st.session_state.prompts_for_copy_area = ""
    st.session_state.initialized = True


# --- データ保存・読み込み機能 ---
st.sidebar.header(get_text("sidebar_data_management"))

uploaded_file = st.sidebar.file_uploader(get_text("upload_file"), type="json")
if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        if "keyword_lists" in data and "list_sets" in data:
            loaded_keyword_lists = {int(k): v for k, v in data["keyword_lists"].items()}
            loaded_list_sets = {}
            for set_id_str, set_info in data["list_sets"].items():
                loaded_list_sets[int(set_id_str)] = {
                    "display_name": set_info["display_name"],
                    "order": [int(o) for o in set_info["order"]]
                }
            st.session_state.keyword_lists = loaded_keyword_lists
            st.session_state.list_sets = loaded_list_sets
            st.session_state.next_list_id = max(st.session_state.keyword_lists.keys()) + 1 if st.session_state.keyword_lists else 1
            st.session_state.next_set_id = max(st.session_state.list_sets.keys()) + 1 if st.session_state.list_sets else 0
            st.session_state.selected_set_ids_for_generation = []
            st.session_state.generated_prompts = []
            st.session_state.generated_prompts_by_set = {} # リセット
            st.session_state.prompts_for_copy_area = ""
            st.sidebar.success(get_text("upload_success"))
            st.rerun()
        else:
            st.sidebar.error(get_text("upload_invalid_format"))
    except json.JSONDecodeError:
        st.sidebar.error(get_text("upload_invalid_json"))
    except ValueError:
        st.sidebar.error(get_text("upload_invalid_key_type"))

if st.sidebar.button(get_text("download_settings_button")):
    current_data = {
        "keyword_lists": {str(k): v for k, v in st.session_state.keyword_lists.items()},
        "list_sets": {str(k): {"display_name": v["display_name"], "order": v["order"]} for k, v in st.session_state.list_sets.items()},
    }
    json_data = json.dumps(current_data, indent=4, ensure_ascii=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"prompt_generator_settings_{timestamp}.json"
    st.sidebar.download_button(
        label=get_text("download_start_json"),
        data=json_data,
        file_name=file_name,
        mime="application/json"
    )

if st.sidebar.button(get_text("download_prompts_button"), disabled=not st.session_state.generated_prompts):
    if st.session_state.generated_prompts:
        prompts_text = st.session_state.prompts_for_copy_area
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"generated_prompts_{timestamp}.txt"
        st.sidebar.download_button(
            label=get_text("download_start_txt"),
            data=prompts_text,
            file_name=file_name,
            mime="text/plain"
        )
    else:
        st.sidebar.warning(get_text("no_prompts_yet"))

st.markdown(get_text("divider"))


# --- Keyword/Text List Management ---
st.markdown(f"### {get_text('keyword_list_management_title')}")
st.markdown(get_text("keyword_list_instruction"))

lists_to_delete = []
sorted_list_ids = sorted(st.session_state.keyword_lists.keys())

for list_id in sorted_list_ids:
    list_data = st.session_state.keyword_lists[list_id]

    st.markdown(f"##### {get_text('list_name_prefix')} {list_id}")
    col_name, col_delete = st.columns([0.9, 0.1])

    with col_name:
        current_display_name = list_data.get("display_name", f"{get_text('list_name_prefix')}{list_id}")
        new_display_name = st.text_input(f"{get_text('list_name_prefix')} {list_id} {get_text('name_col')}", value=current_display_name, key=f"list_display_name_input_{list_id}")
        if new_display_name != current_display_name:
            st.session_state.keyword_lists[list_id]["display_name"] = new_display_name

    with col_delete:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(get_text("delete_button"), key=f"delete_list_{list_id}"):
            lists_to_delete.append(list_id)

    col_content, col_upload = st.columns([0.9, 0.1])
    with col_content:
        current_content = list_data["content"]
        new_content = st.text_area(f"{get_text('list_name_prefix')} {list_id} {get_text('list_content_label')}", current_content, height=100, key=f"list_content_{list_id}")
        st.session_state.keyword_lists[list_id]["content"] = new_content
    with col_upload:
        uploaded_txt_file = st.file_uploader(f"{get_text('list_name_prefix')} {list_id} {get_text('upload_txt_to_list')}", type="txt", key=f"upload_txt_list_{list_id}")
        if uploaded_txt_file is not None:
            string_data = uploaded_txt_file.read().decode("utf-8")
            st.session_state.keyword_lists[list_id]["content"] = string_data
            st.rerun()

    st.markdown(get_text("divider"))

if lists_to_delete:
    for list_id_to_delete in lists_to_delete:
        del st.session_state.keyword_lists[list_id_to_delete]

    new_keyword_lists = {}
    old_to_new_id_map = {}
    current_new_id = 1
    for old_id in sorted([int(k) for k in st.session_state.keyword_lists.keys()]):
        new_keyword_lists[current_new_id] = st.session_state.keyword_lists[old_id]
        old_to_new_id_map[old_id] = current_new_id
        current_new_id += 1

    st.session_state.keyword_lists = new_keyword_lists
    st.session_state.next_list_id = current_new_id

    for set_id in st.session_state.list_sets:
        updated_order = []
        for old_list_id_in_order in st.session_state.list_sets[set_id]["order"]:
            if old_list_id_in_order in old_to_new_id_map:
                updated_order.append(old_to_new_id_map[old_list_id_in_order])
        st.session_state.list_sets[set_id]["order"] = updated_order

    st.rerun()

if st.button(get_text("add_new_list")):
    st.session_state.keyword_lists[st.session_state.next_list_id] = {"content": "", "display_name": f"{get_text('list_name_prefix')}{st.session_state.next_list_id}"}
    st.session_state.next_list_id += 1
    st.rerun()


# --- List Set Management ---
st.markdown(f"### {get_text('list_set_management_title')}")
st.markdown(get_text("list_set_instruction"))

set_ids_to_delete = []
set_ids_sorted = sorted(st.session_state.list_sets.keys())

if not set_ids_sorted:
    st.info(get_text("no_set_yet"))

st.markdown(f"#### **{get_text('available_keyword_lists')}**")
if st.session_state.keyword_lists:
    available_lists_df = pd.DataFrame([
        {get_text("id_col"): lid, get_text("name_col"): st.session_state.keyword_lists[lid]["display_name"], get_text("keyword_count_col"): len(parse_list(st.session_state.keyword_lists[lid]["content"]))}
        for lid in sorted(st.session_state.keyword_lists.keys())
    ])
    st.dataframe(available_lists_df, hide_index=True)
else:
    st.info(get_text("no_keyword_lists"))
st.markdown(get_text("divider"))


for set_id in set_ids_sorted:
    set_data = st.session_state.list_sets[set_id]

    st.markdown(f"##### {get_text('set_name_prefix')} {set_id + 1}")

    col_name_set, col_delete_set = st.columns([0.9, 0.1])
    with col_name_set:
        current_display_name = set_data.get("display_name", "")
        new_display_name = st.text_input(f"{get_text('set_name_prefix')} {set_id + 1} {get_text('name_col')}", value=current_display_name, key=f"set_display_name_input_{set_id}")
        if new_display_name != current_display_name:
            st.session_state.list_sets[set_id]["display_name"] = new_display_name
    with col_delete_set:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(get_text("delete_button"), key=f"delete_set_{set_id}"):
            set_ids_to_delete.append(set_id)

    current_order_str = " ".join(map(str, set_data["order"]))
    new_order_str = st.text_input(f"{get_text('set_name_prefix')} {set_id + 1} {get_text('set_order_label')}", value=current_order_str, key=f"set_order_input_{set_id}")

    ordered_list_numbers_for_set = []
    invalid_numbers_found_in_order = False
    max_available_list_id = max(st.session_state.keyword_lists.keys()) if st.session_state.keyword_lists else 0

    try:
        if new_order_str:
            temp_order = []
            for x in new_order_str.split():
                if x.isdigit():
                    num = int(x)
                    if 1 <= num <= max_available_list_id and num in st.session_state.keyword_lists:
                        temp_order.append(num)
                    else:
                        st.warning(get_text("invalid_list_num_warning").format(x, max_available_list_id), key=f"invalid_num_warning_{set_id}_{x}")
                        invalid_numbers_found_in_order = True
                else:
                    st.warning(get_text("invalid_input_warning").format(x), key=f"invalid_char_warning_{set_id}_{x}")
                    invalid_numbers_found_in_order = True
            ordered_list_numbers_for_set = temp_order
    except ValueError:
        st.warning(get_text("value_error_warning"), key=f"value_error_warning_{set_id}")
        ordered_list_numbers_for_set = []

    if ordered_list_numbers_for_set != set_data["order"] and not invalid_numbers_found_in_order:
        st.session_state.list_sets[set_id]["order"] = ordered_list_numbers_for_set
        st.rerun()

    is_selected = st.checkbox(get_text("include_in_generation"), value=(set_id in st.session_state.selected_set_ids_for_generation), key=f"select_set_for_gen_{set_id}")
    if is_selected and set_id not in st.session_state.selected_set_ids_for_generation:
        st.session_state.selected_set_ids_for_generation.append(set_id)
    elif not is_selected and set_id in st.session_state.selected_set_ids_for_generation:
        st.session_state.selected_set_ids_for_generation.remove(set_id)

    st.markdown(get_text("divider"))

if set_ids_to_delete:
    for set_id_to_delete in set_ids_to_delete:
        del st.session_state.list_sets[set_id_to_delete]

    new_list_sets = {}
    current_new_set_id = 0
    for old_set_id in sorted(st.session_state.list_sets.keys()):
        new_list_sets[current_new_set_id] = st.session_state.list_sets[old_set_id]
        current_new_set_id += 1
    st.session_state.list_sets = new_list_sets
    st.session_state.next_set_id = current_new_set_id

    st.session_state.selected_set_ids_for_generation = [
        s_id for s_id in st.session_state.selected_set_ids_for_generation
        if s_id not in set_ids_to_delete
    ]
    st.rerun()

new_set_display_name_for_create_input = st.text_input(get_text("new_set_name_input"), value="", key="new_set_display_name_for_create_list_set_overview_bottom")
if st.button(get_text("create_new_set_button"), key="create_new_set_button_overview_bottom"):
    if new_set_display_name_for_create_input:
        if st.session_state.list_sets:
            max_current_set_id = max(st.session_state.list_sets.keys())
            new_set_id = max_current_set_id + 1
        else:
            new_set_id = 0

        st.session_state.list_sets[new_set_id] = {"display_name": new_set_display_name_for_create_input, "order": []}
        st.session_state.next_set_id = new_set_id + 1
        st.success(get_text("set_created_success").format(new_set_display_name_for_create_input))
        st.rerun()
    else:
        st.warning(get_text("enter_set_name"))

st.markdown(get_text("divider"))


# --- プロンプト生成セクション ---
st.markdown(f"### {get_text('prompt_generation_title')}")

generation_mode = st.radio(
    get_text("generation_mode_label"),
    (get_text("random_gen_mode"), get_text("all_combinations_gen_mode"), get_text("specific_list_sweep_gen_mode")),
    key="generation_mode"
)

num_results = 0
if generation_mode == get_text("random_gen_mode"):
    num_results = st.number_input(get_text("num_prompts_to_generate"), min_value=1, max_value=20, value=5)
elif generation_mode == get_text("all_combinations_gen_mode"):
    st.info(get_text("all_combinations_info"))
elif generation_mode == get_text("specific_list_sweep_gen_mode"):
    st.info(get_text("specific_list_sweep_info"))

    st.markdown(f"#### **{get_text('full_sweep_list_ids_title')}**")
    st.markdown(get_text("full_sweep_list_ids_instruction"))

    full_sweep_list_ids_str = st.text_input(
        get_text("full_sweep_list_num_input"),
        value=st.session_state.get("full_sweep_list_ids_str", ""),
        key="full_sweep_list_ids_input"
    )
    st.session_state.full_sweep_list_ids_str = full_sweep_list_ids_str

    full_sweep_list_ids = []
    if full_sweep_list_ids_str:
        max_available_list_id = max(st.session_state.keyword_lists.keys()) if st.session_state.keyword_lists else 0

        parsed_input_numbers = []
        input_error = False
        for x in full_sweep_list_ids_str.split():
            if x.isdigit():
                num = int(x)
                if 1 <= num <= max_available_list_id and num in st.session_state.keyword_lists:
                    parsed_input_numbers.append(num)
                else:
                    st.warning(get_text("invalid_list_num_warning").format(x, max_available_list_id), key=f"invalid_full_sweep_num_{x}")
                    input_error = True
            else:
                st.warning(get_text("invalid_input_warning").format(x), key=f"invalid_full_sweep_char_{x}")
                input_error = True

        if not input_error:
            full_sweep_list_ids = list(set(parsed_input_numbers))

output_display_mode = st.radio(
    get_text("output_display_method"),
    (get_text("display_by_set"), get_text("display_all_together")),
    key="output_display_mode"
)

shuffle_results = st.checkbox(get_text("shuffle_results"), key="shuffle_generated_prompts")

line_spacing_mode = st.radio(
    get_text("line_spacing_display"),
    (get_text("line_spacing_single"), get_text("line_spacing_none")),
    key="line_spacing_mode"
)


if st.button(get_text("generate_button")):
    st.session_state.generated_prompts = [] # 全体のフラットなリスト
    st.session_state.generated_prompts_by_set = {} # セットごとのプロンプトを格納
    st.session_state.prompts_for_copy_area = ""

    if st.session_state.selected_set_ids_for_generation:
        all_generated_results_flat = [] # 全プロンプトを格納する一時リスト

        sorted_selected_set_ids = sorted(st.session_state.selected_set_ids_for_generation)

        for set_id_to_generate in sorted_selected_set_ids:
            set_data_to_generate = st.session_state.list_sets.get(set_id_to_generate)
            display_set_name = f"{get_text('set_name_prefix')}{set_id_to_generate + 1} ({set_data_to_generate['display_name']})"

            if set_data_to_generate and "order" in set_data_to_generate:
                ordered_parsed_lists_with_flags = []
                for list_num in set_data_to_generate["order"]:
                    list_obj = st.session_state.keyword_lists.get(list_num)
                    if list_obj and "content" in list_obj:
                        parsed_list = parse_list(list_obj["content"])
                    else:
                        parsed_list = []

                    if not parsed_list:
                        st.warning(get_text("no_keyword_in_list_warning").format(set_name=display_set_name, list_num=list_num), key=f"skip_warning_{set_id_to_generate}_{list_num}")
                        continue

                    is_full_sweep = False
                    if generation_mode == get_text("specific_list_sweep_gen_mode"):
                        if list_num in full_sweep_list_ids:
                            is_full_sweep = True

                    ordered_parsed_lists_with_flags.append((list_num, is_full_sweep, parsed_list))

                generated_prompts_for_set = []

                if generation_mode == get_text("random_gen_mode"):
                    all_lists_for_generation = [item[2] for item in ordered_parsed_lists_with_flags]
                    if num_results > 0:
                        generated_prompts_for_set = generate_unique_combinations_random(all_lists_for_generation, num_results)
                elif generation_mode == get_text("all_combinations_gen_mode"):
                    all_lists_for_generation = [item[2] for item in ordered_parsed_lists_with_flags]
                    generated_prompts_for_set = generate_all_combinations(all_lists_for_generation)
                elif generation_mode == get_text("specific_list_sweep_gen_mode"):
                    if not full_sweep_list_ids:
                        st.warning(get_text("no_full_sweep_list_warning").format(set_name=display_set_name), key=f"no_fs_list_warning_{set_id_to_generate}")
                        all_lists_for_generation = [item[2] for item in ordered_parsed_lists_with_flags]
                        generated_prompts_for_set = generate_unique_combinations_random(all_lists_for_generation, 5)
                    else:
                        fs_indices = []
                        fs_actual_lists = []
                        rand_indices = []
                        rand_actual_lists = []

                        for i, (list_num, is_fs, parsed_list) in enumerate(ordered_parsed_lists_with_flags):
                            if is_fs:
                                fs_indices.append(i)
                                fs_actual_lists.append(parsed_list)
                            else:
                                rand_indices.append(i)
                                rand_actual_lists.append(parsed_list)

                        full_sweep_product = list(itertools.product(*fs_actual_lists)) if fs_actual_lists else [()]

                        generated_prompts_set_for_unique = set()

                        target_generation_count = len(full_sweep_product) if full_sweep_product else 1

                        current_attempts = 0
                        max_attempts_for_safety = target_generation_count * 10

                        while len(generated_prompts_set_for_unique) < target_generation_count and current_attempts < max_attempts_for_safety:
                            for fs_combo_tuple in full_sweep_product:
                                if len(generated_prompts_set_for_unique) >= target_generation_count:
                                    break

                                random_selected_elements = [random.choice(lst) for lst in rand_actual_lists]

                                final_prompt_elements = [None] * len(set_data_to_generate["order"])

                                for i, fs_val in zip(fs_indices, fs_combo_tuple):
                                    final_prompt_elements[i] = fs_val

                                for i, rand_val in zip(rand_indices, random_selected_elements):
                                    final_prompt_elements[i] = rand_val

                                final_prompt_elements_filtered = [elem for elem in final_prompt_elements if elem is not None]

                                prompt_str = ", ".join(final_prompt_elements_filtered)
                                generated_prompts_set_for_unique.add(prompt_str)
                            current_attempts += 1

                        generated_prompts_for_set = list(generated_prompts_set_for_unique)

                        if len(generated_prompts_for_set) < target_generation_count:
                            st.warning(get_text("partial_gen_warning").format(set_name=display_set_name, target_count=target_generation_count, generated_count=len(generated_prompts_for_set)), key=f"partial_gen_warning_{set_id_to_generate}")

                # 各セットのプロンプトを個別に保存
                st.session_state.generated_prompts_by_set[set_id_to_generate] = generated_prompts_for_set
                all_generated_results_flat.extend(generated_prompts_for_set)

            else:
                st.error(get_text("set_data_corrupt_error").format(display_set_name))

        st.session_state.generated_prompts = all_generated_results_flat # 全体をまとめたリストも更新

        prompts_for_copy_list = []
        
        # コピーエリアの構築ロジックを修正
        if output_display_mode == get_text("display_by_set"):
            for set_id in sorted_selected_set_ids:
                set_data = st.session_state.list_sets[set_id]
                display_set_name_for_separator = f"{get_text('set_name_prefix')}{set_id + 1} ({set_data['display_name']})"
                
                prompts_in_this_set = list(st.session_state.generated_prompts_by_set.get(set_id, []))
                if shuffle_results:
                    random.shuffle(prompts_in_this_set)

                if prompts_in_this_set:
                    prompts_for_copy_list.append(get_text("set_separator").format(set_name=display_set_name_for_separator, count=len(prompts_in_this_set)))
                    if line_spacing_mode == get_text("line_spacing_single"):
                        prompts_for_copy_list.append("")
                    
                    for prompt_line in prompts_in_this_set:
                        prompts_for_copy_list.append(prompt_line)
                        if line_spacing_mode == get_text("line_spacing_single"):
                            prompts_for_copy_list.append("")
                    # セットの最後の空行は、次のセットの区切りと統合されるか、
                    # 最後であれば削除されるように調整
                    if line_spacing_mode == get_text("line_spacing_single") and prompts_for_copy_list and prompts_for_copy_list[-1] == "":
                        prompts_for_copy_list.pop()
                    prompts_for_copy_list.append("") # セットの終わりにも空行を追加して次のセットとの間に間隔を作る

        else: # display_all_together の場合
            display_prompts_for_copy_prep = list(st.session_state.generated_prompts)
            if shuffle_results:
                random.shuffle(display_prompts_for_copy_prep)
            
            for prompt_line in display_prompts_for_copy_prep:
                prompts_for_copy_list.append(prompt_line)
                if line_spacing_mode == get_text("line_spacing_single"):
                    prompts_for_copy_list.append("")
        
        st.session_state.prompts_for_copy_area = "\n".join(prompts_for_copy_list)
        
        # 最終的な空行調整: 末尾の不要な空行を削除
        if st.session_state.prompts_for_copy_area.endswith("\n\n"):
            st.session_state.prompts_for_copy_area = st.session_state.prompts_for_copy_area[:-1]
        elif st.session_state.prompts_for_copy_area.endswith("\n"):
            st.session_state.prompts_for_copy_area = st.session_state.prompts_for_copy_area.rstrip('\n')

        if not st.session_state.generated_prompts:
            st.warning(get_text("no_prompts_generated"))

    else:
        st.warning(get_text("select_at_least_one_set"))

# --- コピー専用テキストエリアの表示 (生成ボタン押下後にも表示されるように移動) ---
st.markdown(get_text("divider"))
st.markdown(f"### {get_text('prompts_for_copy')}")

# コピーボタンは削除され、テキストエリアのみ表示
st.text_area(
    f"{get_text('prompts_for_copy')} ({get_text('line_spacing_display').replace('（コピー＆ペースト用）', '').replace('一行空きで表示', '')})",
    value=st.session_state.prompts_for_copy_area,
    height=300,
    key="final_copy_area_streamlit",
    disabled=not st.session_state.prompts_for_copy_area,
    help="このエリアのテキストをコピーするには、**テキストをすべて選択（Ctrl/Cmd+A）してからコピー（Ctrl/Cmd+C）**してください。"
)

st.markdown(get_text("divider"))


# --- プロンプト編集コーナー ---
st.markdown(f"### {get_text('prompt_edit_corner')}")

# 編集コーナーでは全プロンプトを対象とする
pure_prompts_for_edit = list(st.session_state.generated_prompts)

if not pure_prompts_for_edit:
    st.info(get_text("no_prompts_to_edit"))
else:
    st.markdown(f"#### {get_text('remove_specific_words')}")
    remove_words_input = st.text_input(get_text("remove_words_input_label"), key="remove_words_input")
    if st.button(get_text("remove_words_button"), disabled=not remove_words_input):
        words_to_remove = [w.strip() for w in remove_words_input.split(",") if w.strip()]
        if words_to_remove:
            new_prompts_temp = []
            for prompt in pure_prompts_for_edit:
                for word in words_to_remove:
                    # 単語の境界(\b)を使って、完全な単語としてマッチさせる
                    # re.escape()で特殊文字をエスケープ
                    prompt = re.sub(r'\b' + re.escape(word) + r'\b', '', prompt, flags=re.IGNORECASE)

                # 連続するカンマや、カンマ前後の不要なスペースを整理
                prompt = re.sub(r',(\s*,)+', ',', prompt) # 複数カンマを一つに
                prompt = re.sub(r'^\s*,\s*', '', prompt) # 行頭のカンマを削除
                prompt = re.sub(r'\s*,\s*$', '', prompt) # 行末のカンマを削除
                prompt = re.sub(r'\s*,\s*', ', ', prompt).strip() # カンマ前後のスペースを統一
                prompt = re.sub(r'\s+', ' ', prompt).strip() # 複数スペースを一つに

                if prompt: # 空になったプロンプトは追加しない
                    new_prompts_temp.append(prompt)

            st.session_state.generated_prompts = new_prompts_temp
            
            # コピーエリアの再構築
            prompts_for_copy_list_after_edit = []

            # 編集後は、セットの区切り情報は再構築が複雑になるため、
            # 基本的に「すべてまとめて表示」の形式で再構築する
            display_prompts_for_copy_prep = list(st.session_state.generated_prompts)
            if shuffle_results:
                random.shuffle(display_prompts_for_copy_prep)

            for prompt_line in display_prompts_for_copy_prep:
                prompts_for_copy_list_after_edit.append(prompt_line)
                if line_spacing_mode == get_text("line_spacing_single"):
                    prompts_for_copy_list_after_edit.append("")
            
            st.session_state.prompts_for_copy_area = "\n".join(prompts_for_copy_list_after_edit)
            
            # 最終的な空行調整
            if st.session_state.prompts_for_copy_area.endswith("\n\n"):
                st.session_state.prompts_for_copy_area = st.session_state.prompts_for_copy_area[:-1]
            elif st.session_state.prompts_for_copy_area.endswith("\n"):
                st.session_state.prompts_for_copy_area = st.session_state.prompts_for_copy_area.rstrip('\n')

            st.success(get_text("words_removed_success"))
            st.rerun()

    st.markdown(get_text("divider"))