# Nyquest AI Lab · 小家电九齐 MCU AI 开发基地

简体中文 | [English](README.en.md)

面向Windows的九齐NY8固件开发工作区。用普通语言描述产品，确认电气需求，由AI按准确芯片型号完成资料核验、工程创建、固件开发、真实编译和工程师交接。

## 能力

- 采用对应芯片的官方完整工程、真实C头文件、链接配置和数据手册证据完成资格核验。
- 每次构建统一核对配置字、时钟、WDT、LVR、引脚、编译结果、资源和项目软件场景。
- 项目配置、源码、固件和逐项报告通过run_id及SHA256关联，形成完整验证证据。
- 提供10个参考模块：按键消抖、休眠唤醒、PWM软启动、电压ADC、充电状态、电机多档、灯效、蜂鸣器、组合键、软件电流保护。
- 提供中文工程师交接、实板清单、隔离复编和公开源码导出。

## 环境

| 组件 | 支持基线 |
|---|---|
| 系统 | Windows 10/11；纯英文ASCII工作目录 |
| Shell | Windows PowerShell 5.1及.NET Framework |
| Python | 3.10及以上 |
| 九齐工具 | NYC_NY8 2.10、NYASM 2.80；NYIDE提供make及原始Makefile模板 |
| 新芯片资料提取 | requirements.txt中的pypdf |

从[九齐技术支持](https://www.nyquest.com.tw/cn/support/download)或[来源记录](THIRD_PARTY.md)列出的渠道取得厂商工具。公开源码包包含本项目代码与示例源码配方，Setup从使用者的安装目录导入厂商依赖，各依赖沿用其原发行授权。

## 快速开始

将源码克隆到例如C:\work\Nyquest_AI_Lab，在目录中打开PowerShell，使用自己安装的实际路径：

```powershell
python -m pip install -r requirements.txt
.\Setup.ps1 `
  -SdkPath 'C:\Nyquest\NYC_NY8' `
  -AssemblerPath 'C:\Nyquest\NYASM' `
  -NyidePath 'C:\Nyquest\NYIDE' `
  -ExamplesPath 'C:\Nyquest\NY8_Example_Code' `
  -DatasheetDirectory 'C:\Nyquest\Datasheets'
```

SdkPath包含bin/sdcc.exe、cfg/inc/include/lib；AssemblerPath包含nyas.exe、nylinker.exe与Nyquest.Core.dll；ExamplesPath包含NY8A、NY8B目录。手册文件名和SHA256见[安装说明](docs/SETUP.md)。Setup在全新源码目录导入依赖，以对应官方工程生成参考项目，通过真实构建后登记两个Validated母版。

```powershell
.\New-Project.ps1 -ListChips
.\New-Project.ps1 -Chip NY8B062D -Name Test_01_LedReference
.\Build.ps1 -Project 02_Projects\Test_01_LedReference_NY8B062D -Isolated
```

新工程最初运行所选参考程序。产品开发先填写Product_Requirements.md，随后同步维护应用、Project_Profile.json、behavior_tests.py和README_For_Engineer.md。

## 验证与交付

Project_Profile.json记录芯片、实际时钟、配置字、引脚功能和必需场景。每次构建用厂商库读回当前cb并核对配置及计时公式，再运行make -B all、产物检查和软件场景。报告与本次固件、配置和输入哈希关联。

| 状态 | 含义 |
|---|---|
| ARTIFACTS_PASS | 编译产物及静态资源检查通过 |
| Workflow PASS | 配置、编译及必需软件场景全部通过 |
| INCOMPLETE | 项目配置或场景证据待补齐 |
| FAILED | 配置、工具、产物或场景检查需要修正 |
| Bench UNTESTED | 工程师实板测量待完成 |

NY8B062D三档灯参考程序采用3.0V参考板、PA0低有效按键、三个低有效LED、4MHz IHRC/4T、10ms节拍及300秒无操作关机，包含27项软件场景。NY8A051F提供6项空闲资格探针场景。当前时钟后端支持4MHz IRC的2T/4T解码，每个项目配置选择其实际核验值。

```powershell
python -m unittest discover -s 00_Reference/Scripts -p 'test_*.py' -v
python 00_Reference/Scripts/integration_checks.py
.\Package-Project.ps1 -Project 02_Projects\Test_01_LedReference_NY8B062D
```

独立单测可在干净源码目录运行；集成验证使用导入后的厂商工具与已生成工程。GitHub Actions执行独立单测，本机集成报告记录真实厂商工具验证。

交付使用工程目录中的bin、README_For_Engineer.md、Bench_Results.md及验证记录。实板按[测试清单](00_Reference/Templates/Bench_Test_Checklist.md)完成电流、时序、唤醒、WDT/LVR与负载保护测量，结果回填Bench_Results.md。固件C源码及注释采用ASCII英文，工程师交接采用中文，公开说明同步提供中英文。

## 开源发布

```powershell
.\Export-OpenSource.ps1 -Destination C:\work\Nyquest_AI_Lab_Public
```

导出器向全新目录写入明确选择的源码，生成SHA256清单并核验ZIP。在该目录建立公开Git历史，保留本机完整开发档案。详细步骤见[GitHub发布说明](docs/PUBLISH.md)。

项目编写的公开源码采用[MIT许可证](LICENSE)。参见[第三方来源](THIRD_PARTY.md)、[贡献指南](CONTRIBUTING.md)、[验证契约](docs/VERIFICATION.md)和[安全说明](SECURITY.md)。
