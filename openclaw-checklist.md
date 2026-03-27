# Openclaw 系统最佳实践清单

## 安全与凭证
- Token 权限：Contents Read & Write, Metadata Read-only
- Workflow 权限：如需修改 CI 文件，额外加 Workflow Read & Write
- 凭证保存：Keychain / 密码管理器

## 备份与完整性
- 定期 tarball + SHA256 校验
- 保留 manifest 和 restore log
- 多副本存储（本地 + 云端）

## 文档与可读性
- README 简介
- .env.example 配置示例
- 脚本用途说明

## CI/CD 与自动化
- JSON schema 校验
- Meta 字段注入
- Workflow 权限配置

## 推送与协作
- 私人项目：直接 push 主分支
- 团队协作：使用 PR 流程
