# 九齐芯片资源表（本地发行包支持型号）

来源：NYASM 2.80 的 `Nyquest.Core.dll` 内嵌 `mask.xml`（已原样提取到 `Chip_Config/mask.xml`），交叉检查 NYC_NY8 2.10 的 cfg/inc/C 头文件。不是全市场型号表。
ROM 用“指令字 × 位宽”表示；cfg 的 program size 是链接器字节地址空间，不能当成指令字数。cfg 的 RAM 区含 SFR/地址空洞，不能直接当成物理 RAM。
ADC/PWM 为配置数据库声明，复用引脚不表示可同时占用；某些新型号共用旧 profile，使用前还须核对对应最新版手册。未声明不等于资料已证实不存在。
配置文件没有堆栈层数字段。NY8B062D及接入试跑NY8A051F已用对应官方手册补齐为8层；其它未补证型号保持“待核验”，不得据此批准新项目。NY8B062D ADC 的12通道为11个外部输入加1个内部通道。

| 型号 | ROM（字×位） | RAM（字节） | 全局变量70%上限 | 硬件堆栈 | ADC配置 | PWM配置（复用脚） |
|---|---:|---:|---:|---|---|---|
| NY8A050D | 512 × 14 | 32 | 22 | 待核验 | no ADC declared | no PWM pin declared |
| NY8A050E | 512 × 14 | 32 | 22 | 待核验 | no ADC declared | no PWM pin declared |
| NY8A050E1 | 512 × 14 | 32 | 22 | 待核验 | no ADC declared | no PWM pin declared |
| NY8A051A | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM1 8b PB2 |
| NY8A051B | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM1 8b PB2 |
| NY8A051C | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM1 8b PB2 |
| NY8A051D | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM1 8b PB2 |
| NY8A051E | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM1 8b PB2 |
| NY8A051F | 1024 × 14 | 48 | 33 | 8 | 无ADC（手册功能表及头文件核对） | 1路8位，PB2；与BZ1复用 |
| NY8A051G | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM1 8b PB2 |
| NY8A051H | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM1 8b PB2 |
| NY8A051H1 | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM1 8b PB2 |
| NY8A051J | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM3 ?b PB0; PWM2 ?b PB1; PWM1 8b PB2; PWM2 ?b PB4; PWM3 ?b PB5 |
| NY8A051K | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM3 ?b PB0; PWM2 ?b PB1; PWM1 8b PB2; PWM2 ?b PB4; PWM3 ?b PB5 |
| NY8A051L | 1024 × 14 | 48 | 33 | 待核验 | no ADC declared | PWM3 ?b PB0; PWM2 ?b PB1; PWM1 8b PB2; PWM2 ?b PB4; PWM3 ?b PB5 |
| NY8A052E | 1536 × 14 | 96 | 67 | 待核验 | no ADC declared | PWM2 ?b PA0; PWM2 ?b PA1; PWM4 ?b PA2; PWM3 ?b PA3; PWM4 ?b PB0; PWM3 ?b PB1; PWM1 10b PB2; PWM1 10b PB6 |
| NY8A053A | 1024 × 14 | 64 | 44 | 待核验 | no ADC declared | PWM1 8b PB6 |
| NY8A053B | 1024 × 14 | 64 | 44 | 待核验 | no ADC declared | PWM1 8b PB2; PWM1 8b PB6 |
| NY8A053D | 1024 × 14 | 64 | 44 | 待核验 | no ADC declared | PWM1 8b PB2; PWM1 8b PB6 |
| NY8A053E | 1024 × 14 | 64 | 44 | 待核验 | no ADC declared | PWM2 ?b PA0; PWM2 ?b PA1; PWM4 ?b PA2; PWM3 ?b PA3; PWM4 ?b PB0; PWM3 ?b PB1; PWM1 10b PB2; PWM1 10b PB6 |
| NY8A053E1 | 1024 × 14 | 96 | 67 | 待核验 | no ADC declared | PWM2 ?b PA0; PWM2 ?b PA1; PWM4 ?b PA2; PWM3 ?b PA3; PWM4 ?b PB0; PWM3 ?b PB1; PWM1 10b PB2; PWM1 10b PB6 |
| NY8A054A | 2048 × 14 | 128 | 89 | 待核验 | no ADC declared | PWM2 10b PA0; PWM5 10b PA1; PWM4 10b PA2; PWM3 10b PA3; PWM1 10b PA4; PWM5 10b PB0; PWM2 10b PB2; PWM1 10b PB3; PWM3 10b PB4; PWM4 10b PB5 |
| NY8A054D | 2048 × 14 | 128 | 89 | 待核验 | no ADC declared | PWM2 ?b PA0; PWM5 ?b PA1; PWM4 ?b PA2; PWM3 10b PA3; PWM1 10b PA4; PWM5 ?b PB0; PWM2 ?b PB2; PWM1 10b PB3; PWM3 10b PB4; PWM4 ?b PB5 |
| NY8A054E | 2048 × 14 | 128 | 89 | 待核验 | no ADC declared | PWM2 ?b PA0; PWM5 ?b PA1; PWM4 ?b PA2; PWM3 10b PA3; PWM1 10b PA4; PWM5 ?b PB0; PWM2 ?b PB2; PWM1 10b PB3; PWM3 10b PB4; PWM4 ?b PB5 |
| NY8A054E1 | 2048 × 14 | 128 | 89 | 待核验 | no ADC declared | PWM2 10b PA0; PWM5 ?b PA1; PWM4 ?b PA2; PWM3 10b PA3; PWM1 10b PA4; PWM5 ?b PA6; PWM2 10b PA7; PWM5 ?b PB0; PWM2 10b PB2; PWM1 10b PB3; PWM3 10b PB4; PWM4 ?b PB5 |
| NY8A056A | 1024 × 14 | 96 | 67 | 待核验 | no ADC declared | PWM2 8b PB4; PWM1 8b PB6 |
| NY8AE51D | 1024 × 14 | 64 | 44 | 待核验 | no ADC declared | PWM2 ?b PB0; PWM3 ?b PB1; PWM1 10b PB2 |
| NY8AE51F | 1024 × 14 | 64 | 44 | 待核验 | no ADC declared | PWM2 ?b PB0; PWM3 ?b PB1; PWM1 10b PB2 |
| NY8B060D | 1024 × 14 | 64 | 44 | 待核验 | 12 bit / 7 channels | PWM3 ?b PA2; PWM2 ?b PB2; PWM1 10b PB3 |
| NY8B060E | 1024 × 14 | 128 | 89 | 待核验 | 12 bit / 7 channels | PWM3 ?b PA2; PWM2 ?b PB2; PWM1 10b PB3 |
| NY8B060F | 1024 × 14 | 64 | 44 | 待核验 | 12 bit / 7 channels | PWM3 ?b PA2; PWM2 ?b PA4; PWM3 ?b PB1; PWM2 ?b PB2; PWM1 10b PB3 |
| NY8B061D | 2048 × 14 | 96 | 67 | 待核验 | 12 bit / 12 channels | PWM3 10b PA2; PWM2 10b PB2; PWM1 10b PB3 |
| NY8B061E | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 12 channels | PWM3 10b PA2; PWM4 ?b PA3; PWM2 10b PA4; PWM4 ?b PA7; PWM2 10b PB2; PWM1 10b PB3 |
| NY8B061F | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 12 channels | PWM3 ?b PA2; PWM4 ?b PA3; PWM2 10b PA4; PWM4 ?b PA7; PWM5 ?b PB0; PWM2 10b PB2; PWM1 10b PB3; PWM5 ?b PB3 |
| NY8B062A | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 12 channels | PWM3 10b PA2; PWM2 10b PB2; PWM1 10b PB3; PWM1 10b PB4; PWM2 10b PB5 |
| NY8B062B | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 12 channels | PWM3 10b PA2; PWM2 10b PB2; PWM1 10b PB3; PWM1 10b PB4; PWM2 10b PB5 |
| NY8B062D | 2048 × 14 | 128 | 89 | 8 | 12 bit / 12 channels | PWM3 10b PA2; PWM2 10b PB2; PWM1 10b PB3 |
| NY8B062E | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 12 channels | PWM3 10b PA2; PWM4 ?b PA3; PWM2 10b PA4; PWM4 ?b PA7; PWM2 10b PB2; PWM1 10b PB3 |
| NY8B062F | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 12 channels | PWM3 10b PA2; PWM4 ?b PA3; PWM2 10b PA4; PWM4 ?b PA7; PWM2 10b PB2; PWM1 10b PB3 |
| NY8B062F1 | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 12 channels | PWM3 10b PA2; PWM4 ?b PA3; PWM2 10b PA4; PWM4 ?b PA7; PWM5 ?b PB0; PWM2 10b PB2; PWM1 10b PB3; PWM5 ?b PB3 |
| NY8B071A | 1024 × 14 | 96 | 67 | 待核验 | 12 bit / 6 channels | PWM3 10b PA2; PWM2 10b PB2; PWM1 10b PB3 |
| NY8B072A | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 13 channels | PWM3 10b PA2; PWM1 10b PB4; PWM2 10b PB6 |
| NY8BE62D | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 13 channels | PWM3 ?b PA2; PWM2 ?b PA4; PWM3 ?b PA7; PWM1 10b PB1; PWM2 ?b PB2; PWM5 10b PB2; PWM1 10b PB3; PWM4 10b PB3; PWM1 10b PB4; PWM2 ?b PB5 |
| NY8BE64A | 4096 × 14 | 288 | 201 | 待核验 | 12 bit / 14 channels | PWM3 ?b PA2; PWM4 10b PA4; PWM3 ?b PA7; PWM1 10b PB1; PWM5 10b PB2; PWM2 ?b PB3; PWM1 10b PB4; PWM2 ?b PB5 |
| NY8BM61D | 2048 × 14 | 128 | 89 | 待核验 | no ADC declared | PWM3 ?b PA2; PWM4 10b PA3; PWM2 ?b PA4; PWM3 ?b PA7; PWM4 10b PA7; PWM1 10b PB1; PWM2 ?b PB2; PWM5 10b PB2; PWM1 10b PB3; PWM4 10b PB3; PWM1 10b PB4; PWM2 ?b PB5 |
| NY8BM62D | 2048 × 14 | 128 | 89 | 待核验 | no ADC declared | PWM3 ?b PA2; PWM4 10b PA3; PWM2 ?b PA4; PWM3 ?b PA7; PWM4 10b PA7; PWM1 10b PB1; PWM2 ?b PB2; PWM5 10b PB2; PWM1 10b PB3; PWM4 10b PB3; PWM1 10b PB4; PWM2 ?b PB5 |
| NY8BM72A | 2048 × 14 | 128 | 89 | 待核验 | 12 bit / 13 channels | PWM3 10b PA2; PWM3 10b PA7; PWM2 10b PB2; PWM1 10b PB3; PWM1 10b PB4; PWM2 10b PB5; PWM2 10b PC0; PWM1 10b PC1 |
| NY8BM84A | 4096 × 16 | 336 | 235 | 待核验 | 12 bit / 22 channels | PWM5 10b PA0; PWM4 10b PA1; PWM3 ?b PA2; PWM1 10b PA3; PWM2 ?b PA4; PWM4 10b PA4; PWM1 10b PA5; PWM3 ?b PA6; PWM2 ?b PA7; PWM3 ?b PB0; PWM1 10b PB1; PWM5 10b PB2; PWM2 ?b PB3; PWM4 10b PB3; PWM2 ?b PB4; PWM1 10b PB5; PWM3 ?b PB6; PWM2 ?b PB7; PWM5 10b PC0; PWM4 10b PC1; PWM5 10b PC2; PWM4 10b PC3; PWM5 10b PC5 |

## NY8B062D 权威补充

官方手册 `Docs/NY8B062D_v1.8_SC.pdf`：第7–9页资源；第24、29页输入/上拉；第56–57页Timer1/PWM；第71–78页看门狗、中断与睡眠；第97页配置字。
已确认：2048×14位ROM，128字节RAM，全局变量最多89字节，8层硬件堆栈，3路10位PWM（PB3/PB2/PA2）。末尾0x7FE–0x7FF有校验保留用途，实际以链接报告为准。
官方资料：https://www.nyquest.com.tw/upload/2023_02_243/NY8B062D_v1.8_SC.pdf

## NY8A051F 接入补证

官方手册：`00_Reference/Docs/NY8A051F_v1.5.pdf`，堆栈第7页、保留区第12页；ROM/RAM与配置数据库一致。资格证据：`Templates/NY8A051F_Validated/Qualification_Verification.json`。只是编译与空闲探针验证，未替用户选型、未实板验收。
