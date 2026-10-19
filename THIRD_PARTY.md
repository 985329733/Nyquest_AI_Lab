# 第三方来源 / Third-party provenance

项目编写的公开源码采用MIT许可证。公开源码清单由Export-OpenSource.ps1生成的PUBLIC_SOURCE_MANIFEST.json定义。九齐及其它依赖按各自发行包的授权条款使用。

Project-authored public source files use the MIT License. PUBLIC_SOURCE_MANIFEST.json identifies the exported files. Vendor components and other dependencies retain the terms provided by their respective distributions.

| 组件 / Component | 获取来源 / Source | 本项目处理 / Handling |
|---|---|---|
| NYIDE、NYC_NY8、NYASM、官方示例 | [Nyquest support](https://www.nyquest.com.tw/cn/support/download) | 用户提供安装目录，Setup导入本地依赖 / User-supplied local dependency |
| 已验证发行包 / Verified distribution baseline | [Distributor download page](https://www.atwin-tech.com/download/edownload.html) | 版本与归档哈希见下表 / Versions and observed archive hash below |
| NY8B062D v1.8 SC手册 | [Vendor PDF](https://www.nyquest.com.tw/upload/2023_02_243/NY8B062D_v1.8_SC.pdf) | 用户提供对应PDF / User-supplied matching PDF |
| NY8A051F v1.5手册 | [Vendor PDF](https://www.nyquest.com.tw/upload/2021_07_073/NY8A051F_v1.5.pdf) | 用户提供对应PDF / User-supplied matching PDF |
| Python pypdf | [pypdf](https://github.com/py-pdf/pypdf) | 由requirements.txt安装 / Installed through requirements.txt |

| 记录 / Record | 值 / Value |
|---|---|
| 发行包版本 / Distribution | NYIDE 5.90 Build 251128.00 |
| 编译器 / Compiler | NYC_NY8 2.10 Build 251121.00 |
| 汇编链接 / Assembly and linking | NYASM 2.80 Build 251121.00 |
| 官方示例 / Examples | NY8_Example_Code 2.10 Build 251127.00 |
| 归档SHA256 / Observed archive SHA256 | `6ecbc5367fc487cc9c071f79754ea9a25243ee8b413fe0257b38a40206897064` |

该SHA256记录本基地已验证下载文件的身份。厂商签名与厂商公布校验值按厂商渠道核对。

The SHA256 identifies the archive verified in this workspace. Verify vendor signatures and vendor-published checksums through the vendor's channels.

公开导出范围包含自主脚本、模块、源码配方、技术参数记录和短小的资料定位摘录。工具二进制、厂商头文件、原始模板、数据手册、编译产物和本机Git历史保留在本地完整基地。厂商SDK中的SDCC组件自带COPYING；使用其发行包时保留相应版权和许可证文件。

The public export contains project-authored scripts, modules, source recipes, factual technical records and short evidence locators. Tool binaries, vendor headers/templates, datasheets, compiled artifacts and the local Git archive stay in the full development workspace. The SDK's SDCC component includes COPYING; preserve its notices and license files when handling that distribution.
