# Changelog

本项目所有重要变更都记录在本文件中。
格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- DV-12: 种子数据脚本 `seed.py`，一键插入演示用客户/动物/物业/预约数据
- DV-12: 本 CHANGELOG.md
- DV-12: config.py 支持通过 `APP_ENV` 区分开发/测试/生产环境

## [v0.2.0] - 2026-09-26

### Added
- DV-01: 客户建档（姓名、电话、地址）与客户搜索（按姓名/电话）
- DV-02: 客户信息修改与客户停用（软删除，停用客户不可新建预约）
- DV-03: 动物 CRUD（新增/查看动物档案）
- DV-04: 动物搜索（按名称和物种筛选）
- DV-05: 物业（Property）记录与页面
- DV-08: 预约改期与取消（区分诊所预约 clinic / 农场出诊 farm，含时间冲突校验）
- DV-10: 农场出诊路线视图（按物业名称排序）

### Changed
- 使用 Flask + Flask-SQLAlchemy + SQLite 技术栈
- 分支规范：feature 分支从 develop 拉出，PR 评审后合并

## [v0.1.0] - 2026-09-17

### Added
- 项目初始化：Flask 工程结构、SQLite 数据库、基础模板
- CI 流水线（GitHub Actions）
