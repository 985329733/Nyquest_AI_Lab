# 安全 / Security

发布前运行Export-OpenSource.ps1，并检查PUBLIC_SOURCE_MANIFEST.json。公开目录采用独立Git历史。账号令牌、本机配置、厂商安装包和完整工作归档保存在用户本机。

Create public releases with Export-OpenSource.ps1 and inspect PUBLIC_SOURCE_MANIFEST.json. Use a dedicated public Git history. Keep account tokens, machine configuration, vendor installers and the complete working archive on the user's machine.

涉及凭据泄露的报告通过仓库维护者的私密渠道提交，并附最小复现步骤。涉及固件电气风险的报告记录芯片、供电、负载、原理图版本和固件哈希；验证使用具有限流及保护的工程测试环境。

Report credential exposure through a private maintainer channel with minimal reproduction steps. Electrical firmware reports should identify the MCU, supply, load, schematic revision and firmware hash. Perform hardware verification in an engineering test setup with appropriate current limiting and protection.
