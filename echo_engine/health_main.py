from typing import List
from .health import load_config, run_health, save_json
from .health.registry import MetricRegistry
from .health.phase1 import complexity_analyzer as cpx
from .health.phase1 import debt_manager as debt
from .health.phase1 import style_enforcer as style
from .health.phase1 import size_import_analyzer as szimp


def build_registry(cfg: dict, focus: List[str], auto_issue: bool = False) -> tuple:
    w = cfg["weights"]
    opt = cfg.get("options", {})
    reg = MetricRegistry()
    root = opt.get("repo_root", ".")
    include = []

    # Phase 1 - with new config support
    size_cfg = opt.get("size", {})
    imp_cfg = opt.get("import", {})

    if not focus or "size" in focus or "basic" in focus:
        szimp.register_size(reg, root, w["size"], size_cfg)
        include.append("size")

    if not focus or "import" in focus or "basic" in focus:
        prefixes = imp_cfg.get("internal_prefixes", ["echo_engine", "echo", "app", "src"])
        szimp.register_import(reg, root, w["import"], prefixes)
        include.append("import")

    if not focus or "complexity" in focus or "basic" in focus:
        cpx.register(reg, root, w["complexity"])
        include.append("complexity")
    if not focus or "debt" in focus or "basic" in focus:
        debt.register(reg, root, w["debt"], auto_issue)
        include.append("debt")
    if not focus or "style" in focus or "basic" in focus:
        style.register(reg, cfg, w["style"])
        include.append("style")

    # Phase 2 & 3 would be added here in future versions

    return reg, include, w


def run(focus: List[str], auto_issue: bool, out_json: str):
    cfg = load_config("echo_engine/health/config.yaml")
    reg, include, weights = build_registry(cfg, focus, auto_issue)
    report = run_health(reg, include, weights)
    print(report["table"])
    print(f"\n🎯 Total Health Score: {report['total']}/100")

    # 점수별 메시지
    score = report["total"]
    if score >= 80:
        print("🟢 EXCELLENT: Architecture-level quality achieved!")
    elif score >= 70:
        print("🟡 ADVANCED: Production-ready with advanced practices!")
    elif score >= 50:
        print("🔵 GOOD: Basic quality standards met!")
    elif score >= 45:
        print("🟠 IMPROVING: Almost ready for production!")
    else:
        print("🔴 NEEDS WORK: Focus on basic improvements needed!")

    if out_json:
        save_json(report, out_json)
        print(f"📄 Report saved: {out_json}")
