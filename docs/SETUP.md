# 安装与首次构建 / Setup and first build

工作目录采用纯英文ASCII路径。Windows PowerShell负责调用厂商.NET配置库，Python负责构建事务及验证。先安装Python 3.10+，然后按README提供的Setup命令导入厂商依赖。

Use an ASCII workspace path. Windows PowerShell invokes the vendor .NET configuration library; Python runs the build transaction and verification. Install Python 3.10+ and import the vendor dependencies with the Setup command in the README.

| 参数 / Argument | 目录内容 / Expected contents |
|---|---|
| SdkPath | bin/sdcc.exe, include, cfg, inc, lib |
| AssemblerPath | nyas.exe, nylinker.exe, Nyquest.Core.dll, Nyquest.Bin.dll |
| NyidePath | bin/toolchain/make.exe, data/templates/project/makefile/makefile_ny8C.template |
| ExamplesPath | NY8A/NY8A051F/Template_C, NY8B/NY8B062D/Template_C |
| DatasheetDirectory | 下表两个PDF / The two PDFs below |

| 文件 / File | SHA256 |
|---|---|
| NY8B062D_v1.8_SC.pdf | `1727d429b25ce72bd3bd7c8bd3795b59f21eb2018ba30ba0f65d68cdec88befe` |
| NY8A051F_v1.5.pdf | `16ff2ebd608ee3bf88304dac545784fc437c9276539702230e254c094ac8d404` |

工具解析使用当前仓库内的00_Reference/Tools目录。make按NYQUEST_MAKE环境变量、toolchain.local.json、PATH、常见NYIDE安装目录的顺序定位。toolchain.local.json属于本机配置。SDK变更后重新完成对应芯片资格核验。

Vendor components resolve within the current workspace's 00_Reference/Tools directory. Make resolves from NYQUEST_MAKE, toolchain.local.json, PATH, then the common NYIDE installation location. toolchain.local.json belongs to the local machine. Requalify the chip after changing the SDK.

Setup在全新源码目录执行依赖导入与两份参考模板的真实编译。已有完整基地使用Repair-ProjectPaths.ps1逐个校正生成工程路径，再使用Build.ps1 -Isolated复核。官方工程原件作为来源归档保留。

Setup imports dependencies and actually builds both reference templates in a fresh source tree. Existing full workspaces relocate generated projects with Repair-ProjectPaths.ps1 and verify them with Build.ps1 -Isolated. Keep the original official projects as provenance records.

备份使用Backup.ps1 -Destination F:\NyquestBackups -Keep 10，选择与基地不同的实际磁盘。Backup requires an explicit destination on a different drive, for example Backup.ps1 -Destination F:\NyquestBackups -Keep 10.
