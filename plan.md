1. **构建模拟环境及对象模型 (Simulation Environment & Object Models)**:
   - 定义图网络：`RoadNetwork` (15个节点，包含正常边与损坏边)，`PowerNetwork` (12个节点，包含配电站、节点、负荷、关键设施，以及正常线路与故障线路)。使用 `networkx` 构建网络拓扑。
   - 定义抢修任务类 `RepairTask`，分路网抢修和电网抢修。
   - 定义抢修队伍类 `RepairCrew`：路网抢修队、电网抢修队、直升机队，具备位置、状态、移动速度、作业时间等属性。
2. **实现四种调度策略 (Heuristic Dispatch Strategies)**:
   - `S1_Strategy`: 先路后电。先指派路网抢修队修复损坏路段，只有道路连通后电网队伍才可前往修复点。
   - `S2_Strategy`: 边路边电。路网和电网队伍并行作业。电网队伍可利用已修复或未损坏的路网动态选择可达的故障点进行修复。
   - `S3_Strategy`: 空中跨维响应。除了地面队伍作业，增加直升机队伍。直升机可无视路网阻断，直接飞往关键设施所在的电力故障点或路段投送力量。
   - `S4_Strategy`: 天地组合策略。地空协同，直升机优先修复高价值电力节点，地面队伍并行推进。采用贪心策略根据收益(关键负荷大小/距离)分配任务。
3. **事件驱动仿真引擎 (Event-Driven Simulation Engine)**:
   - 维护一个全局时钟 $t$ 和事件队列（如到达节点、开始修复、修复完成）。
   - 每次事件触发时，更新任务状态、恢复供电负荷 $L(t)$，并调用策略分配空闲队伍。
   - 在每个时间步或事件点记录已恢复的总负荷。
4. **WandB 集成与运行实验 (WandB Integration & Experimentation)**:
   - 使用给定的 WandB API key 初始化项目。
   - 针对四种策略分别运行仿真，记录时间 $t$、当前恢复负荷 $L(t)$、累计 AUC、总工期 Makespan 等指标到 WandB。
   - 利用 `matplotlib` 在本地绘制恢复曲线图 (LSD)、AUC对比柱状图、工期对比柱状图，保存为本地图片。并将这些图片 log 到 wandb。
5. **上传图片至 imgbb (Image Upload to ImgBB)**:
   - 编写函数，使用给定的 imgbb API key 将本地生成的图表图片上传至 imgbb，获取公开的图片 URL。
6. **生成实验报告 (Markdown Report Generation)**:
   - 编写代码自动生成 `报告.md`，包含背景介绍、实验设置、各策略的恢复曲线与指标对比（插入 imgbb 获取的图片链接）、以及策略的解释性分析。
7. **执行测试与检查 (Pre-commit checks & Verification)**:
   - 运行 pre-commit check (验证是否有 linter/formatter 错误，不过这主要是一个单脚本项目，重点是代码能跑通且图表和报告能正常生成)。
