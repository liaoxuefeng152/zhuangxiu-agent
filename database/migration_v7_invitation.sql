-- V2.6.8 邀请系统迁移脚本
-- 执行时间：2026-02-16
-- 说明：添加邀请记录表和免费解锁权益表

-- 1. 创建邀请记录表
CREATE TABLE IF NOT EXISTS invitation_records (
    id SERIAL PRIMARY KEY,
    inviter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invitee_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, accepted, rewarded
    reward_type VARCHAR(20), -- free_unlock, points, etc.
    reward_granted BOOLEAN DEFAULT FALSE,
    reward_granted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 创建免费解锁权益表
CREATE TABLE IF NOT EXISTS free_unlock_entitlements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entitlement_type VARCHAR(20) NOT NULL, -- invitation, promotion, etc.
    source_id INTEGER, -- 来源ID（如邀请记录ID）
    report_type VARCHAR(20), -- quote, contract, company, acceptance
    report_id INTEGER, -- 具体报告ID（可选，为空表示通用）
    status VARCHAR(20) NOT NULL DEFAULT 'available', -- available, used, expired
    used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_invitation_records_inviter_id ON invitation_records(inviter_id);
CREATE INDEX IF NOT EXISTS idx_invitation_records_invitee_id ON invitation_records(invitee_id);
CREATE INDEX IF NOT EXISTS idx_invitation_records_status ON invitation_records(status);
CREATE INDEX IF NOT EXISTS idx_invitation_records_created_at ON invitation_records(created_at);

CREATE INDEX IF NOT EXISTS idx_free_unlock_entitlements_user_id ON free_unlock_entitlements(user_id);
CREATE INDEX IF NOT EXISTS idx_free_unlock_entitlements_status ON free_unlock_entitlements(status);
CREATE INDEX IF NOT EXISTS idx_free_unlock_entitlements_expires_at ON free_unlock_entitlements(expires_at);
CREATE INDEX IF NOT EXISTS idx_free_unlock_entitlements_created_at ON free_unlock_entitlements(created_at);

-- 4. 添加邀请码字段到用户表（可选，用于邀请链接）
ALTER TABLE users ADD COLUMN IF NOT EXISTS invitation_code VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS invited_by INTEGER REFERENCES users(id);

-- 5. 为现有用户生成邀请码（如果字段已存在则跳过）
UPDATE users SET invitation_code = 'INV' || LPAD(id::text, 6, '0') WHERE invitation_code IS NULL;

-- 6. 创建唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_invitation_code ON users(invitation_code) WHERE invitation_code IS NOT NULL;

COMMENT ON TABLE invitation_records IS '邀请记录表（V2.6.8新增）';
COMMENT ON COLUMN invitation_records.inviter_id IS '邀请人ID';
COMMENT ON COLUMN invitation_records.invitee_id IS '被邀请人ID';
COMMENT ON COLUMN invitation_records.status IS '状态：pending-待接受, accepted-已接受, rewarded-已奖励';
COMMENT ON COLUMN invitation_records.reward_type IS '奖励类型：free_unlock-免费解锁, points-积分';
COMMENT ON COLUMN invitation_records.reward_granted IS '奖励是否已发放';

COMMENT ON TABLE free_unlock_entitlements IS '免费解锁权益表（V2.6.8新增）';
COMMENT ON COLUMN free_unlock_entitlements.entitlement_type IS '权益类型：invitation-邀请奖励, promotion-活动奖励';
COMMENT ON COLUMN free_unlock_entitlements.source_id IS '来源ID（如邀请记录ID）';
COMMENT ON COLUMN free_unlock_entitlements.report_type IS '报告类型：quote-报价单, contract-合同, company-公司, acceptance-验收报告';
COMMENT ON COLUMN free_unlock_entitlements.report_id IS '具体报告ID（为空表示通用权益）';
COMMENT ON COLUMN free_unlock_entitlements.status IS '状态：available-可用, used-已使用, expired-已过期';

COMMENT ON COLUMN users.invitation_code IS '用户邀请码（V2.6.8新增）';
COMMENT ON COLUMN users.invited_by IS '邀请人ID（V2.6.8新增）';
