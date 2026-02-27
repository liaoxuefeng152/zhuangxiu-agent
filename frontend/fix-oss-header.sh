#!/bin/bash

# 备份原文件
cp src/services/api.ts src/services/api.ts.bak

# 修复 acceptanceApi.uploadPhoto 中的 header
sed -i '' '/uploadPhoto:/,/Taro\.uploadFile/{ /header: headers,/d; }' src/services/api.ts

# 修复 quoteApi.upload 中的 header（可选，但一起修复）
sed -i '' '/quoteApi = {/,/upload:/ { /header: getAuthHeaders(),/s//\/\/ header: getAuthHeaders(),/ }' src/services/api.ts

# 修复 contractApi.upload 中的 header（可选，但一起修复）
sed -i '' '/contractApi = {/,/upload:/ { /header: getAuthHeaders(),/s//\/\/ header: getAuthHeaders(),/ }' src/services/api.ts

# 修复 constructionPhotoApi.upload 中的 header（可选，但一起修复）
sed -i '' '/constructionPhotoApi = {/,/upload:/ { /header: getAuthHeaders(),/s//\/\/ header: getAuthHeaders(),/ }' src/services/api.ts

# 修复 designerApi.uploadImage 中的 header
sed -i '' '/designerApi = {/,/uploadImage:/ { /header: headers,/d; }' src/services/api.ts

echo "修复完成！"
