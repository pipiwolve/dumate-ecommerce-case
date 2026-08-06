import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const W = 1280;
const H = 720;
const COLORS = {
  ink: "#111111",
  muted: "#5D6470",
  panel: "#F1F3F5",
  rule: "#C8CDD3",
  blue: "#2E7CF6",
  blueSoft: "#DDEBFF",
  red: "#D23B3B",
  redSoft: "#FCE7E7",
  amber: "#B46A00",
  amberSoft: "#FFF1CF",
  green: "#18794E",
  greenSoft: "#DFF3E8",
  white: "#FFFFFF",
};
const FONT = "PingFang SC";

function rect(slide, name, left, top, width, height, fill, line = "none") {
  return slide.shapes.add({
    geometry: "rect",
    name,
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 },
  });
}

function textBox(slide, name, value, left, top, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    fontSize: options.fontSize ?? 18,
    bold: options.bold ?? false,
    color: options.color ?? COLORS.ink,
    typeface: options.typeface ?? FONT,
    alignment: options.alignment ?? "left",
    verticalAlignment: options.verticalAlignment ?? "top",
    autoFit: options.autoFit ?? "shrinkText",
  };
  return shape;
}

function notes(slide, sources) {
  slide.speakerNotes.textFrame.setText(
    `[Sources]\n${sources.map((source) => `- ${source}`).join("\n")}`,
  );
}

function footer(slide, snapshotId, page) {
  textBox(slide, `footer-${page}`, `ShopFlow v2.6  |  ${snapshotId}`, 42, 672, 800, 22, {
    fontSize: 13,
    color: COLORS.muted,
  });
  textBox(slide, `page-${page}`, String(page).padStart(2, "0"), 1170, 672, 68, 22, {
    fontSize: 13,
    color: COLORS.muted,
    alignment: "right",
  });
}

function slideTitle(slide, title, subtitle, snapshotId, page) {
  textBox(slide, `title-${page}`, title, 42, 34, 1196, 62, { fontSize: 38, bold: true });
  if (subtitle) {
    textBox(slide, `subtitle-${page}`, subtitle, 42, 102, 1196, 48, {
      fontSize: 19,
      color: COLORS.muted,
    });
  }
  footer(slide, snapshotId, page);
}

function addCover(presentation, audience, headline, context, sourceList) {
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.white;
  textBox(slide, "cover-kicker", "SHOPFLOW  /  DELIVERY REVIEW", 42, 40, 700, 36, {
    fontSize: 20,
    bold: true,
    color: COLORS.blue,
  });
  textBox(slide, "cover-title", headline, 42, 168, 1040, 190, {
    fontSize: 58,
    bold: true,
    verticalAlignment: "bottom",
  });
  rect(slide, "cover-rule", 42, 393, 1196, 2, COLORS.ink);
  textBox(slide, "cover-audience", audience, 42, 430, 500, 48, {
    fontSize: 26,
    bold: true,
  });
  textBox(
    slide,
    "cover-meta",
    `快照时间  ${context.project.snapshot_at}\n里程碑  ${context.project.milestone.title}\n证据快照  ${context.snapshot_id}`,
    42,
    500,
    850,
    104,
    { fontSize: 19, color: COLORS.muted },
  );
  textBox(slide, "cover-health", "有风险", 1000, 500, 238, 72, {
    fontSize: 34,
    bold: true,
    color: COLORS.red,
    alignment: "right",
  });
  notes(slide, sourceList);
}

function addHealthSlide(presentation, context, audience, page, sourceList) {
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.white;
  const title = audience === "tech" ? "版本完成 65%，但超卖缺陷仍阻塞发布" : "版本完成 65%，当前交付状态为有风险";
  const subtitle = audience === "tech"
    ? "Issue 进度是计划基线；PR、Diff 与检查结果用于验证完成度和风险。"
    : "核心能力已部分完成，团队正在处理一个影响发布的库存一致性问题。";
  slideTitle(slide, title, subtitle, context.snapshot_id, page);

  textBox(slide, "progress-number", `${context.metrics.weighted_progress}%`, 42, 222, 330, 142, {
    fontSize: 82,
    bold: true,
    color: COLORS.blue,
    verticalAlignment: "bottom",
  });
  rect(slide, "progress-base", 42, 390, 330, 18, COLORS.panel);
  rect(slide, "progress-fill", 42, 390, 330 * context.metrics.weighted_progress / 100, 18, COLORS.blue);
  textBox(slide, "progress-label", "加权里程碑进度", 42, 426, 330, 34, {
    fontSize: 18,
    color: COLORS.muted,
  });

  const stats = audience === "tech"
    ? [
        ["1", "发布阻塞项", COLORS.redSoft, COLORS.red],
        ["1", "失败检查", COLORS.amberSoft, COLORS.amber],
        ["1", "计划外改动", COLORS.panel, COLORS.ink],
      ]
    : [
        ["2", "已完成事项", COLORS.greenSoft, COLORS.green],
        ["2", "处理中事项", COLORS.blueSoft, COLORS.blue],
        ["1", "待启动风险", COLORS.amberSoft, COLORS.amber],
      ];
  stats.forEach((item, index) => {
    const left = 446 + index * 266;
    rect(slide, `stat-bg-${index}`, left, 236, 230, 220, item[2]);
    textBox(slide, `stat-value-${index}`, item[0], left + 24, 270, 182, 88, {
      fontSize: 62,
      bold: true,
      color: item[3],
      verticalAlignment: "bottom",
    });
    textBox(slide, `stat-label-${index}`, item[1], left + 24, 372, 182, 42, {
      fontSize: 22,
      bold: true,
    });
  });
  textBox(
    slide,
    "health-conclusion",
    audience === "tech"
      ? "发布门禁：BUG-102 的并发回归测试仍失败；SEC-105 未启动；PERF-104 等待 owner review。"
      : "当前不建议进入发布候选。若阻塞在下一个工作日仍未关闭，发布日期影响需由项目经理确认。",
    446,
    504,
    792,
    94,
    { fontSize: 23, bold: true },
  );
  notes(slide, sourceList);
}

function drawIssueTable(slide, issues, left, top, width, rowHeight, customer = false) {
  const columns = customer
    ? [220, 540, 170, 170]
    : [155, 470, 165, 175, 135];
  const headers = customer
    ? ["事项", "业务结果", "状态", "负责人"]
    : ["Issue", "事项", "状态", "进度", "优先级"];
  let x = left;
  headers.forEach((header, index) => {
    rect(slide, `header-bg-${index}-${top}`, x, top, columns[index], rowHeight, COLORS.ink);
    textBox(slide, `header-${index}-${top}`, header, x + 12, top + 10, columns[index] - 24, rowHeight - 16, {
      fontSize: 17,
      bold: true,
      color: COLORS.white,
      verticalAlignment: "middle",
    });
    x += columns[index];
  });
  issues.forEach((issue, row) => {
    const y = top + rowHeight * (row + 1);
    const fill = issue.status === "阻塞" ? COLORS.redSoft : row % 2 ? COLORS.white : COLORS.panel;
    const values = customer
      ? [issue.key, issue.title, issue.status, issue.assignee]
      : [issue.key, issue.title, issue.status, `${issue.progress}%`, issue.priority];
    x = left;
    values.forEach((value, col) => {
      rect(slide, `cell-bg-${row}-${col}-${top}`, x, y, columns[col], rowHeight, fill, COLORS.rule);
      textBox(slide, `cell-${row}-${col}-${top}`, String(value), x + 12, y + 9, columns[col] - 24, rowHeight - 14, {
        fontSize: 16,
        bold: col === 0 || issue.status === "阻塞",
        color: issue.status === "阻塞" && col === 2 ? COLORS.red : COLORS.ink,
        verticalAlignment: "middle",
      });
      x += columns[col];
    });
  });
}

function addIssuePortfolio(presentation, context, audience, page, sourceList) {
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.white;
  slideTitle(
    slide,
    audience === "tech" ? "六项计划中，两项完成、一项阻塞" : "已完成核心能力，但发布阻塞尚未解除",
    audience === "tech" ? "状态来自同一 GitHub Milestone 快照。" : "客户视图聚焦业务结果与责任人，不展示内部代码细节。",
    context.snapshot_id,
    page,
  );
  const issues = context.issues.filter((issue) => issue.type !== "epic");
  drawIssueTable(slide, issues, 42, 180, 1196, 62, audience === "customer");
  notes(slide, sourceList);
}

function addBugEvidence(presentation, context, page, sourceList) {
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.white;
  const pr = context.pull_requests.find((item) => item.number === 202);
  slideTitle(
    slide,
    "首次修复只锁写入，仍未关闭并发竞态",
    `BUG-102 / PR #${pr.github_number ?? pr.number} / changes requested`,
    context.snapshot_id,
    page,
  );
  rect(slide, "bug-left", 42, 180, 706, 420, COLORS.panel);
  textBox(slide, "bug-code-title", "失败证据", 72, 210, 220, 42, { fontSize: 24, bold: true });
  textBox(
    slide,
    "bug-code",
    `分支    ${pr.diff.head_ref}\nSHA     ${pr.diff.head_sha.slice(0, 10)}\n模块    ${pr.diff.modules.join(" / ")}\nDiff    +${pr.diff.insertions} / -${pr.diff.deletions}\n检查    bug-102-regression: failure\n断言    expected available=0\n        actual available=-1`,
    72,
    276,
    640,
    260,
    { fontSize: 20, typeface: "Menlo", color: COLORS.ink },
  );
  rect(slide, "bug-risk", 788, 180, 450, 182, COLORS.redSoft);
  textBox(slide, "bug-risk-title", "风险判断", 818, 210, 390, 38, { fontSize: 24, bold: true, color: COLORS.red });
  textBox(slide, "bug-risk-body", "余量校验仍在锁外，两个请求可以读取同一份库存。当前修改不能通过发布门禁。", 818, 266, 390, 70, {
    fontSize: 19,
    bold: true,
  });
  textBox(slide, "bug-action-title", "下一步", 788, 404, 220, 36, { fontSize: 24, bold: true });
  textBox(slide, "bug-action-body", "1. 将校验与写入纳入同一原子边界\n2. 保留订单 ID 幂等约束\n3. 让并发回归进入发布门禁\n4. 由库存一致性专家复核方案", 788, 460, 450, 132, {
    fontSize: 20,
  });
  notes(slide, sourceList);
}

function addChangeImpact(presentation, context, page, sourceList) {
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.white;
  slideTitle(slide, "三条开发线影响库存核心链路，一条改动脱离计划", "代码变化按 PR 与 Git ref 归因。", context.snapshot_id, page);
  const rows = [
    ...context.pull_requests.filter((pr) => [202, 203, 204].includes(pr.number)).map((pr) => ({
      id: pr.github_number ? `PR #${pr.github_number}` : `Commit ${pr.diff.head_sha.slice(0, 7)}`,
      title: pr.title,
      modules: pr.diff.modules.join(" / "),
      state: pr.checks.some((check) => check.conclusion === "failure") ? "检查失败" : pr.state === "merged" ? "已合并" : "审查中",
    })),
    {
      id: "CHORE-106",
      title: context.findings[0].title,
      modules: context.findings[0].diff.modules.join(" / "),
      state: "待确认",
    },
  ];
  const columns = [170, 470, 360, 196];
  const headers = ["变更", "目的", "影响模块", "结论"];
  let x = 42;
  headers.forEach((header, col) => {
    rect(slide, `impact-head-bg-${col}`, x, 180, columns[col], 58, COLORS.ink);
    textBox(slide, `impact-head-${col}`, header, x + 12, 192, columns[col] - 24, 36, { fontSize: 17, bold: true, color: COLORS.white });
    x += columns[col];
  });
  rows.forEach((row, index) => {
    const y = 238 + index * 82;
    const values = [row.id, row.title, row.modules, row.state];
    x = 42;
    values.forEach((value, col) => {
      const risk = row.state === "检查失败" || row.state === "待确认";
      rect(slide, `impact-bg-${index}-${col}`, x, y, columns[col], 82, risk ? COLORS.amberSoft : index % 2 ? COLORS.white : COLORS.panel, COLORS.rule);
      textBox(slide, `impact-${index}-${col}`, value, x + 12, y + 12, columns[col] - 24, 56, {
        fontSize: 16,
        bold: col === 0 || col === 3,
        color: row.state === "检查失败" && col === 3 ? COLORS.red : COLORS.ink,
        verticalAlignment: "middle",
      });
      x += columns[col];
    });
  });
  notes(slide, sourceList);
}

function addKnowledgeExpert(presentation, context, page, sourceList) {
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.white;
  slideTitle(slide, "规范解释为什么失败，专家负责当前例外处理", "知识与人员来自不同的受控数据源。", context.snapshot_id, page);
  rect(slide, "knowledge-band", 42, 188, 562, 360, COLORS.blueSoft);
  textBox(slide, "knowledge-label", "知识证据", 72, 218, 220, 36, { fontSize: 24, bold: true, color: COLORS.blue });
  textBox(slide, "knowledge-title", context.enrichment.primary_knowledge.title, 72, 280, 490, 62, { fontSize: 28, bold: true });
  textBox(slide, "knowledge-claim", "“余量校验与预占写入必须处于同一原子边界；只锁写入仍属于 check-then-act 竞态。”", 72, 372, 490, 112, {
    fontSize: 21,
  });
  textBox(slide, "knowledge-source", context.enrichment.primary_knowledge.source_url, 72, 508, 490, 24, { fontSize: 13, color: COLORS.muted });

  const expert = context.enrichment.primary_expert;
  rect(slide, "expert-band", 650, 188, 588, 360, COLORS.panel);
  textBox(slide, "expert-label", "推荐专家", 680, 218, 220, 36, { fontSize: 24, bold: true });
  textBox(slide, "expert-name", `${expert.name}  /  ${expert.title}`, 680, 280, 520, 58, { fontSize: 30, bold: true });
  textBox(slide, "expert-reason", `${expert.match_reason}\n状态：${expert.availability}\n升级条件：${expert.escalate_when}`, 680, 372, 520, 118, { fontSize: 19 });
  textBox(slide, "expert-contact", expert.contact, 680, 508, 520, 24, { fontSize: 14, color: COLORS.muted });
  textBox(slide, "knowledge-action", "建议动作：技术负责人在下一轮修复提交前完成方案评审，并将并发回归测试设为合并必需检查。", 42, 584, 1196, 54, { fontSize: 22, bold: true });
  notes(slide, sourceList);
}

function addNextActions(presentation, context, audience, page, sourceList) {
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.white;
  const title = audience === "tech" ? "先解除 P0 阻塞，再收敛性能与权限风险" : "团队按三步恢复计划推进，发布日期影响待确认";
  slideTitle(slide, title, "本期快照后的建议动作，不改变已冻结证据。", context.snapshot_id, page);
  rect(slide, "timeline", 72, 356, 1100, 2, COLORS.ink);
  const actions = audience === "tech"
    ? [
        ["今天 20:00", "原子性方案评审", "陈晨 + 王海"],
        ["明天 12:00", "并发回归与 owner review", "QA + 模块负责人"],
        ["明天 18:00", "发布门禁复核", "赵磊"],
      ]
    : [
        ["当前", "专家复核库存修复方案", "技术负责人"],
        ["下一检查点", "完成并发回归与安全评估", "研发团队"],
        ["结果确认", "更新发布日期与客户影响", "项目经理"],
      ];
  actions.forEach((action, index) => {
    const left = 72 + index * 388;
    rect(slide, `timeline-dot-${index}`, left, 345, 24, 24, index === 0 ? COLORS.red : COLORS.blue);
    textBox(slide, `timeline-time-${index}`, action[0], left, 274, 300, 36, { fontSize: 18, bold: true, color: COLORS.muted });
    textBox(slide, `timeline-title-${index}`, action[1], left, 404, 330, 68, { fontSize: 25, bold: true });
    textBox(slide, `timeline-owner-${index}`, action[2], left, 496, 330, 36, { fontSize: 18, color: COLORS.muted });
  });
  rect(slide, "decision-band", 72, 576, 1100, 58, audience === "tech" ? COLORS.panel : COLORS.amberSoft);
  textBox(
    slide,
    "decision-text",
    audience === "tech"
      ? "技术负责人决策：是否冻结非阻塞变更，并指定 BUG-102 第二次修复的合并门禁。"
      : "客户项目经理决策：维持 8 月 15 日目标；若下一检查点未通过，再确认是否调整发布日期。",
    94,
    591,
    1056,
    34,
    { fontSize: 20, bold: true },
  );
  notes(slide, sourceList);
}

async function saveDeck(presentation, target) {
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(target);
}

async function main() {
  const [contextPath, outputDir] = process.argv.slice(2);
  if (!contextPath || !outputDir) {
    throw new Error("usage: report_builder.mjs <context.json> <output-dir>");
  }
  const context = JSON.parse(await fs.readFile(contextPath, "utf-8"));
  await fs.mkdir(outputDir, { recursive: true });

  const githubSource = context.sources.find((item) => item.type === "github").uri;
  const gitSource = context.sources.find((item) => item.type === "git").uri;
  const techSources = [githubSource, gitSource, context.enrichment.primary_knowledge.source_url, context.enrichment.incident_knowledge.source_url];
  const customerSources = [githubSource, gitSource, context.enrichment.release_policy.source_url];

  const tech = Presentation.create({ slideSize: { width: W, height: H } });
  addCover(tech, "技术负责人版", "限时促销版本\n交付风险审查", context, techSources);
  addHealthSlide(tech, context, "tech", 2, techSources);
  addIssuePortfolio(tech, context, "tech", 3, [githubSource]);
  addBugEvidence(tech, context, 4, [githubSource, gitSource, context.enrichment.primary_knowledge.source_url]);
  addChangeImpact(tech, context, 5, [githubSource, gitSource]);
  addKnowledgeExpert(tech, context, 6, [context.enrichment.primary_knowledge.source_url, context.enrichment.incident_knowledge.source_url, context.enrichment.primary_expert.source_url]);
  addNextActions(tech, context, "tech", 7, [githubSource, context.enrichment.release_policy.source_url]);

  const customer = Presentation.create({ slideSize: { width: W, height: H } });
  addCover(customer, "客户项目经理版", "ShopFlow v2.6\n项目进展更新", context, customerSources);
  addHealthSlide(customer, context, "customer", 2, customerSources);
  addIssuePortfolio(customer, context, "customer", 3, [githubSource]);
  addNextActions(customer, context, "customer", 4, customerSources);

  await saveDeck(tech, path.join(outputDir, "ShopFlow-v2.6-技术负责人版.pptx"));
  await saveDeck(customer, path.join(outputDir, "ShopFlow-v2.6-客户项目经理版.pptx"));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
