# 新工程：Test_02_ChipFlowProbe_NY8A051F

当前为复制的参考/资格母版，尚未实现新产品需求。请先完成Product_Requirements.md，再更新程序、行为场景和中文工程师交接。

# NY8A051F 芯片接入母版

这是未接产品负载的资格测试母版，不是成品功能。复制自对应官方完整GPIO工程，原件副本在Vendor_Original，官方文件原目录未改。

引脚：{'PORTB': 0}；各PORT先写0，再按上述输入掩码设置方向，其余脚为低输出，只适用于未连接外部驱动的资格夹具。新产品先填写需求表，重做引脚和有效电平。

状态：上电初始化后8位counter循环递增；主循环喂狗，无ISR、无产品定时器。没有设置产品关机时间。

配置继承对应型号的官方cb，具体值见Configuration_Readback.json。当前配置不代表实际产品供电/LVR、复位脚或负载要求已经确认，开发产品前必须重新核对，不能把062D配置套用。

编译、资源、自建模型通过；实板未测。请参考 ../../Bench_Test_Checklist.md，产品实测回填项目Bench_Results.md。


## 实板记录入口

按基地 `00_Reference/Templates/Bench_Test_Checklist.md` 执行。实测结果逐批次回填本目录 `Bench_Results.md`；当前未连接实物，全部实测项仍是待测，编译和模型结果不得填作实测通过。


## 资格夹具配置读回

| 项目 | 实际读回 |
|---|---|
| Id | NY8A051F |
| HighOsc | IRC |
| LowOsc | IRC |
| IrcFreq | FREQ_4 |
| InstructionClock | Clock4 |
| Wdt | ENABLE |
| WdtEvent | Reset |
| WdtTimeBase | Ms15 |
| LvrSetting | AlwaysOn |
| LvrVoltage | V16 |
| PowerOnClock | High |

FREQ_4=4MHz，Clock4=4T，因此指令周期1µs；本夹具不启用产品定时器，无产品超时计算。V16=1.6V只是继承官方配置的资格测试值，不能直接当作产品低电保护阈值。PB3在本GPIO配置中为IO，若产品需要RST必须重新配置并核对原理图。供电、电池、负载和保护参数仍待实际产品需求确认。
