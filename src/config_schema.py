CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ConfigObject",
    "type": "object",
    "properties": {
        "endpoints": {
            "type": "object",
            "patternProperties": {
                "/.*": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "properties": {"function": {"type": "string"}, "env": {"type": "object"}},
                            "required": ["function"],
                        }
                    },
                }
            },
        }
    },
    "required": ["endpoints"],
}
