# 清理照片与分析报告数据

`clear_photos_and_reports.sql` 会删除以下表的数据（不删用户、订单、消息等）：

- 施工照片 `construction_photos`
- 验收分析 `acceptance_analyses` 及关联（ai_consult_messages、ai_consult_sessions、acceptance_appeals）
- 材料核对 `material_checks`、`material_check_items`
- 公司检测 `company_scans`
- 报价单 `quotes`
- 合同 `contracts`
- **台账报告**（施工进度）`constructions`

## 在阿里云服务器执行

项目根目录执行（将 SQL 通过 stdin 传给远程 Postgres）：

```bash
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 "docker exec -i decoration-postgres-dev psql -U decoration -d zhuangxiu_dev" < scripts/clear_photos_and_reports.sql
```

或在服务器上（已 `git pull` 到 `/root/project/dev/zhuangxiu-agent`）：

```bash
cd /root/project/dev/zhuangxiu-agent
docker exec -i decoration-postgres-dev psql -U decoration -d zhuangxiu_dev < scripts/clear_photos_and_reports.sql
```

执行前请确认连接的是开发库 `zhuangxiu_dev`。
