# 验证契约 / Verification contract

每个工程使用schema_version=1的Project_Profile.json，列出configuration、clock、behavior.required_checks。定时产品同时列出timer.reload、timer.prescaler和behavior.tick_period_us。

Each project supplies a schema_version=1 Project_Profile.json with configuration, clock and behavior.required_checks. Timed applications also supply timer.reload, timer.prescaler and behavior.tick_period_us.

1. 解析工程身份和本机工具路径。Resolve project identity and local tool paths.
2. 用厂商库解码Makefile指定的cb，对照明确配置核对时钟、WDT、LVR及引脚。Decode the Makefile-selected cb with the vendor library and compare its clock, watchdog, LVR and pin functions with the explicit policy.
3. 按实际时钟计算指令频率和定时周期。Calculate instruction frequency and timer period from the decoded clock.
4. 运行make -B all，检查当前bin、elf、map、link.lst与编译诊断。Run make -B all and check current artifacts and diagnostics.
5. 核验资源与调用深度，写入包含run_id及输入/固件哈希的Build_Context.json。Verify resources and call depth; write the build context with the run ID and input/firmware hashes.
6. 执行项目场景并逐项核对报告，确认哈希和输入在全过程保持一致。Run project scenarios, validate each result and confirm stable hashes through the transaction.

BehaviorSuite负责生成报告。报告通过条件为：schema_version=1，status=PASS，failed=0，passed等于检查数量，检查名称唯一，每个passed为JSON布尔true，必需场景全部覆盖，context与本次构建完全一致。

BehaviorSuite writes the report. Successful evidence has schema_version=1, status=PASS, failed=0, a passed count equal to the number of checks, unique names, JSON boolean true for every check, coverage of all required scenarios and a context identical to the current build.

```python
from verification_contract import BehaviorSuite
suite = BehaviorSuite(PROJECT, 'Linked instruction model: product scenarios')
suite.check('Boot output is safe', observed_safe_output)
suite.finish()
```

软件模型使用构建上下文的实际指令频率。外设电气行为及振荡器误差由工程师按Bench_Test_Checklist.md执行实板测量。软件报告记录bench=UNTESTED，实测结果记录在Bench_Results.md。

The software model uses the instruction frequency bound to the build context. Engineers measure electrical peripheral behavior and oscillator tolerance with Bench_Test_Checklist.md. Software reports record bench=UNTESTED; hardware results belong in Bench_Results.md.
