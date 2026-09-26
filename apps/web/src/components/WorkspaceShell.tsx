import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  Bell,
  Blocks,
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
import { useI18n } from "@/lib/i18n";
import { navigate } from "@/lib/router.js";
import { Brand, LangToggle, ThemeToggle } from "./Brand.jsx";
import { Button, Chip, Notice, Toast } from "./ui";
const navigation = [
  { path: "/app", key: "overview", Icon: House },
  { path: "/app/issues", key: "issues", Icon: ListTodo },
  { path: "/app/listings", key: "products", Icon: Package },
  { path: "/app/sources", key: "sources", Icon: Blocks },
  { path: "/app/alerts", key: "alerts", Icon: Bell },
  { path: "/app/settings", key: "settings", Icon: Settings },
];
const stages: Record<string, string> = {
  queued: "jobQueued",
  analysing: "jobAnalysing",
  syncing: "jobSyncing",
  clearing: "jobClearing",
  seeding: "jobSeeding",
  importing: "jobImporting",
  drafting: "jobDrafting",
};
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
  return (
    <div className="workspace-shell">
      <header className="mobile-header">
        <Brand />
        <button
          ref={menu}
          className="btn btn--outline"
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
          {navigation.map(({ path: href, key, Icon }) => (
            <a
              key={href}
              href={"#" + href}
              className="nav-item"
              aria-current={
                (href === "/app" ? path === href : path.startsWith(href))
                  ? "page"
                  : undefined
              }
              onClick={() => setOpen(false)}
            >
              <Icon size={18} aria-hidden />
              {t("common." + key)}
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
        </nav>
        <div className="sidebar-footer">
          <div className="account">
            <strong>{user?.name}</strong>
            <span className="muted">{user?.email}</span>
            {user?.is_demo && <Chip>{t("workspace.demoAccount")}</Chip>}
          </div>
          <Button
            variant="text"
            busy={signingOut}
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
            <LogOut size={16} aria-hidden />
            {t("common.signOut")}
          </Button>
          <div className="sidebar-preferences">
            <LangToggle />
            <ThemeToggle />
          </div>
        </div>
      </aside>
      <main className="workspace-main stack" {...(open ? { inert: "" } : {})}>
        {job && (
          <Notice
            tone={failed ? "warn" : running ? "info" : "good"}
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
          </Notice>
        )}
        {error && <Notice tone="alert">{localizeError(error)}</Notice>}
        {children}
      </main>
      {workspace.toast && (
        <Toast onClose={workspace.closeToast}>{workspace.toast}</Toast>
      )}
    </div>
  );
}
