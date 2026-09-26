import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  Bell,
  Blocks,
  ChevronRight,
  ChevronsLeft,
  House,
  ListTodo,
  LogOut,
  Menu,
  Package,
  Settings,
  X,
  LoaderCircle,
} from "lucide-react";
import { useAuth } from "@/api/auth";
import { useWorkspace } from "@/api/workspace";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
import { navigate } from "@/lib/router.js";
import { readPreference, writePreference } from "@/lib/storage.js";
import { Brand, BrandMark, LangToggle, ThemeToggle } from "./Brand.jsx";
import { Button, Chip, Notice, Toast } from "./ui";
const groups = [
  {
    key: "navGroupWork",
    items: [
      { path: "/app", key: "overview", Icon: House },
      { path: "/app/issues", key: "issues", Icon: ListTodo },
      { path: "/app/listings", key: "products", Icon: Package },
      { path: "/app/sources", key: "sources", Icon: Blocks },
      { path: "/app/alerts", key: "alerts", Icon: Bell },
    ],
  },
  {
    key: "navGroupSetup",
    items: [{ path: "/app/settings", key: "settings", Icon: Settings }],
  },
];
const navigation = groups.flatMap((group) => group.items);
const stages: Record<string, string> = {
  queued: "jobQueued",
  analysing: "jobAnalysing",
  syncing: "jobSyncing",
  clearing: "jobClearing",
  seeding: "jobSeeding",
  importing: "jobImporting",
  drafting: "jobDrafting",
};
function isCurrent(href: string, path: string) {
  return href === "/app" ? path === href : path.startsWith(href);
}
export function WorkspaceShell({
  path,
  children,
}: {
  path: string;
  children: ReactNode;
}) {
  const { user, logout } = useAuth();
  const { t, localizeError } = useI18n();
  const workspace = useWorkspace();
  const [open, setOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(
    () => readPreference("deciqo-sidebar", "open") === "collapsed",
  );
  const [signingOut, setSigningOut] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const drawer = useRef<HTMLElement>(null);
  const menu = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (!open) return;
    const before = document.activeElement as HTMLElement | null;
    drawer.current?.querySelector<HTMLElement>("button,a")?.focus();
    return () => before?.focus();
  }, [open]);
  useEffect(() => {
    const media = matchMedia("(min-width:900px)");
    const close = () => {
      if (media.matches) setOpen(false);
    };
    media.addEventListener("change", close);
    return () => media.removeEventListener("change", close);
  }, []);
  function toggleCollapsed() {
    setCollapsed((value) => {
      writePreference("deciqo-sidebar", value ? "open" : "collapsed");
      return !value;
    });
  }
  function trap(event: React.KeyboardEvent) {
    if (!open) return;
    if (event.key === "Escape") {
      setOpen(false);
      return;
    }
    if (event.key !== "Tab") return;
    const elements = drawer.current?.querySelectorAll<HTMLElement>(
      "a[href],button:not([disabled])",
    );
    if (!elements?.length) return;
    const first = elements[0];
    const last = elements[elements.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
  const job = workspace.job;
  const running = job && ["queued", "running"].includes(job.status);
  const failed =
    job && ["failed", "interrupted", "contact_lost"].includes(job.status);
  const current = navigation.find((item) => isCurrent(item.path, path));
  const openCount = workspace.summary?.findings_open;
  const initials = (user?.name || user?.email || "?")
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
  const progress =
    job?.detail.index != null && job.detail.total
      ? Math.min(100, (job.detail.index / job.detail.total) * 100)
      : null;
  return (
    <div className={cn("workspace-shell", collapsed && "is-collapsed")}>
      <header className="mobile-header">
        <Brand />
        <button
          ref={menu}
          className="btn btn--outline btn--sm"
          aria-expanded={open}
          aria-controls="workspace-sidebar"
          onClick={() => setOpen(true)}
        >
          <Menu size={18} aria-hidden />
          {t("workspace.menu")}
        </button>
      </header>
      {open && (
        <button
          className="drawer-scrim"
          aria-label={t("workspace.closeMenu")}
          tabIndex={-1}
          onClick={() => setOpen(false)}
        />
      )}
      <aside
        id="workspace-sidebar"
        ref={drawer}
        className={"workspace-sidebar" + (open ? " is-open" : "")}
        role={open ? "dialog" : undefined}
        aria-modal={open ? true : undefined}
        aria-label={t("workspace.navigation")}
        onKeyDown={trap}
      >
        <div className="sidebar-brand">
          <Brand />
          <a className="sidebar-mark" href="#/" aria-label={"Deciqo · " + t("common.home")}>
            <BrandMark size={30} />
          </a>
          <Button
            className="drawer-close"
            variant="text"
            aria-label={t("workspace.closeMenu")}
            onClick={() => setOpen(false)}
          >
            <X size={18} aria-hidden />
          </Button>
        </div>
        <nav aria-label={t("workspace.navigation")}>
          {groups.map((group) => (
            <div key={group.key} className="nav-group">
              <p className="nav-group__label">{t("workspace." + group.key)}</p>
              {group.items.map(({ path: href, key, Icon }) => (
                <a
                  key={href}
                  href={"#" + href}
                  className="nav-item"
                  data-tip={t("common." + key)}
                  aria-current={isCurrent(href, path) ? "page" : undefined}
                  onClick={() => setOpen(false)}
                >
                  <span className="nav-item__icon">
                    <Icon size={18} aria-hidden />
                    {key === "issues" && !!openCount && <i className="nav-dot" aria-hidden />}
                  </span>
                  <span className="nav-item__label">{t("common." + key)}</span>
                  {key === "issues" && workspace.summary && (
                    <span
                      className="nav-count"
                      aria-label={t("workspace.openIssueCount", {
                        count: workspace.summary.findings_open,
                      })}
                    >
                      {workspace.summary.findings_open}
                    </span>
                  )}
                </a>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="account">
            <span className="account__avatar" aria-hidden>
              {initials}
            </span>
            <div className="account__text">
              <strong>{user?.name}</strong>
              <span className="muted">{user?.email}</span>
              {user?.is_demo && <Chip tone="info">{t("workspace.demoAccount")}</Chip>}
            </div>
            <Button
              variant="text"
              className="account__out"
              busy={signingOut}
              aria-label={t("common.signOut")}
              title={t("common.signOut")}
              onClick={async () => {
                setSigningOut(true);
                try {
                  await logout();
                  navigate("/login");
                } catch (e) {
                  setError((e as { code?: string }).code ?? "request_failed");
                } finally {
                  setSigningOut(false);
                }
              }}
            >
              {!signingOut && <LogOut size={16} aria-hidden />}
            </Button>
          </div>
          <div className="sidebar-preferences">
            <LangToggle />
            <ThemeToggle />
          </div>
          <button
            type="button"
            className="sidebar-toggle"
            aria-pressed={collapsed}
            onClick={toggleCollapsed}
          >
            <ChevronsLeft size={18} aria-hidden />
            <span>{t(collapsed ? "workspace.sidebarExpand" : "workspace.sidebarCollapse")}</span>
          </button>
        </div>
      </aside>
      <div className="workspace-column" {...(open ? { inert: "" } : {})}>
        <div className="workspace-topbar">
          <p className="crumbs">
            <a href="#/app">Deciqo</a>
            <ChevronRight size={14} aria-hidden />
            <span aria-current="page">{t("common." + (current?.key ?? "products"))}</span>
          </p>
          <div className="workspace-topbar__tools">
            {running && (
              <span className="job-pill" aria-hidden>
                <span className="pulse-dot" />
                {t(workspace.jobLabel)}
              </span>
            )}
            {openCount != null && openCount > 0 && (
              <a className="topbar-issues" href="#/app/issues">
                <ListTodo size={16} aria-hidden />
                <span className="count">{openCount}</span>
                <span className="visually-hidden">
                  {t("workspace.openIssueCount", { count: openCount })}
                </span>
              </a>
            )}
            <LangToggle />
            <ThemeToggle />
          </div>
        </div>
        <main className="workspace-main stack">
          {job && (
            <Notice
              tone={failed ? "warn" : running ? "info" : "good"}
              className="job-notice"
              action={
                !running ? (
                  <Button variant="text" onClick={workspace.closeJob}>
                    {t("common.close")}
                  </Button>
                ) : undefined
              }
            >
              <div className="job-bar" aria-live="polite">
                {running && (
                  <LoaderCircle size={18} className="spinner" aria-hidden />
                )}
                <strong>
                  {failed
                    ? t(
                        job.status === "interrupted"
                          ? "workspace.jobInterrupted"
                          : job.status === "contact_lost"
                            ? "workspace.jobLost"
                            : "workspace.jobFailed",
                      )
                    : running
                      ? t(workspace.jobLabel)
                      : t("workspace.jobDone")}
                </strong>
                {job.detail.index != null && job.detail.total != null && (
                  <span className="count">
                    {t("workspace.jobProgress", {
                      index: job.detail.index,
                      total: job.detail.total,
                    })}
                  </span>
                )}
                {running && (
                  <span>
                    {t(
                      "workspace." +
                        (stages[job.detail.stage ?? ""] ?? "jobProcessing"),
                    )}
                  </span>
                )}
              </div>
              {running && (
                <div className={cn("job-progress", progress == null && "is-indeterminate")} aria-hidden>
                  <span style={progress == null ? undefined : { width: progress + "%" }} />
                </div>
              )}
            </Notice>
          )}
          {error && <Notice tone="alert">{localizeError(error)}</Notice>}
          <div key={path} className="stack page-enter">
            {children}
          </div>
        </main>
      </div>
      {workspace.toast && (
        <Toast onClose={workspace.closeToast}>{workspace.toast}</Toast>
      )}
    </div>
  );
}
