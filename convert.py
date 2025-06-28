import json


def convert_sample_format(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    converted_data = {}

    for doc_id_str, entity_list in original_data.items():
        doc_id = int(doc_id_str)

        # 尝试自动生成简要信息（也可以根据原始文档数据加载更完整信息）
        sample_title = entity_list[0]["context"] if entity_list else f"Document {doc_id}"
        content_preview = entity_list[-1]["context"] if entity_list else ""

        extracted_entities = []
        for entity in entity_list:
            converted_entity = {
                "entity_type": entity.get("entity_type"),
                "entity_value": entity.get("entity_value"),
                "confidence": entity.get("confidence", 0.0),
                "field": entity.get("field", ""),
                "context": entity.get("context", "")[:100],
                "start_pos": entity.get("start_position", -1),
                "end_pos": entity.get("end_position", -1)
            }
            extracted_entities.append(converted_entity)

        converted_data[str(doc_id)] = {
            "document_info": {
                "doc_id": doc_id,
                "title": sample_title[:100],
                "content_preview": content_preview[:300]
            },
            "extracted_entities": extracted_entities
        }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 转换完成，保存到: {output_path}")


# 使用方法
convert_sample_format(
    input_path='results/npr_extraction_results.json',  # 替换为你的原始文件路径
    output_path='results/extraction_output.json'
)
