import json

def parse_json_from_buffer(buffer):
    json_objects = []
    last_valid_json = None  # Keep track of the last valid JSON object
    start_index = 0  # Initialize the starting index for searching

    while True:
        try:
            # Find the next opening brace
            start_index = buffer.index('{', start_index)
            open_braces = 1  # Counter for nested braces
            
            # Find the corresponding closing brace
            end_index = start_index + 1
            while open_braces > 0 and end_index < len(buffer):
                if buffer[end_index] == '{':
                    open_braces += 1
                elif buffer[end_index] == '}':
                    open_braces -= 1
                end_index += 1
            
            # If we found a complete object, extract it
            if open_braces == 0:
                json_str = buffer[start_index:end_index]  # Extract complete JSON string
                json_objects.append(json.loads(json_str))  # Parse and append to the list
                last_valid_json = json.loads(json_str)  # Update last valid JSON
                
                # Move the starting index past this object for further searching
                start_index = end_index
            else:
                break  # Exit if we didn't find a complete object
            
        except (ValueError, json.JSONDecodeError):
            # If we can't find another opening brace or if there's an error in decoding, break out of the loop
            break

    return json_objects, buffer[end_index:].strip(), last_valid_json  # Return parsed objects, remaining buffer, and last valid JSON

# Example usage and test cases
test_cases = [
    '{"key1": {"nested_key": "value1"}}{"key2": "value2"}{"key3": "value3"}{"key4": {"nested_key_2": {"nested_key_3": "result"}}}',
    '{"key1": {"nested_key": "value1"}}{"key2": "value2"}{"key3": "value3"',
    '"key1": {"nested_key": "value1"}}{"key2": "value2"}{"key3": "value3"',
    '{"key1": {"nested_key": "value1"}}{"key2": "value2"}{"key3": "value3"}{"key4": {"nested_key_2": "value4"}}',
    '"key1": {"nested_key": "value1"}}{"key2": "value2"}{"key3": "value3"}{"key4": {"nested_key_2": "value4"}}',
]

for test in test_cases:
    parsed_objects, remaining_buffer, last_valid_json = parse_json_from_buffer(test)
    
    print(f"Input Buffer: {test}")
    print("Parsed JSON Objects:", parsed_objects)
    print("Remaining Buffer:", remaining_buffer)
    print("Last Valid JSON Object:", last_valid_json)
    print("---")
