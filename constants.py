EXAMPLES = [
    {
        "text": (
            "Haidar Jupiter Fund ('the Fund') is an opportunistic, "
            "global-macro fund that takes exposure to liquid asset markets. "
        ),
        "head": "Haidar Jupiter Fund",
        "head_type": "Fund",
        "relation": "USES_STRATEGY",
        "tail": "global macro",
        "tail_type": "Strategy",
    },
    {
        "text": (
            "Haidar Jupiter Fund ('the Fund') is an opportunistic, "
            "global-macro fund that takes exposure to liquid asset markets. "
        ),
        "head": "Haidar Jupiter Fund",
        "head_type": "Fund",
        "relation": "HAS_EXPOSURE_TO",
        "tail": "Liquid Asset Markets",
        "tail_type": "Market",
    },
    {
        "text": (
            "The ASV Fund (“Fund”) is a multi-manager, multi-strategy, Asia focused fund which seeks absolute returns across market conditions."
        ),
        "head": "ASV Fund",
        "head_type": "Fund",
        "relation": "HAS_CHARACTERISTIC",
        "tail": "multi-manager",
        "tail_type": "Characteristic",
    },
    {
        "text": "The ASV Fund (“Fund”) is a multi-manager, multi-strategy, Asia focused fund which seeks absolute returns across market conditions.",
        "head": "ASV Fund",
        "head_type": "Fund",
        "relation": "HAS_CHARACTERISTIC",
        "tail": "multi-strategy",
        "tail_type": "Characteristic",
    },
    {
        "text": "Microsoft Word is a lightweight app that accessible offline",
        "head": "Microsoft Word",
        "head_type": "Product",
        "relation": "HAS_CHARACTERISTIC",
        "tail": "accessible offline",
        "tail_type": "Characteristic",
    },
]

system_prompt_parts = [
        "You are an algorithm designed to extract information in structured formats to build a knowledge graph. ",
        "Your task is to identify the entities and relations requested with the user prompt from a given text. ",
        "You must generate the output in JSON format containing a list with JSON objects. ",
        'Each object should have the keys: "head", "head_type", "relation", "tail", "tail_type". ',
        'The "head" key must contain the text of the extracted entity with one type. ',
        "Attempt to extract as many entities and relations as you can. ", 
        "Maintain Entity Consistency: When extracting entities, it's vital to ensure consistency. ", 
        'If an entity, such as "Haidar Jupiter Fund", is mentioned multiple times in the text but is referred to by different names or pronouns ', 
        '(e.g. "the Fund"), always use the most complete identifier for that entity. ',
        'The knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial. ',
        "IMPORTANT NOTES: \n - Don't add any explanation and text."
    ]

GRAPH_BUILDER_SYSTEM_PROMPT = "".join(system_prompt_parts)

GRAPH_BUILDER_HUMAN_PROMPT = """Based on the following example, extract entities and 
        relations from the provided text. Attempt to extract as many entities and relations as you can.

        Below are a number of examples of text and their extracted entities and relationships.
        {examples}

        For the following text or table, extract entities and relations as in the provided example. 
        {format_instructions}
        Text: {input} 
        IMPORTANT NOTES:
        - Each key must have a valid value, 'null' is not allowed. 
        - Unless otherwise specified, indefinite or nonspecific pronouns referring to "the month" or "the year" refer to the month {month} and the year {year} respectively.
        - Unless otherwise specified, indefinite or nonspecific pronouns referring to "the Fund", such as "our" or "we", refer to the entity {fund_name} """

BASE_ENTITY_LABEL = "__Entity__"

INCLUDE_DOCS_QUERY = (
    "MERGE (d:Document {id:$document.metadata.id}) "
    "SET d.text = $document.page_content "
    "SET d += $document.metadata "
    "WITH d "
)

NODE_IMPORT_QUERY = (
    f"{INCLUDE_DOCS_QUERY}"
    "UNWIND $data AS row "
    f"MERGE (source:`{BASE_ENTITY_LABEL}` {{id: row.id}}) "
    "SET source += row.properties "
    f"{'MERGE (d)-[:MENTIONS]->(source) '}"
    "WITH source, row "
    "CALL apoc.create.addLabels( source, [row.type] ) YIELD node "
    "RETURN distinct 'done' AS result"
    )

REL_IMPORT_QUERY = (
    "UNWIND $data AS row "
    f"MERGE (source:`{BASE_ENTITY_LABEL}` {{id: row.source}}) "
    f"MERGE (target:`{BASE_ENTITY_LABEL}` {{id: row.target}}) "
    "WITH source, target, row "
    "CALL apoc.merge.relationship(source, row.type, "
    "{}, row.properties, target) YIELD rel "
    "RETURN distinct 'done'"
    )