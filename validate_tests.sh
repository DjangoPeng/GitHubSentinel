#!/bin/bash

# 运行单元测试并将结果输出到 test_results.txt
python -m unittest discover -s tests -p "test_*.py" > test_results.txt

# 检查测试结果，如果有失败，输出失败信息并让脚本退出状态为 1
if grep -q "FAILED" test_results.txt; then
    cat test_results.txt
    exit 1
else
    echo "All tests passed!"
    exit 0
fi
