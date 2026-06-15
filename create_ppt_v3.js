const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Wesley Cheng";
pres.title = "AI Chat Platform - 项目文档（含测试与日志）";

// Color palette - Ocean Gradient theme
const PRIMARY = "065A82";
const SECONDARY = "1C7293";
const ACCENT = "21295C";
const DARK = "0F1B2D";
const LIGHT = "F0F7FF";
const WHITE = "FFFFFF";
const GREEN = "059669";
const RED = "DC2626";
const AMBER = "D97706";
const BLUE_LIGHT = "DBEAFE";
const GRAY = "64748B";
const GRAY_LIGHT = "F1F5F9";

const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.12 });

// ========== Slide 1: Title ==========
let s1 = pres.addSlide();
s1.background = { color: DARK };
s1.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.08, fill: { color: SECONDARY } });
s1.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.545, w: 10, h: 0.08, fill: { color: SECONDARY } });
s1.addText("AI Chat Platform", { x: 0.8, y: 1.2, w: 8.4, h: 1.2, fontSize: 44, fontFace: "Arial Black", color: WHITE, bold: true });
s1.addText("项目文档", { x: 0.8, y: 2.3, w: 8.4, h: 0.8, fontSize: 32, fontFace: "Arial", color: SECONDARY, bold: true });
s1.addShape(pres.shapes.LINE, { x: 0.8, y: 3.3, w: 3, h: 0, line: { color: SECONDARY, width: 3 } });
s1.addText([
  { text: "React + TypeScript + FastAPI + PostgreSQL", options: { fontSize: 14, color: "94A3B8", breakLine: true } },
  { text: "开发者：Wesley Cheng", options: { fontSize: 14, color: "94A3B8", breakLine: true } },
  { text: "更新日期：2026-06-15", options: { fontSize: 14, color: "94A3B8" } }
], { x: 0.8, y: 3.6, w: 8, h: 1.2 });

// ========== Slide 2: 目录 ==========
let s2 = pres.addSlide();
s2.background = { color: WHITE };
s2.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s2.addText("目录", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 28, fontFace: "Arial Black", color: WHITE, bold: true });

const tocItems = [
  ["01", "项目概述与核心特性"],
  ["02", "系统架构与技术栈"],
  ["03", "功能模块详解"],
  ["04", "开发时间线与Bug修复"],
  ["05", "单元测试体系"],
  ["06", "测试覆盖率报告"],
  ["07", "日志系统设计"],
  ["08", "部署架构与使用指南"],
  ["09", "未来规划"],
];
tocItems.forEach((item, i) => {
  const row = Math.floor(i / 3);
  const col = i % 3;
  const x = 0.5 + col * 3.2;
  const y = 1.3 + row * 1.4;
  s2.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.8, h: 1.1, fill: { color: i >= 4 && i <= 6 ? BLUE_LIGHT : GRAY_LIGHT }, shadow: makeShadow(), rectRadius: 0.08 });
  s2.addText(item[0], { x, y: y + 0.08, w: 2.8, h: 0.45, fontSize: 22, fontFace: "Arial Black", color: PRIMARY, align: "center" });
  s2.addText(item[1], { x, y: y + 0.55, w: 2.8, h: 0.4, fontSize: 11, fontFace: "Arial", color: GRAY, align: "center" });
});

// ========== Slide 3: 项目概述 ==========
let s3 = pres.addSlide();
s3.background = { color: WHITE };
s3.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s3.addText("项目概述与核心特性", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 28, fontFace: "Arial Black", color: WHITE, bold: true });

const features = [
  ["多模型支持", "DeepSeek、OpenAI、Anthropic\nOllama、自定义模型"],
  ["文件智能解析", "PDF、DOCX、XLSX、TXT、MD\n自动解析内容 + RAG"],
  ["Agent 智能体", "自定义 System Prompt\n工具配置、角色绑定"],
  ["流式对话", "SSE 实时输出\n打字动画 + 光标效果"],
  ["响应式设计", "桌面端 + 移动端适配\n侧边栏滑出 + 遮罩"],
  ["安全认证", "JWT + bcrypt 加密\nToken 刷新机制"],
];
features.forEach((f, i) => {
  const row = Math.floor(i / 3);
  const col = i % 3;
  const x = 0.5 + col * 3.2;
  const y = 1.3 + row * 2.0;
  s3.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.8, h: 1.7, fill: { color: LIGHT }, shadow: makeShadow(), rectRadius: 0.08 });
  s3.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.8, h: 0.06, fill: { color: SECONDARY } });
  s3.addText(f[0], { x: x + 0.15, y: y + 0.15, w: 2.5, h: 0.4, fontSize: 14, fontFace: "Arial", color: PRIMARY, bold: true });
  s3.addText(f[1], { x: x + 0.15, y: y + 0.55, w: 2.5, h: 1.0, fontSize: 11, fontFace: "Arial", color: GRAY });
});

// ========== Slide 4: 系统架构 ==========
let s4 = pres.addSlide();
s4.background = { color: WHITE };
s4.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s4.addText("系统架构", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 28, fontFace: "Arial Black", color: WHITE, bold: true });

// Architecture layers
const layers = [
  { label: "用户层", sub: "Web Browser / Mobile", color: "3B82F6", y: 1.2 },
  { label: "前端层", sub: "React + TypeScript + Vite + Zustand + TanStack Query", color: "0EA5E9", y: 2.1 },
  { label: "后端层", sub: "FastAPI + LangChain + SQLAlchemy + JWT + SSE", color: SECONDARY, y: 3.0 },
  { label: "数据层", sub: "PostgreSQL + Redis + ChromaDB + Uploads", color: PRIMARY, y: 3.9 },
];
layers.forEach(l => {
  s4.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: l.y, w: 8.4, h: 0.7, fill: { color: l.color }, shadow: makeShadow(), rectRadius: 0.06 });
  s4.addText(l.label, { x: 1.0, y: l.y + 0.05, w: 2, h: 0.6, fontSize: 14, fontFace: "Arial", color: WHITE, bold: true });
  s4.addText(l.sub, { x: 3.2, y: l.y + 0.05, w: 5.8, h: 0.6, fontSize: 11, fontFace: "Arial", color: WHITE });
});
// Arrows
[1.95, 2.85, 3.75].forEach(ay => {
  s4.addShape(pres.shapes.LINE, { x: 5, y: ay, w: 0, h: 0.15, line: { color: GRAY, width: 2 } });
});
s4.addText("HTTP / SSE", { x: 5.3, y: 1.95, w: 1.5, h: 0.25, fontSize: 9, fontFace: "Arial", color: GRAY });
s4.addText("SQL / Redis / File", { x: 5.3, y: 3.75, w: 2, h: 0.25, fontSize: 9, fontFace: "Arial", color: GRAY });

// ========== Slide 5: 功能模块 ==========
let s5 = pres.addSlide();
s5.background = { color: WHITE };
s5.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s5.addText("功能模块详解", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 28, fontFace: "Arial Black", color: WHITE, bold: true });

const modules = [
  ["用户认证", "注册 / 登录 / JWT\nToken 刷新 / bcrypt"],
  ["模型配置", "多提供商支持\nAPI Key 加密存储"],
  ["对话管理", "SSE 流式输出\n上下文管理 / 历史记录"],
  ["文件管理", "PDF/DOCX/XLSX/TXT/MD\n自动解析 + RAG"],
  ["Agent 管理", "CRUD / System Prompt\n角色绑定 / 工具选择"],
  ["响应式 UI", "移动端适配\n动画效果 / 交互优化"],
];
modules.forEach((m, i) => {
  const row = Math.floor(i / 3);
  const col = i % 3;
  const x = 0.5 + col * 3.2;
  const y = 1.3 + row * 2.0;
  s5.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.8, h: 1.7, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
  s5.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h: 1.7, fill: { color: SECONDARY } });
  s5.addText(m[0], { x: x + 0.2, y: y + 0.15, w: 2.4, h: 0.4, fontSize: 14, fontFace: "Arial", color: PRIMARY, bold: true });
  s5.addText(m[1], { x: x + 0.2, y: y + 0.6, w: 2.4, h: 0.9, fontSize: 11, fontFace: "Arial", color: GRAY });
});

// ========== Slide 6: Bug修复 ==========
let s6 = pres.addSlide();
s6.background = { color: WHITE };
s6.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s6.addText("开发时间线与关键Bug修复", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 26, fontFace: "Arial Black", color: WHITE, bold: true });

const bugs = [
  ["Bug #1", "Authorization 拼写错误", "前端 api.ts 拼写为 Authoriation\n→ 修正为 Authorization", RED],
  ["Bug #2", "FormData Content-Type 问题", "手动设置 Content-Type 导致 boundary 丢失\n→ FormData 不手动设置 Content-Type", RED],
  ["Bug #3", "Agent model_id 空字符串", "未选模型时传空字符串致 500\n→ 空字符串转为 None", AMBER],
  ["Bug #4", "文件内容未随消息发送", "file_ids 类型不匹配 + user_id 过滤错误\n→ 修正类型和过滤条件", RED],
  ["Bug #5", "getMe 时序问题", "登录后调用 getMe 时序不对\n→ 登录接口直接返回 user 信息", AMBER],
];
bugs.forEach((b, i) => {
  const y = 1.15 + i * 0.85;
  s6.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 9, h: 0.7, fill: { color: i % 2 === 0 ? GRAY_LIGHT : WHITE } });
  s6.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 0.06, h: 0.7, fill: { color: b[3] } });
  s6.addText(b[0], { x: 0.7, y: y + 0.05, w: 0.8, h: 0.3, fontSize: 11, fontFace: "Arial", color: b[3], bold: true });
  s6.addText(b[1], { x: 1.6, y: y + 0.05, w: 2.8, h: 0.3, fontSize: 11, fontFace: "Arial", color: DARK, bold: true });
  s6.addText(b[2], { x: 4.5, y: y + 0.05, w: 5, h: 0.6, fontSize: 10, fontFace: "Arial", color: GRAY });
});

// ========== Slide 7: 单元测试体系 (NEW) ==========
let s7 = pres.addSlide();
s7.background = { color: WHITE };
s7.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s7.addText("05  单元测试体系", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 28, fontFace: "Arial Black", color: WHITE, bold: true });

// Test framework
s7.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.2, w: 4.3, h: 1.8, fill: { color: LIGHT }, shadow: makeShadow(), rectRadius: 0.08 });
s7.addText("测试框架与工具", { x: 0.7, y: 1.3, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Arial", color: PRIMARY, bold: true });
s7.addText([
  { text: "pytest + pytest-asyncio", options: { bullet: true, fontSize: 11, color: DARK, breakLine: true } },
  { text: "pytest-cov（覆盖率报告）", options: { bullet: true, fontSize: 11, color: DARK, breakLine: true } },
  { text: "httpx（异步HTTP测试）", options: { bullet: true, fontSize: 11, color: DARK, breakLine: true } },
  { text: "SQLite 内存数据库（测试隔离）", options: { bullet: true, fontSize: 11, color: DARK } },
], { x: 0.7, y: 1.7, w: 3.9, h: 1.2 });

// Test structure
s7.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.2, w: 4.3, h: 1.8, fill: { color: LIGHT }, shadow: makeShadow(), rectRadius: 0.08 });
s7.addText("测试文件结构", { x: 5.4, y: 1.3, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Arial", color: PRIMARY, bold: true });
s7.addText([
  { text: "tests/", options: { fontSize: 11, color: PRIMARY, bold: true, breakLine: true } },
  { text: "  conftest.py  — 公共 fixtures", options: { fontSize: 10, color: DARK, breakLine: true } },
  { text: "  core/test_security.py  — 安全模块", options: { fontSize: 10, color: DARK, breakLine: true } },
  { text: "  api/test_auth.py  — 认证接口", options: { fontSize: 10, color: DARK, breakLine: true } },
  { text: "  api/test_config.py  — 模型配置接口", options: { fontSize: 10, color: DARK, breakLine: true } },
  { text: "  api/test_agents.py  — Agent接口", options: { fontSize: 10, color: DARK } },
], { x: 5.4, y: 1.7, w: 3.9, h: 1.2 });

// Test detail cards
const testGroups = [
  ["密码安全测试 (4项)", "密码哈希验证 ($2b$格式)\n密码验证成功/失败\n相同密码不同哈希（随机盐）", GREEN],
  ["Access Token 测试 (3项)", "Token 创建与格式验证\nToken 带过期时间创建\nToken 解码成功/失败", SECONDARY],
  ["Refresh Token 测试 (2项)", "刷新 Token 创建与验证\n刷新 Token 寿命 > Access Token", ACCENT],
  ["API 接口测试 (15+项)", "注册/登录/Token刷新\n模型配置 CRUD\nAgent CRUD\n权限验证", PRIMARY],
];
testGroups.forEach((tg, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const x = 0.5 + col * 4.7;
  const y = 3.3 + row * 1.1;
  s7.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.5, h: 0.95, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
  s7.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h: 0.95, fill: { color: tg[2] } });
  s7.addText(tg[0], { x: x + 0.2, y: y + 0.05, w: 4.1, h: 0.3, fontSize: 11, fontFace: "Arial", color: tg[2], bold: true });
  s7.addText(tg[1], { x: x + 0.2, y: y + 0.35, w: 4.1, h: 0.55, fontSize: 9, fontFace: "Arial", color: GRAY });
});

// ========== Slide 8: 测试覆盖率 (NEW) ==========
let s8 = pres.addSlide();
s8.background = { color: WHITE };
s8.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s8.addText("06  测试覆盖率报告", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 28, fontFace: "Arial Black", color: WHITE, bold: true });

// Big coverage number
s8.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.2, w: 3.5, h: 2.5, fill: { color: LIGHT }, shadow: makeShadow(), rectRadius: 0.1 });
s8.addText("58%", { x: 0.5, y: 1.3, w: 3.5, h: 1.5, fontSize: 64, fontFace: "Arial Black", color: GREEN, align: "center", bold: true });
s8.addText("当前代码覆盖率", { x: 0.5, y: 2.8, w: 3.5, h: 0.4, fontSize: 14, fontFace: "Arial", color: GRAY, align: "center" });
s8.addText("目标：80%+", { x: 0.5, y: 3.2, w: 3.5, h: 0.3, fontSize: 12, fontFace: "Arial", color: AMBER, align: "center" });

// Coverage breakdown
s8.addShape(pres.shapes.RECTANGLE, { x: 4.3, y: 1.2, w: 5.2, h: 2.5, fill: { color: WHITE }, shadow: makeShadow(), rectRadius: 0.08 });
s8.addText("覆盖率配置", { x: 4.5, y: 1.3, w: 4.8, h: 0.4, fontSize: 14, fontFace: "Arial", color: PRIMARY, bold: true });

const covItems = [
  ["报告格式", "终端 + HTML + XML", "term-missing / htmlcov / coverage.xml"],
  ["最低阈值", "55%（当前）", "pyproject.toml: --cov-fail-under=55"],
  ["测试来源", "app/ 目录", "排除 tests/、venv/"],
  ["排除行", "pragma / repr / main", "标准覆盖率排除规则"],
];
covItems.forEach((ci, i) => {
  const y = 1.8 + i * 0.45;
  s8.addText(ci[0], { x: 4.5, y, w: 1.5, h: 0.35, fontSize: 10, fontFace: "Arial", color: PRIMARY, bold: true });
  s8.addText(ci[1], { x: 6.1, y, w: 1.8, h: 0.35, fontSize: 10, fontFace: "Arial", color: DARK });
  s8.addText(ci[2], { x: 8.0, y, w: 1.5, h: 0.35, fontSize: 9, fontFace: "Arial", color: GRAY });
});

// Test output example
s8.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.0, w: 9, h: 1.3, fill: { color: "1E293B" }, shadow: makeShadow(), rectRadius: 0.06 });
s8.addText("pytest --cov=app 输出示例", { x: 0.7, y: 4.05, w: 8.6, h: 0.25, fontSize: 9, fontFace: "Consolas", color: "94A3B8" });
s8.addText([
  { text: "tests/core/test_security.py  ", options: { fontSize: 9, fontFace: "Consolas", color: "94A3B8" } },
  { text: "PASSED", options: { fontSize: 9, fontFace: "Consolas", color: GREEN, bold: true } },
  { text: " [100%]", options: { fontSize: 9, fontFace: "Consolas", color: "94A3B8" } },
], { x: 0.7, y: 4.35, w: 8.6, h: 0.25 });
s8.addText([
  { text: "---------- coverage: platform darwin ----------", options: { fontSize: 9, fontFace: "Consolas", color: "94A3B8", breakLine: true } },
  { text: "Name                     Stmts   Miss  Cover", options: { fontSize: 9, fontFace: "Consolas", color: "94A3B8", breakLine: true } },
  { text: "app/core/security.py       42      5    ", options: { fontSize: 9, fontFace: "Consolas", color: "94A3B8" } },
  { text: "88%", options: { fontSize: 9, fontFace: "Consolas", color: GREEN, bold: true } },
], { x: 0.7, y: 4.6, w: 8.6, h: 0.65 });

// ========== Slide 9: 日志系统 (NEW) ==========
let s9 = pres.addSlide();
s9.background = { color: WHITE };
s9.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s9.addText("07  日志系统设计", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 28, fontFace: "Arial Black", color: WHITE, bold: true });

// Log architecture
const logChannels = [
  ["控制台输出", "INFO 级别", "实时查看运行状态\n关键操作日志输出", SECONDARY],
  ["文件输出", "DEBUG 级别", "按日期命名文件\nlogs/app_YYYYMMDD.log", PRIMARY],
  ["第三方库", "WARNING 级别", "uvicorn.access\nhttpx 静默处理", GRAY],
];
logChannels.forEach((lc, i) => {
  const x = 0.5 + i * 3.2;
  s9.addShape(pres.shapes.RECTANGLE, { x, y: 1.2, w: 3.0, h: 1.7, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
  s9.addShape(pres.shapes.RECTANGLE, { x, y: 1.2, w: 3.0, h: 0.06, fill: { color: lc[3] } });
  s9.addText(lc[0], { x: x + 0.15, y: 1.35, w: 2.7, h: 0.35, fontSize: 14, fontFace: "Arial", color: lc[3], bold: true });
  s9.addText(lc[1], { x: x + 0.15, y: 1.7, w: 2.7, h: 0.3, fontSize: 12, fontFace: "Arial", color: DARK });
  s9.addText(lc[2], { x: x + 0.15, y: 2.0, w: 2.7, h: 0.7, fontSize: 10, fontFace: "Arial", color: GRAY });
});

// Log format example
s9.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.2, w: 9, h: 0.5, fill: { color: LIGHT }, shadow: makeShadow(), rectRadius: 0.06 });
s9.addText("日志格式", { x: 0.7, y: 3.25, w: 2, h: 0.4, fontSize: 12, fontFace: "Arial", color: PRIMARY, bold: true });
s9.addText("2026-06-15 11:30:00 - app.services.chat_service - INFO - [ChatService] 加载文件: report.pdf", { x: 2.7, y: 3.25, w: 6.5, h: 0.4, fontSize: 10, fontFace: "Consolas", color: GRAY });

// Log functions
s9.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.9, w: 4.3, h: 1.4, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
s9.addText("日志辅助函数", { x: 0.7, y: 3.95, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Arial", color: PRIMARY, bold: true });
s9.addText([
  { text: "log_request(request, status)", options: { bullet: true, fontSize: 10, fontFace: "Consolas", color: DARK, breakLine: true } },
  { text: "log_error(error_msg, exc_info)", options: { bullet: true, fontSize: 10, fontFace: "Consolas", color: RED, breakLine: true } },
  { text: "log_debug(debug_msg)", options: { bullet: true, fontSize: 10, fontFace: "Consolas", color: GRAY, breakLine: true } },
  { text: "log_warning(warning_msg)", options: { bullet: true, fontSize: 10, fontFace: "Consolas", color: AMBER } },
], { x: 0.7, y: 4.3, w: 3.9, h: 0.9 });

// Business log examples
s9.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 3.9, w: 4.3, h: 1.4, fill: { color: "1E293B" }, shadow: makeShadow(), rectRadius: 0.06 });
s9.addText("业务日志示例", { x: 5.4, y: 3.95, w: 3.9, h: 0.3, fontSize: 11, fontFace: "Arial", color: "94A3B8", bold: true });
s9.addText([
  { text: "[Chat] Agent: 代码助手, prompt: 你是...", options: { fontSize: 9, fontFace: "Consolas", color: GREEN, breakLine: true } },
  { text: "[ChatService] 检测到 2 个文件", options: { fontSize: 9, fontFace: "Consolas", color: "38BDF8", breakLine: true } },
  { text: "[FileAPI] 文件上传成功: report.pdf", options: { fontSize: 9, fontFace: "Consolas", color: "FCD34D", breakLine: true } },
  { text: "[ChatService] 文件内容: 3200 字符", options: { fontSize: 9, fontFace: "Consolas", color: "94A3B8" } },
], { x: 5.4, y: 4.3, w: 3.9, h: 0.9 });

// ========== Slide 10: 部署架构 ==========
let s10 = pres.addSlide();
s10.background = { color: WHITE };
s10.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s10.addText("08  部署架构", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 28, fontFace: "Arial Black", color: WHITE, bold: true });

// Docker services
const services = [
  ["Frontend", "Nginx Alpine", ":80", "静态文件服务\nSSE 代理", "0EA5E9"],
  ["Backend", "FastAPI + Uvicorn", ":8000", "API 服务\n健康检查", SECONDARY],
  ["Redis", "Redis 7 Alpine", ":6379", "缓存 / 会话\n异步任务队列", RED],
];
services.forEach((sv, i) => {
  const x = 0.5 + i * 3.2;
  s10.addShape(pres.shapes.RECTANGLE, { x, y: 1.2, w: 3.0, h: 2.0, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
  s10.addShape(pres.shapes.RECTANGLE, { x, y: 1.2, w: 3.0, h: 0.5, fill: { color: sv[4] } });
  s10.addText(sv[0], { x: x + 0.15, y: 1.25, w: 2.7, h: 0.4, fontSize: 16, fontFace: "Arial", color: WHITE, bold: true });
  s10.addText(sv[1], { x: x + 0.15, y: 1.8, w: 2.7, h: 0.3, fontSize: 11, fontFace: "Arial", color: DARK });
  s10.addText(sv[2], { x: x + 0.15, y: 2.1, w: 2.7, h: 0.3, fontSize: 12, fontFace: "Arial", color: sv[4], bold: true });
  s10.addText(sv[3], { x: x + 0.15, y: 2.4, w: 2.7, h: 0.7, fontSize: 10, fontFace: "Arial", color: GRAY });
});

// ECS info
s10.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.5, w: 9, h: 1.8, fill: { color: LIGHT }, shadow: makeShadow(), rectRadius: 0.08 });
s10.addText("ECS 部署信息", { x: 0.7, y: 3.6, w: 3, h: 0.35, fontSize: 14, fontFace: "Arial", color: PRIMARY, bold: true });
s10.addText([
  { text: "服务器：8.137.103.202 (腾讯云 ECS)", options: { bullet: true, fontSize: 11, color: DARK, breakLine: true } },
  { text: "项目路径：/var/www/ai-chat", options: { bullet: true, fontSize: 11, color: DARK, breakLine: true } },
  { text: "部署方式：Docker Compose + git pull", options: { bullet: true, fontSize: 11, color: DARK, breakLine: true } },
  { text: "健康检查：GET /health → {\"status\":\"ok\",\"version\":\"1.0.0\"}", options: { bullet: true, fontSize: 11, color: DARK } },
], { x: 0.7, y: 3.95, w: 8.6, h: 1.2 });

// ========== Slide 11: 未来规划 ==========
let s11 = pres.addSlide();
s11.background = { color: WHITE };
s11.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: PRIMARY } });
s11.addText("09  未来规划", { x: 0.5, y: 0.15, w: 9, h: 0.6, fontSize: 28, fontFace: "Arial Black", color: WHITE, bold: true });

const plans = [
  ["功能增强", "更多文件格式 / RAG 检索增强\n多模态输入 / 对话分享 / 插件系统"],
  ["测试完善", "覆盖率提升至 80%+\n修复 f-string 语法错误\nE2E 测试框架"],
  ["性能优化", "消息分页加载\n文件解析速度优化\nRedis 缓存策略"],
  ["安全加固", "API 限流 / 输入验证\n敏感信息脱敏\n审计日志"],
];
plans.forEach((p, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const x = 0.5 + col * 4.8;
  const y = 1.3 + row * 2.0;
  s11.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.3, h: 1.7, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
  s11.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h: 1.7, fill: { color: SECONDARY } });
  s11.addText(p[0], { x: x + 0.2, y: y + 0.15, w: 3.9, h: 0.4, fontSize: 14, fontFace: "Arial", color: PRIMARY, bold: true });
  s11.addText(p[1], { x: x + 0.2, y: y + 0.6, w: 3.9, h: 0.9, fontSize: 11, fontFace: "Arial", color: GRAY });
});

// ========== Slide 12: Thank You ==========
let s12 = pres.addSlide();
s12.background = { color: DARK };
s12.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.08, fill: { color: SECONDARY } });
s12.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.545, w: 10, h: 0.08, fill: { color: SECONDARY } });
s12.addText("Thank You", { x: 0.8, y: 1.5, w: 8.4, h: 1.2, fontSize: 44, fontFace: "Arial Black", color: WHITE, bold: true, align: "center" });
s12.addShape(pres.shapes.LINE, { x: 3.5, y: 2.8, w: 3, h: 0, line: { color: SECONDARY, width: 3 } });
s12.addText([
  { text: "AI Chat Platform - 项目文档 v3.0", options: { fontSize: 14, color: "94A3B8", breakLine: true } },
  { text: "GitHub: github.com/wesleycheng/ai-chat", options: { fontSize: 14, color: SECONDARY, breakLine: true } },
  { text: "Live: http://8.137.103.202", options: { fontSize: 14, color: "94A3B8" } },
], { x: 1, y: 3.0, w: 8, h: 1.5, align: "center" });

// Save
pres.writeFile({ fileName: "/Users/wesleycheng/Documents/ai-chat-platform/AI_Chat_Platform_项目文档_v3.pptx" })
  .then(() => console.log("PPT created successfully!"))
  .catch(err => console.error("Error:", err));
