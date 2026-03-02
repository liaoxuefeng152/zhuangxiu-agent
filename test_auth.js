// 模拟前端getWithAuth函数
const BASE_URL = "https://lakeli.top/api/v1";

// 模拟storage
const storage = {
  token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJvcGVuaWQiOiJvSXU1UTNTeWhrR3FnTXlfSXVvRkFmTnE5RnZnIiwiZXhwIjoxNzczMDMxMjM1fQ.6hBYleVAEIuPkgTT_ZWwCEEPtWq0SehMd7qFT0n7p1M",
  user_id: "2"
};

function getAuthHeaders() {
  const h = { 'Content-Type': 'application/json' };
  if (storage.token) h['Authorization'] = `Bearer ${storage.token}`;
  if (storage.user_id) h['X-User-Id'] = String(storage.user_id).trim();
  return h;
}

console.log("模拟的认证头:");
console.log(JSON.stringify(getAuthHeaders(), null, 2));

// 测试URL
const url = `${BASE_URL}/acceptance?stage=plumbing&page=1&page_size=5`;
console.log("\n测试URL:");
console.log(url);

// 模拟curl命令
console.log("\n模拟的curl命令:");
console.log(`curl -k -s "${url}" \\\n  -H "Authorization: Bearer ${storage.token}" \\\n  -H "X-User-Id: ${storage.user_id}"`);
