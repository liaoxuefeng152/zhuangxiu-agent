#!/bin/bash

echo "=== 修复施工照片API - 添加url字段 ==="
echo ""

# 1. 首先检查本地代码
echo "1. 检查本地construction_photos.py代码："
if grep -q '"url": signed_url or p.file_url' backend/app/api/v1/construction_photos.py; then
    echo "   ✅ 本地代码已包含url字段"
    
    # 显示关键代码
    echo ""
    echo "   关键代码位置："
    grep -n '"url": signed_url or p.file_url' backend/app/api/v1/construction_photos.py
    
    echo ""
    echo "   代码内容："
    grep -B2 -A2 '"url": signed_url or p.file_url' backend/app/api/v1/construction_photos.py | head -10
else
    echo "   ❌ 本地代码缺少url字段，需要修复"
fi

echo ""
echo "2. 修复阿里云服务器上的代码："
echo "   执行以下命令修复..."

# 创建修复脚本
cat > /tmp/fix_construction_photos.py << 'FIXEOF'
#!/usr/bin/env python3
"""
修复construction_photos.py，添加url字段
"""
import os
import sys

file_path = "/root/project/dev/zhuangxiu-agent/backend/app/api/v1/construction_photos.py"

# 读取文件内容
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经修复
if '"url": signed_url or p.file_url' in content:
    print("✅ 代码已包含url字段，无需修复")
    sys.exit(0)

# 查找需要修复的位置
# 第一个位置：by_stage[p.stage].append
if 'by_stage[p.stage].append' in content:
    # 找到第一个位置
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'by_stage[p.stage].append' in line:
            # 找到对应的闭合括号
            for j in range(i, min(i+20, len(lines))):
                if lines[j].strip() == '})':
                    # 在第j行之前插入url字段
                    # 找到"file_url": signed_url or p.file_url所在行
                    for k in range(i, j):
                        if '"file_url": signed_url or p.file_url' in lines[k]:
                            # 在这一行之后添加url字段
                            indent = len(lines[k]) - len(lines[k].lstrip())
                            new_line = ' ' * indent + '"url": signed_url or p.file_url,  # 添加url字段供前端使用'
                            lines.insert(k+1, new_line)
                            print(f"✅ 在第{k+1}行添加了url字段（第一个位置）")
                            break
                    break
            break

# 第二个位置：photo_list.append
if 'photo_list.append' in content:
    # 找到第二个位置
    for i, line in enumerate(lines):
        if 'photo_list.append' in line:
            # 找到对应的闭合括号
            for j in range(i, min(i+20, len(lines))):
                if lines[j].strip() == '})':
                    # 在第j行之前插入url字段
                    # 找到"file_url": signed_url or p.file_url所在行
                    for k in range(i, j):
                        if '"file_url": signed_url or p.file_url' in lines[k]:
                            # 在这一行之后添加url字段
                            indent = len(lines[k]) - len(lines[k].lstrip())
                            new_line = ' ' * indent + '"url": signed_url or p.file_url,  # 添加url字段供前端使用'
                            lines.insert(k+1, new_line)
                            print(f"✅ 在第{k+1}行添加了url字段（第二个位置）")
                            break
                    break
            break

# 写回文件
new_content = '\n'.join(lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ 代码修复完成")
FIXEOF

echo "   修复脚本已创建：/tmp/fix_construction_photos.py"
echo ""
echo "3. 执行修复："
echo "   ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 'python3 /tmp/fix_construction_photos.py'"
echo ""
echo "4. 重启后端服务："
echo "   ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 'cd /root/project/dev/zhuangxiu-agent && docker compose -f docker-compose.dev.yml restart backend'"
echo ""
echo "5. 验证修复："
echo "   等待10秒后测试API..."
echo "   sleep 10 && curl -H 'Authorization: Bearer YOUR_TOKEN' http://120.26.201.61:8001/api/v1/construction-photos | python3 -m json.tool | grep -A5 -B5 'url'"
echo ""
echo "=== 修复完成 ==="
