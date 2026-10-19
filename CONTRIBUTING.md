# 贡献 / Contributing

先阅读AGENTS.md，并保持CLAUDE.md与其逐字一致。使用具体芯片、真实头文件和对应官方工程完成开发。每个产品维护自己的需求、Project_Profile.json和behavior_tests.py。

Read AGENTS.md and keep CLAUDE.md byte-identical. Use the exact MCU, its actual C header and matching vendor project. Maintain product requirements, Project_Profile.json and behavior_tests.py for each application.

提交前执行：

```powershell
python -m unittest discover -s 00_Reference/Scripts -p 'test_*.py' -v
python 00_Reference/Scripts/integration_checks.py
```

Run the portable unit tests and the vendor-backed integration checks before submitting changes that affect builds. Include the observed result, tool versions, chip, resource use and test scope in the pull request. Describe board measurements with the board revision, instruments and firmware SHA256.

PR说明写明问题、修改后的行为、验证结果和实板状态。公开提交使用项目源码；厂商依赖通过Setup在本机导入。C源码和注释采用ASCII英文，工程师交接文档采用中文，公开说明同步维护中英文。

Firmware C sources and comments use ASCII English. Engineering handoffs use Chinese. Keep the Chinese and English public documentation aligned. Submit project source; import vendor dependencies locally through Setup.
