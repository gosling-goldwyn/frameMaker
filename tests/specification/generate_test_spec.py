import ast
import inspect
import re

def extract_test_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())

    test_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            docstring = ast.get_docstring(node)
            
            # Extract fixture names
            fixture_names = []
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == 'pytest.fixture':
                    # This decorator is for the fixture itself, not for functions using it
                    pass
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'pytest.mark.parametrize':
                    # Handle parametrize, if needed, but for now, just skip
                    pass
            
            # Extract fixtures from function arguments
            for arg in node.args.args:
                # Check if the argument name matches a known fixture pattern or is explicitly marked
                # For simplicity, we'll assume any argument not starting with 'self' is a fixture
                if not arg.arg.startswith('self'):
                    fixture_names.append(arg.arg)

            assert_statements = []
            for sub_node in ast.walk(node):
                if isinstance(sub_node, ast.Assert):
                    assert_statements.append(ast.unparse(sub_node))
            
            test_functions.append({
                'name': node.name,
                'docstring': docstring,
                'fixtures': fixture_names,
                'asserts': assert_statements
            })
    return test_functions

def format_test_spec(test_info, file_prefix):
    markdown_output = f"# Test Specification for {file_prefix}" + "\n\n"
    test_case_id_counter = 1

    for test in test_info:
        test_case_id = f"{file_prefix}-{test_case_id_counter:03d}"
        test_case_id_counter += 1
        
        # Format test case name
        formatted_name = test['name'].replace('test_', '').replace('_', ' ').title()
        
        markdown_output += f"## {test_case_id}: {formatted_name}" + "\n\n"
        markdown_output += f"**テスト関数名:** `{test['name']}`" + "\n\n"
        
        if test['docstring']:
            markdown_output += f"**概要:**\n{test['docstring']}" + "\n\n"
        else:
            markdown_output += "**概要:** (docstringがありません)" + "\n\n"

        if test['fixtures']:
            markdown_output += "**前提条件:**\n"
            for fixture in test['fixtures']:
                markdown_output += f"- `{fixture}` フィクスチャが提供するテストデータ/環境\n"
            markdown_output += "\n"
        
        markdown_output += "**テスト手順:**\n"
        markdown_output += f"1. `{test['name']}` 関数を実行する。\n"
        markdown_output += "\n"

        if test['asserts']:
            markdown_output += "**期待結果:**\n"
            for assert_stmt in test['asserts']:
                markdown_output += f"- `{assert_stmt}` が真であること。\n"
            markdown_output += "\n"
        else:
            markdown_output += "**期待結果:** (assert文が見つかりませんでした)" + "\n\n"
        
        markdown_output += "---" + "\n\n"
    return markdown_output

if __name__ == "__main__":
    frame_maker_tests = extract_test_info("tests/test_FrameMaker.py")
    image_handler_tests = extract_test_info("tests/test_ImageHandler.py")

    frame_maker_spec = format_test_spec(frame_maker_tests, "FM")
    image_handler_spec = format_test_spec(image_handler_tests, "IH")

    with open("tests/specification/test_specification_FrameMaker.md", "w", encoding="utf-8") as f:
        f.write(frame_maker_spec)
    
    with open("tests/specification/test_specification_ImageHandler.md", "w", encoding="utf-8") as f:
        f.write(image_handler_spec)

    print("テスト仕様書を生成しました: tests/specification/test_specification_FrameMaker.md, tests/specification/test_specification_ImageHandler.md")