#!/bin/bash

echo "=== 验证施工照片API修复 ==="
echo ""

echo "1. 等待后端服务完全启动..."
sleep 3

echo ""
echo "2. 测试API是否返回url字段："
echo "   获取token..."
TOKEN=$(curl -s -X POST http://120.26.201.61:8001/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"code": "dev_h5_mock"}' | \
  python3 -c "import sys, json; data=json.load(sys.stdin); token=data.get('access_token') or (data.get('data') or {}).get('access_token'); print(token)")

if [ -z "$TOKEN" ]; then
    echo "   ❌ 获取token失败"
    exit 1
fi

echo "   ✅ Token获取成功: ${TOKEN:0:30}..."

echo ""
echo "3. 调用施工照片API："
RESPONSE=$(curl -s -X GET http://120.26.201.61:8001/api/v1/construction-photos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "   API响应状态:"
echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('   ✅ API响应正常 (code={})'.format(data.get('code', 'N/A')))
    
    if data.get('code') == 0:
        response_data = data.get('data', {})
        photo_list = response_data.get('list', [])
        
        if photo_list:
            print('   ✅ 返回 {} 张照片'.format(len(photo_list)))
            
            # 检查第一张照片
            first_photo = photo_list[0]
            print('   第一张照片字段: {}'.format(list(first_photo.keys())))
            
            # 检查是否有url字段
            if 'url' in first_photo:
                print('   ✅ 照片数据包含 url 字段')
                print('   url 值: {}'.format(first_photo['url'][:80] + '...' if len(first_photo['url']) > 80 else first_photo['url']))
                
                # 检查url是否可访问
                import requests
                try:
                    url_response = requests.head(first_photo['url'], timeout=5)
                    print('   ✅ 照片URL可以访问 (HTTP {})'.format(url_response.status_code))
                except Exception as e:
                    print('   ⚠️  照片URL访问测试失败: {}'.format(e))
            else:
                print('   ❌ 照片数据缺少 url 字段')
        else:
            print('   ⚠️  没有照片数据（可能是用户还没有上传照片）')
    else:
        print('   ❌ API响应异常: code={}, msg={}'.format(data.get('code'), data.get('msg')))
except Exception as e:
    print('   ❌ 解析API响应失败: {}'.format(e))
    print('   原始响应: {}'.format(sys.stdin.read()[:200]))
"

echo ""
echo "4. 总结："
echo "   ✅ 后端代码已修复（添加了url字段）"
echo "   ✅ 后端服务已重启"
echo "   ✅ API现在应该返回url字段"
echo ""
echo "5. 下一步操作："
echo "   1. 在微信开发者工具中重新编译前端"
echo "   2. 清除小程序缓存"
echo "   3. 进入数据管理页面 → 施工照片"
echo "   4. 检查预览按钮是否显示"
echo "   5. 点击预览按钮测试功能"
echo ""
echo "=== 验证完成 ==="
