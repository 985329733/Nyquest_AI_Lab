# 小家电九齐 MCU AI 开发基地规范

本规范适用于本仓库新建和维护的产品固件。AGENTS.md与CLAUDE.md保持逐字一致。交流与工程师交接使用中文，固件.c源码与注释使用简单ASCII英文。

## 1. 可迁移环境

仓库根目录由脚本位置解析。SDK位于00_Reference/Tools/NYC_NY8/app，汇编链接器位于00_Reference/Tools/NYASM/app，真实C头文件位于00_Reference/include。make按NYQUEST_MAKE、toolchain.local.json、PATH、常见NYIDE安装路径定位。Setup.ps1从使用者提供的厂商安装目录导入依赖。

采用NY8专用SDCC、NYASM及真实.naprj、.NySln、.cb格式。Makefile从已验证工程复制或由NYIDE原始makefile_ny8C.template填入明确值生成。官方原件按原始字节归档。生成工程随仓库迁移后，用Repair-ProjectPaths.ps1显式校正并执行隔离复编。

## 2. 工程与芯片资格

新产品统一使用New-Project.ps1 -Chip 准确型号 -Name Category_01_ProductName，工程存入02_Projects/Category_01_ProductName_芯片型号，全路径采用英文ASCII。每个产品和修订使用独立目录，历史交付保留原件。

创建前核对Templates/准确型号_Validated/Qualification_Verification.json的型号与PASS状态。新型号由Add-Chip.ps1接入：读取本型号官方完整工程、真实C头、cfg/inc/lib、chips.json和官方手册；Chip_Evidence记录资料SHA256、页码、摘录、堆栈、校验保留字数、R-page位宽、启动库模型、GPIO夹具及ADC/PWM事实。资料一致、工具编译及该型号资格场景通过后登记Validated。待补资料逐项列明，独立工作继续执行。

产品开发先按Product_Requirement_Template.md确认供电、电池、负载、保护、引脚与验收条件。初次复制构建验证母版及工程链路，随后按已确认需求实现产品。

## 3. 真实资源和8位约束

写固件前读取Chip_Specs.md及对应型号真实C头，通常经ny8.h与-D__CPU_型号选取。寄存器、位名及宏均以真实C声明为依据。型号、频率或工具链变化后重新核验。

全局变量预算为物理RAM的70%向下取整，map同时核对临时变量、参数区、ISR保存和库分配。ROM以指令字计量，校验保留字由官方资料确认。待核验堆栈及外设随证据补齐后使用。

产品变量优先unsigned char及位标志，计时拆成8位计数，宽运算使用经过资源核算的8位分解。固件使用限定类型和接口；float、double、long及printf/malloc等标准库列入静态禁用规则。PC侧Python和PowerShell使用各自正常数据类型。

调用深度连同中断压栈及编译器隐式调用合计最多2层，并符合真实硬件堆栈上限。ISR直接完成短小的寄存器、标志和tick操作，调用图保持叶节点。共享变量使用volatile，读改写使用短临界区。

## 4. 电气与运行状态

main.c顶部集中声明LED_ON、MOTOR_ON等有效电平。关断路径按有效电平真实输出。先写PORT安全锁存，再设置IOST输出方向；外设使能前同样设置安全值。

主循环执行CLRWDT，配置字开启WDT并明确事件和时基。休眠前关闭负载、所需外设和非唤醒上下拉，保留指定唤醒脚的稳定电平，清中断源并启用所需唤醒。确认按键松开后进入睡眠，唤醒后清标志、恢复时钟、外设和WDT。

未用脚策略按实际原理图制定，考虑外部驱动、电源域和反向供电。LVR等保护与功耗取舍写入交接。PWM软启动、电流限幅、堵转和温度保护分别完成设计及实测验收。

## 5. 统一构建契约

Project_Profile.json明确芯片、配置字各字段、引脚、时钟和必需场景；定时产品明确重载、分频和节拍计算。每次固件修改后运行Build.ps1，实际执行make -B all，工具退出0、诊断清零、有效bin/elf/map/link.lst齐全后进入后续验证。

构建每次使用官方库读取Makefile指定cb，并对照项目配置核验WDT、时钟、LVR和引脚。Build_Context.json绑定唯一run_id及源码、配置、固件SHA256。BehaviorSuite输出逐项布尔结果；PASS要求全部必需场景成功、计数一致、failed=0、上下文和输入哈希匹配。

缺必要配置或场景证据使用INCOMPLETE，检查失败使用FAILED，全部软件阶段通过使用PASS。模块独立编译使用ARTIFACTS_PASS。配置、行为及最终流程分别保存证据。

完成工程复核使用Build.ps1 -Project ... -Isolated，保留原固件、配置与交付包。编译、静态检查、有限软件模型、官方仿真和实板验收分别记录结果；实板状态随真实仪器及板卡证据更新。

## 6. 工程师交接

项目README_For_Engineer.md使用中文，包含完整引脚/电平/连接/未用脚表、状态及上电关机唤醒与按键边界、时钟指令周期/分频/重载/中断/产品超时计算，以及实际IHRC、2T/4T、LVR、WDT和RST/IO配置。已写入配置与工程师待选电源负载参数分列。

交接引用00_Reference/Templates/Bench_Test_Checklist.md，实测逐批次回填Bench_Results.md。软件交付描述为编译通过的参考固件；待测实物项目明确列出。实板结果记录板卡、供电、负载、仪器、条件和固件哈希。

## 7. 版本、备份与公开源码

每个维护步骤单独提交Git，保留交付和验证证据。异盘完整备份使用Backup.ps1，包含工具链并默认保留10份。恢复使用独立空目录并核对清单及路径。

公开发布使用Export-OpenSource.ps1选择自主源码和中英文说明，在导出目录建立独立Git历史。厂商依赖通过Setup导入本地，原始授权与来源分别记录。公开源码采用LICENSE，第三方来源参见THIRD_PARTY.md。
